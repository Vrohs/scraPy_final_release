import asyncio
import json
import httpx
import hmac
import hashlib
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings
from app.services.scraper import scrape_static, scrape_dynamic
from app.services.llm import analyze_page
from app.core.database import AsyncSessionLocal
from app.models.job import Job
from app.models.webhook import Webhook
from sqlalchemy import select, update
from datetime import datetime
from app.core.logging import logger, log_job_completed, log_job_failed, log_webhook_dispatched

async def dispatch_webhook(ctx, job_id: str, user_id: str):
    """
    Task to dispatch webhooks for a completed job.
    """
    async with AsyncSessionLocal() as session:
        # Fetch job details
        result = await session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            return

        # Fetch user's webhooks
        result = await session.execute(select(Webhook).where(Webhook.user_id == user_id))
        webhooks = result.scalars().all()
        
        if not webhooks:
            return

        payload = {
            "event": "job.completed",
            "job_id": job.id,
            "url": job.url,
            "status": job.status,
            "data": job.data,
            "created_at": job.created_at.isoformat(),
            "completed_at": datetime.utcnow().isoformat()
        }
        
        payload_json = json.dumps(payload)
        
        async with httpx.AsyncClient() as client:
            for webhook in webhooks:
                if "job.completed" in webhook.events:
                    # Sign payload
                    signature = hmac.new(
                        webhook.secret.encode(),
                        payload_json.encode(),
                        hashlib.sha256
                    ).hexdigest()
                    
                    try:
                        await client.post(
                            webhook.url,
                            content=payload_json,
                            headers={
                                "Content-Type": "application/json",
                                "X-ScraPy-Signature": signature,
                                "X-ScraPy-Event": "job.completed"
                            },
                            timeout=10.0
                        )
                        log_webhook_dispatched(job_id, webhook.url, True)
                    except Exception as e:
                        logger.error(f"Failed to send webhook to {webhook.url}: {e}")
                        log_webhook_dispatched(job_id, webhook.url, False)

async def scrape_task(ctx, job_id: str, url: str, mode: str, selectors: dict = None, instruction: str = None, options: dict = None, user_id: str = None):
    logger.info(f"Starting scrape job {job_id} for {url} in {mode} mode")
    start_time = datetime.utcnow()
    
    # Create job in DB if it doesn't exist, update status to processing
    async with AsyncSessionLocal() as session:
        existing_job = await session.get(Job, job_id)
        if not existing_job:
            new_job = Job(
                id=job_id,
                url=url,
                mode=mode,
                status="processing"
            )
            session.add(new_job)
        else:
            await session.execute(
                update(Job).where(Job.id == job_id).values(status="processing")
            )
        await session.commit()

    try:
        # 1. Scrape Content
        # 1. Scrape & Extract
        if mode == "guided" and selectors:
            if options and options.get("renderJs"):
                data = await scrape_dynamic(url, selectors)
            else:
                data = await scrape_static(url, selectors)
        
        elif mode == "smart" and instruction:
            # For smart mode, we need the raw HTML first
            if options and options.get("renderJs"):
                result = await scrape_dynamic(url)
            else:
                result = await scrape_static(url)
            
            html_content = result.get("html", "")
            data = await analyze_page(html_content, instruction)
            
        else:
            # Default: just return title and meta description using LLM (or could be simple soup)
            if options and options.get("renderJs"):
                result = await scrape_dynamic(url)
            else:
                result = await scrape_static(url)
                
            html_content = result.get("html", "")
            data = await analyze_page(html_content, "Extract the page title and main summary.")

        # 3. Save Results
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="completed",
                    data=data
                )
            )
            await session.commit()
            
        # Update Redis so API sees the change immediately
        await ctx["redis"].set(f"job:{job_id}", json.dumps({
            "status": "completed",
            "url": url,
            "mode": mode,
            "data": data,
            "created_at": datetime.utcnow().isoformat() # Approximate
        }), ex=3600)
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        log_job_completed(job_id, duration)
            
        # 4. Dispatch Webhook
        if user_id:
            await ctx["redis"].enqueue_job("dispatch_webhook", job_id, user_id)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Job {job_id} failed: {error_msg}")
        log_job_failed(job_id, error_msg)
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Job).where(Job.id == job_id).values(
                    status="failed",
                    error=error_msg
                )
            )
            await session.commit()
            
        # Update Redis with error
        await ctx["redis"].set(f"job:{job_id}", json.dumps({
            "status": "failed",
            "url": url,
            "mode": mode,
            "error": error_msg,
            "created_at": datetime.utcnow().isoformat()
        }), ex=3600)

async def startup(ctx):
    ctx["redis"] = await create_pool(RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT))

async def shutdown(ctx):
    await ctx["redis"].close()

class WorkerSettings:
    functions = [scrape_task, dispatch_webhook]
    
    # Parse Redis URL for production support
    from urllib.parse import urlparse
    parsed = urlparse(settings.redis_connection_url)
    
    if parsed.hostname:
        redis_settings = RedisSettings(
            host=parsed.hostname,
            port=parsed.port or 6379,
            password=parsed.password,
            ssl=parsed.scheme == "rediss"
        )
    else:
        redis_settings = RedisSettings(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT
        )
        
    on_startup = startup
    on_shutdown = shutdown
