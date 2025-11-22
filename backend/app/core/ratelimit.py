import time
from fastapi import HTTPException, status
from redis.asyncio import Redis

class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def check_limit(self, key: str, limit: int, window: int = 60):
        """
        Check if the limit has been reached for the given key.
        key: Unique identifier (e.g. api_key_id)
        limit: Max requests allowed
        window: Time window in seconds (default 1 minute)
        """
        # Create a key for the current window
        # Simple approach: key + current_minute timestamp
        current_window = int(time.time() / window)
        redis_key = f"ratelimit:{key}:{current_window}"
        
        # Increment counter
        # pipeline to ensure atomicity of incr + expire
        async with self.redis.pipeline() as pipe:
            await pipe.incr(redis_key)
            await pipe.expire(redis_key, window + 10) # Expire slightly after window
            result = await pipe.execute()
            
        count = result[0]
        
        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        return True
