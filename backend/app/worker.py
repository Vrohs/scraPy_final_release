from arq.connections import RedisSettings
from app.core.config import settings
from app.services.scraper import scrape_static, scrape_dynamic
from app.services.llm import analyze_page
import json

async def startup(ctx):
    print("Worker starting...")

async def shutdown(ctx):
    print("Worker shutting down...")

async def scrape_task(ctx, job_id: str, url: str, mode: str, selectors: dict = None, instruction: str = None, options: dict = None):
    print(f"Scraping {url} for job {job_id}")
    try:
        data = {}
        html_content = ""
        
        # 1. Scrape
        if options and options.get("renderJs"):
            result = await scrape_dynamic(url, selectors if mode == "guided" else None)
        else:
            result = await scrape_static(url, selectors if mode == "guided" else None)
            
        if mode == "guided":
            data = result
        elif mode == "smart":
            html_content = result.get("html", "")
            if instruction:
                analysis = await analyze_page(html_content, instruction)
                data = analysis
            else:
                data = {"error": "No instruction provided for smart mode"}
        
        # Store result in Redis for retrieval
        # We use the job_id as the key
        await ctx['redis'].set(f"job:{job_id}", json.dumps({
            "status": "completed",
            "data": data,
            "url": url,
            "mode": mode
        }), ex=3600) # Expire in 1 hour
        
        return data
        
    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        await ctx['redis'].set(f"job:{job_id}", json.dumps({
            "status": "failed",
            "error": str(e),
            "url": url,
            "mode": mode
        }), ex=3600)

class WorkerSettings:
    functions = [scrape_task]
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT
    )
    on_startup = startup
    on_shutdown = shutdown

