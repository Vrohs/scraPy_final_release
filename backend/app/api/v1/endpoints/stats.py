from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.job import Job

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

from app.api.deps import get_current_user

@router.get("/")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Total jobs
    result = await db.execute(select(func.count(Job.id)))
    total_jobs = result.scalar() or 0
    
    # Completed jobs (Pages Scraped)
    result = await db.execute(select(func.count(Job.id)).where(Job.status == "completed"))
    completed_jobs = result.scalar() or 0
    
    # Success Rate
    success_rate = 0.0
    if total_jobs > 0:
        success_rate = (completed_jobs / total_jobs) * 100
        
    return {
        "total_jobs": total_jobs,
        "pages_scraped": completed_jobs,
        "success_rate": round(success_rate, 1)
    }
