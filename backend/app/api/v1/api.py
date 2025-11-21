from fastapi import APIRouter

api_router = APIRouter()

from app.api.v1.endpoints import scrape
api_router.include_router(scrape.router, prefix="/scrape", tags=["scrape"])
