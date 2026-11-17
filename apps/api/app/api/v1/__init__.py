from fastapi import APIRouter
from apps.api.app.api.v1.health import router as health_router
from apps.api.app.api.v1.tools import router as tools_router
from apps.api.app.api.v1.files import router as files_router
from apps.api.app.api.v1.jobs import router as jobs_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router)
api_v1_router.include_router(tools_router)
api_v1_router.include_router(files_router)
api_v1_router.include_router(jobs_router)

__all__ = ["api_v1_router"]
