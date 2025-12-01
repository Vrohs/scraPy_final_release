from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.api_key import ApiKey
from app.api.deps import get_current_user
from pydantic import BaseModel
from typing import List
import secrets
import hashlib
import uuid

router = APIRouter()

class ApiKeyCreate(BaseModel):
    name: str

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    created_at: str
    key: str = None # Only returned on creation

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post(
    "/",
    response_model=ApiKeyResponse,
    summary="Create API key",
    description="Generate a new API key for programmatic access. The full key is only shown once - save it securely!",
    response_description="New API key with full key value (only shown once)"
)
async def create_api_key(
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new API key for the authenticated user.
    
    - **name**: Friendly name to identify this key
    
    **IMPORTANT**: The full API key is only returned once. Store it securely!
    """
    # Generate a secure random key
    # Format: sk_live_<random_32_chars>
    raw_key = f"sk_live_{secrets.token_urlsafe(32)}"
    
    # Hash it for storage
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_prefix = raw_key[:12] # sk_live_XXXX
    
    user_id = current_user.get("sub") # Clerk user ID is in 'sub' claim
    
    api_key = ApiKey(
        id=str(uuid.uuid4()),
        key_prefix=key_prefix,
        key_hash=key_hash,
        user_id=user_id,
        name=data.name
    )
    
    db.add(api_key)
    await db.commit()
    
    return {
        "id": api_key.id,
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "created_at": api_key.created_at.isoformat(),
        "key": raw_key # Return full key only once
    }

@router.get(
    "/",
    response_model=List[ApiKeyResponse],
    summary="List API keys",
    description="Get all active API keys for the current user. Only key prefixes are shown for security.",
    response_description="List of active API keys"
)
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all active API keys for the authenticated user.
    
    Only the key prefix (first 12 characters) is shown for security. Full keys cannot be retrieved after creation.
    """
    user_id = current_user.get("sub")
    result = await db.execute(
        select(ApiKey)
        .where(ApiKey.user_id == user_id)
        .where(ApiKey.is_active == True)
        .order_by(ApiKey.created_at.desc())
    )
    keys = result.scalars().all()
    
    return [
        {
            "id": k.id,
            "name": k.name,
            "key_prefix": k.key_prefix,
            "created_at": k.created_at.isoformat()
        }
        for k in keys
    ]

@router.delete(
    "/{key_id}",
    summary="Revoke API key",
    description="Deactivate an API key. This action cannot be undone. The key will immediately stop working.",
    response_description="Key revocation status"
)
async def revoke_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke (deactivate) an API key.
    
    - **key_id**: The unique identifier of the key to revoke
    
    The key will be immediately deactivated and can no longer be used for authentication.
    """
    user_id = current_user.get("sub")
    result = await db.execute(
        select(ApiKey)
        .where(ApiKey.id == key_id)
        .where(ApiKey.user_id == user_id)
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")
        
    api_key.is_active = False
    await db.commit()
    
    return {"status": "revoked"}
