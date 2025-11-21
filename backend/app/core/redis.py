from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings
from urllib.parse import urlparse

async def create_redis_pool():
    # Use the smart property that handles both local and production
    redis_url = settings.redis_connection_url
    
    # Parse the URL to extract host, port, and other parameters
    parsed = urlparse(redis_url)
    
    # Handle both redis:// URLs (Railway) and local host:port
    if parsed.hostname:
        return await create_pool(
            RedisSettings(
                host=parsed.hostname,
                port=parsed.port or 6379,
                password=parsed.password if parsed.password else None
            )
        )
    else:
        # Fallback to direct host/port (shouldn't happen with our property)
        return await create_pool(
            RedisSettings(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        )
