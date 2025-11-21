from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import json

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str
    mode: str = "guided"  # guided, smart
    selectors: Optional[Dict[str, str]] = None
    instruction: Optional[str] = None
    options: Optional[Dict[str, bool]] = None

class JobResponse(BaseModel):
    job_id: str
    status: str

@router.post("/", response_model=JobResponse)
async def create_scrape_job(request: ScrapeRequest, req: Request):
    job_id = str(uuid.uuid4())
    
    # Enqueue job to Arq
    await req.app.state.redis.enqueue_job(
        "scrape_task",
        job_id=job_id,
        url=request.url,
        mode=request.mode,
        selectors=request.selectors,
        instruction=request.instruction,
        options=request.options
    )
    
    # Set initial status in Redis
    await req.app.state.redis.set(f"job:{job_id}", json.dumps({
        "status": "pending",
        "url": request.url,
        "mode": request.mode,
        "created_at": "now"
    }), ex=3600)
    
    return {"job_id": job_id, "status": "pending"}

@router.get("/{job_id}")
async def get_job_status(job_id: str, req: Request):
    data = await req.app.state.redis.get(f"job:{job_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(data)

@router.post("/{job_id}/save", response_model=JobResponse)
async def save_job(job_id: str, req: Request):
    # Get job from Redis
    data = await req.app.state.redis.get(f"job:{job_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Job not found in cache")
    
    job_data = json.loads(data)
    
    # Save to DB
    from app.core.database import AsyncSessionLocal
    from app.models.job import Job
    
    async with AsyncSessionLocal() as session:
        # Check if already exists
        existing = await session.get(Job, job_id)
        if existing:
            return {"job_id": job_id, "status": "saved"}
            
        db_job = Job(
            id=job_id,
            url=job_data["url"],
            mode=job_data["mode"],
            status=job_data["status"],
            data=job_data.get("data")
        )
        session.add(db_job)
        await session.commit()
        
    return {"job_id": job_id, "status": "saved"}

@router.get("/history/all")
async def get_history():
    from app.core.database import AsyncSessionLocal
    from app.models.job import Job
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).order_by(Job.created_at.desc()))
        jobs = result.scalars().all()
        return jobs
