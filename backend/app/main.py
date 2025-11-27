from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.redis import create_redis_pool
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

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
    # In a real app, log the exception here
    print(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(exc)} # Be careful exposing this in prod
            }
        }
    )

from app.core.database import engine, Base
from app.models import job
from app.models.api_key import ApiKey
from app.models.webhook import Webhook

@app.on_event("startup")
async def startup_event():
    app.state.redis = await create_redis_pool()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()

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

from app.api.v1.api import api_router

app.include_router(api_router, prefix=settings.API_V1_STR)
