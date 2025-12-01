from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.redis import create_redis_pool
from app.api.v1.api import api_router
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException, status
from datetime import datetime

# Middleware to limit request body size
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Limit request body to 10MB
        max_size = 10 * 1024 * 1024  # 10 MB
        content_length = request.headers.get('content-length')
        
        if content_length and int(content_length) > max_size:
            return JSONResponse(
                status_code=413,
                content={
                    "success": False,
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "Request body too large",
                        "details": {}
                    }
                }
            )
        
        return await call_next(request)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="scraPy - Intelligent Web Scraping API with AI-powered extraction",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Add request size limit middleware
app.add_middleware(RequestSizeLimitMiddleware)

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.errors import ScrapyBaseException

@app.exception_handler(ScrapyBaseException)
async def scrapy_exception_handler(request: Request, exc: ScrapyBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "details": {}
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "details": {"errors": exc.errors()}
            }
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the exception for internal debugging
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # In production, don't expose internal error details
    error_details = {}
    if settings.PROJECT_NAME == "scraPy API":  # Only show details in dev
        # Check if not in production by looking at frontend URL
        if "localhost" in settings.FRONTEND_URL:
            error_details = {"error": str(exc)}
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": error_details
            }
        }
    )

from app.core.database import engine, Base
from app.models import job
from app.models.api_key import ApiKey
from app.models.webhook import Webhook
from app.core.logging import logger

@app.on_event("startup")
async def startup_event():
    logger.info("Starting scraPy API server...")
    app.state.redis = await create_redis_pool()
    logger.info("Redis connection established")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
    logger.info("scraPy API server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down scraPy API server...")
    await app.state.redis.close()
    logger.info("scraPy API server shut down complete")

# Set all CORS enabled origins - supports both local dev and production
# In production, set FRONTEND_URL to your Vercel domain
allowed_origins = [settings.FRONTEND_URL]

# Also allow Vercel preview deployments (optional, for testing)
if settings.FRONTEND_URL != "http://localhost:3000":
    allowed_origins.append("http://localhost:3000")  # Still allow local dev

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to scraPy API"}

@app.get(
    "/health",
    summary="Health check",
    description="Check the health status of the API server, database, and Redis connections",
    response_description="Health status of all services"
)
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Checks:
    - API server status
    - PostgreSQL database connectivity
    - Redis connectivity
    
    Returns status of each component and overall health.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "healthy",
            "database": "unknown",
            "redis": "unknown"
        }
    }
    
    # Check database
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
        logger.debug("Database health check: OK")
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        if hasattr(app.state, "redis"):
            await app.state.redis.ping()
            health_status["services"]["redis"] = "healthy"
            logger.debug("Redis health check: OK")
        else:
            health_status["services"]["redis"] = "not_initialized"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Redis health check failed: {e}")
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)

from app.api.v1.api import api_router

app.include_router(api_router, prefix=settings.API_V1_STR)
