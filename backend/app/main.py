from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.redis import create_redis_pool
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

from app.core.database import engine, Base
from app.models import job # Import models to register them

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
