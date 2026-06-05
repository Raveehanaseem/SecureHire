"""
Prometheus Metrics
- HTTP request counters and latency histograms
- Security event counters (failed logins, anomalies)
- Kafka event counters
CYC386 Requirement: Prometheus observability
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response

router = APIRouter(tags=["Monitoring"])

# ── Metrics ───────────────────────────────────────────────────────────────────
http_requests_total = Counter(
    "securehire_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration = Histogram(
    "securehire_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

failed_logins_total = Counter(
    "securehire_failed_logins_total",
    "Total failed login attempts",
    ["ip"],
)

anomaly_alerts_total = Counter(
    "securehire_anomaly_alerts_total",
    "Total anomaly alerts triggered",
    ["alert_type"],
)

kafka_events_total = Counter(
    "securehire_kafka_events_total",
    "Total Kafka events published",
    ["topic", "event_type"],
)

active_users = Gauge(
    "securehire_active_sessions",
    "Current active Redis sessions",
)


# ── Endpoint ─────────────────────────────────────────────────────────────────
@router.get("/metrics")
async def metrics():
    """Prometheus scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
