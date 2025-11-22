from sqlalchemy import Column, String, JSON, DateTime
from app.core.database import Base
from datetime import datetime
import uuid

class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String, nullable=False)
    events = Column(JSON, default=["job.completed"]) # List of events to subscribe to
    secret = Column(String, nullable=False) # Secret for HMAC signature
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
