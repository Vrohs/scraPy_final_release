from fastapi import APIRouter

api_router = APIRouter()

from app.api.v1.endpoints import scrape, stats, api_keys, webhooks
api_router.include_router(scrape.router, prefix="/scrape", tags=["scrape"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(api_keys.router, prefix="/api_keys", tags=["api_keys"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
