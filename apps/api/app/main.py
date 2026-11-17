from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from apps.api.app.core.config import settings
from apps.api.app.api.v1 import api_v1_router
from apps.api.app.storage import get_storage_driver

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade document processing, PDF tools, and conversion engine API.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    # Initialize storage driver and verify directory permissions
    storage = get_storage_driver()
    if hasattr(storage, "base_dir"):
        storage.base_dir.mkdir(parents=True, exist_ok=True)

@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

@app.head("/")
async def root_head():
    return Response(status_code=200)

@app.get("/")
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs",
        "api_v1": settings.API_V1_STR,
    }
