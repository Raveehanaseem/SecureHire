"""
Main API Router v1
"""

from fastapi import APIRouter
from api.v1.auth_router import router as auth_router
from api.v1.jobs_router import router as jobs_router
from api.v1.applications_router import router as applications_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(jobs_router)
api_router.include_router(applications_router)
