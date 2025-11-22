from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token
from app.core.database import AsyncSessionLocal
from app.models.api_key import ApiKey
from sqlalchemy import select
from typing import Dict, Any, Optional
import hashlib

from app.core.ratelimit import RateLimiter

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    token_creds: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    # 1. Check for API Key in header
    api_key_header = request.headers.get("X-API-Key")
    if api_key_header:
        # Validate API Key
        key_hash = hashlib.sha256(api_key_header.encode()).hexdigest()
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(ApiKey).where(ApiKey.key_hash == key_hash))
            api_key = result.scalar_one_or_none()
            
            if api_key and api_key.is_active:
                # Check Rate Limit
                if hasattr(request.app.state, "redis"):
                    limiter = RateLimiter(request.app.state.redis)
                    await limiter.check_limit(f"apikey:{api_key.id}", api_key.rate_limit)
                
                # Return a user-like dict. We use the user_id associated with the key.
                return {"sub": api_key.user_id, "api_key_id": api_key.id}
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid or inactive API Key"
                )

    # 2. Check for Bearer Token
    if token_creds:
        return verify_token(token_creds.credentials)
        
    # 3. Neither found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )
