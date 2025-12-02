from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, HttpUrl, field_validator, Field
from typing import Optional, Dict, Any
import uuid
import json
import ipaddress
from urllib.parse import urlparse

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str = Field(..., max_length=2048)
    mode: str = "guided"  # guided, smart
    selectors: Optional[Dict[str, str]] = Field(None, max_length=50)
    instruction: Optional[str] = Field(None, max_length=5000)
    options: Optional[Dict[str, bool]] = None
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL and prevent SSRF attacks"""
        # Basic URL validation
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        
        try:
            parsed = urlparse(v)
            hostname = parsed.hostname
            
            if not hostname:
                raise ValueError('Invalid URL: no hostname')
            
            # Try to resolve to IP and check if it's private
            try:
                ip = ipaddress.ip_address(hostname)
                # Block private/local IPs
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    raise ValueError('Access to private IP addresses is not allowed')
            except ValueError:
                # Not an IP address, it's a hostname - that's fine
                # Additional check: block localhost variants
                if hostname.lower() in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
                    raise ValueError('Access to localhost is not allowed')
        except Exception as e:
            raise ValueError(f'Invalid URL: {str(e)}')
        
        return v
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in ['guided', 'smart']:
            raise ValueError('Mode must be either "guided" or "smart"')
        return v

class JobResponse(BaseModel):
    job_id: str
    status: str

from app.api.deps import get_current_user

@router.post(
    "/", 
    response_model=JobResponse,
    summary="Create a scraping job",
    description="Submit a URL to be scraped. The job will be processed asynchronously. Use the job_id to check status and retrieve results.",
    response_description="Job created successfully with unique job_id"
)
async def create_scrape_job(
    request: ScrapeRequest, 
    req: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new scraping job.
    
    - **url**: Target URL to scrape (must be http/https, no private IPs)
    - **mode**: 'guided' (CSS selectors) or 'smart' (AI extraction)
    - **selectors**: CSS selectors for guided mode (optional)
    - **instruction**: Natural language instruction for smart mode (optional)
    - **options**: Additional options like renderJs for dynamic content (optional)
    
    Returns a job_id to track the scraping progress.
    """
    job_id = str(uuid.uuid4())
    
    # Enqueue job to Arq
    from app.core.logging import logger
    logger.info(f"Enqueueing job {job_id} for URL {request.url} in {request.mode} mode")
    
    try:
        await req.app.state.redis.enqueue_job(
            "scrape_task",
            job_id=job_id,
            url=request.url,
            mode=request.mode,
            selectors=request.selectors,
            instruction=request.instruction,
            options=request.options,
            user_id=current_user["sub"] # Pass user_id for webhooks
        )
        logger.info(f"Job {job_id} enqueued successfully")
    except Exception as e:
        logger.error(f"Failed to enqueue job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue job: {str(e)}")
    
    # Set initial status in Redis
    await req.app.state.redis.set(f"job:{job_id}", json.dumps({
        "status": "pending",
        "url": request.url,
        "mode": request.mode,
        "created_at": "now"
    }), ex=3600)
    
    return {"job_id": job_id, "status": "pending"}

@router.get(
    "/{job_id}",
    summary="Get job status and results",
    description="Retrieve the current status and results of a scraping job. Poll this endpoint until status is 'completed' or 'failed'.",
    response_description="Job status and data"
)
async def get_job_status(
    job_id: str, 
    req: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get the status and results of a scraping job.
    
    - **job_id**: The unique identifier returned when creating the job
    
    Possible statuses: pending, processing, completed, failed
    """
    data = await req.app.state.redis.get(f"job:{job_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(data)

@router.post(
    "/{job_id}/save", 
    response_model=JobResponse,
    summary="Save job to database",
    description="Persist a completed job from Redis cache to the PostgreSQL database for long-term storage.",
    response_description="Job saved to database"
)
async def save_job(
    job_id: str, 
    req: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Save a job from cache to permanent database storage.
    
    - **job_id**: The unique identifier of the job to save
    
    Jobs are initially stored in Redis cache (1 hour TTL). Use this endpoint to persist important results.
    """
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

@router.get(
    "/history/all",
    summary="Get scraping history",
    description="Retrieve all saved scraping jobs for the current user, ordered by creation date (newest first).",
    response_description="List of all saved jobs"
)
async def get_history(current_user: dict = Depends(get_current_user)):
    """
    Get all saved scraping jobs for the authenticated user.
    
    Returns jobs stored in the database (not cached jobs). Only returns jobs that were explicitly saved.
    """
    from app.core.database import AsyncSessionLocal
    from app.models.job import Job
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).order_by(Job.created_at.desc()))
        jobs = result.scalars().all()
        return jobs
