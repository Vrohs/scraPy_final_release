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
                    except Exception as e:
                        print(f"Failed to send webhook to {webhook.url}: {e}")

async def scrape_task(ctx, job_id: str, url: str, mode: str, selectors: dict = None, instruction: str = None, options: dict = None, user_id: str = None):
    print(f"Starting scrape job {job_id} for {url} in {mode} mode")
    
    # Update status to processing
    async with AsyncSessionLocal() as session:
        await session.execute(
            update(Job).where(Job.id == job_id).values(status="processing")
        )
        await session.commit()

    try:
        # 1. Scrape Content
        if options and options.get("renderJs"):
            html_content = await scrape_dynamic(url)
        else:
            html_content = await scrape_static(url)
            
        # 2. Extract Data
        data = {}
        if mode == "guided" and selectors:
            # Construct a prompt from selectors
            prompt = "Extract the following fields:\n"
            for key, selector in selectors.items():
                prompt += f"- {key} (CSS: {selector})\n"
            data = await analyze_page(html_content, prompt)
        elif mode == "smart" and instruction:
            data = await analyze_page(html_content, instruction)
        else:
            # Default: just return title and meta description
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
            
        # 4. Dispatch Webhook
        if user_id:
            await ctx["redis"].enqueue_job("dispatch_webhook", job_id, user_id)

    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(Job).where(Job.id == job_id).values(status="failed")
            )
            await session.commit()

async def startup(ctx):
    ctx["redis"] = await create_pool(RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT))

async def shutdown(ctx):
    await ctx["redis"].close()

class WorkerSettings:
    functions = [scrape_task, dispatch_webhook]
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT
    )
    on_startup = startup
    on_shutdown = shutdown
