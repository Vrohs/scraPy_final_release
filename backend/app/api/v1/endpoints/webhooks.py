from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.webhook import Webhook
from app.api.deps import get_current_user
from pydantic import BaseModel, HttpUrl
from typing import List
import secrets
import uuid

router = APIRouter()

class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[str] = ["job.completed"]

class WebhookResponse(BaseModel):
    id: str
    url: str
    events: List[str]
    secret: str
    created_at: str

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=WebhookResponse)
async def create_webhook(
    data: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    
    # Generate a secret for signing
    secret = secrets.token_hex(24)
    
    webhook = Webhook(
        id=str(uuid.uuid4()),
        url=str(data.url),
        events=data.events,
        secret=secret,
        user_id=user_id
    )
    
    db.add(webhook)
    await db.commit()
    
    return {
        "id": webhook.id,
        "url": webhook.url,
        "events": webhook.events,
        "secret": webhook.secret,
        "created_at": webhook.created_at.isoformat()
    }

@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    result = await db.execute(
        select(Webhook)
        .where(Webhook.user_id == user_id)
        .order_by(Webhook.created_at.desc())
    )
    webhooks = result.scalars().all()
    
    return [
        {
            "id": w.id,
            "url": w.url,
            "events": w.events,
            "secret": w.secret,
            "created_at": w.created_at.isoformat()
        }
        for w in webhooks
    ]

@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    result = await db.execute(
        select(Webhook)
        .where(Webhook.id == webhook_id)
        .where(Webhook.user_id == user_id)
    )
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
        
    await db.delete(webhook)
    await db.commit()
    
    return {"status": "deleted"}
