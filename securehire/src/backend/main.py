"""
SecureHire - Secure Job Recruitment Platform
Main Application Entry Point — UPDATED (All requirements integrated)
CYC386 - Secure Software Design & Development
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time

from config import settings
from middleware.security import SecurityHeadersMiddleware, SQLInjectionMiddleware, XSSMiddleware
from middleware.rate_limit import limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded
from api.v1.router import api_router
from database import init_db
from cache.redis_client import init_redis, close_redis
from kafka.producer import init_kafka_producer, close_kafka_producer
from utils.logger import setup_logging
from utils.metrics import (
    router as metrics_router,
    http_requests_total,
    http_request_duration,
    anomaly_alerts_total,
)
from utils.anomaly_detection import check_request_anomaly

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SecureHire starting up...")
    await init_db()
    await init_redis()
    await init_kafka_producer()
    try:
        from utils.vault_client import get_vault_secret
        secrets = await get_vault_secret("securehire/app")
        if secrets:
            logger.info("Vault secrets loaded")
        else:
            logger.warning("Vault not available — using .env values")
    except Exception as e:
        logger.warning(f"Vault skipped: {e}")
    logger.info("All services initialized")
    yield
    logger.info("SecureHire shutting down...")
    await close_redis()
    await close_kafka_producer()


app = FastAPI(
    title="SecureHire API",
    description="Secure Job Recruitment Platform — CYC386",
    version="2.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SQLInjectionMiddleware)
app.add_middleware(XSSMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
    expose_headers=["X-Request-ID"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    start_time = time.time()
    ip = request.client.host if request.client else "unknown"
    anomaly = await check_request_anomaly(ip)
    if anomaly["flagged"]:
        logger.warning(
            f"HIGH_RISK_REQUEST | IP: {ip} | Score: {anomaly['risk_score']} | Alert: {anomaly['alert']}"
        )
        anomaly_alerts_total.labels(alert_type="high_risk_request").inc()
    # Note: burst_attack / ip_switching / off_hours_login alerts are counted
    # directly inside utils.anomaly_detection.AnomalyDetector — no need to
    # increment them again here.

    response = await call_next(request)
    process_time = time.time() - start_time

    # Use the route template (e.g. /api/v1/jobs/{job_id}) rather than the raw path
    # so distinct IDs don't explode the metric's cardinality.
    route = request.scope.get("route")
    endpoint = route.path if route is not None else request.url.path

    http_requests_total.labels(
        method=request.method,
        endpoint=endpoint,
        status_code=str(response.status_code),
    ).inc()
    http_request_duration.labels(
        method=request.method,
        endpoint=endpoint,
    ).observe(process_time)

    response.headers["X-Process-Time"] = str(round(process_time, 4))
    response.headers["X-Risk-Score"] = str(anomaly["risk_score"])
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid input data"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


app.include_router(api_router, prefix="/api/v1")
app.include_router(metrics_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "SecureHire API", "version": "2.0.0"}
