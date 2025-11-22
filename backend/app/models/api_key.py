from sqlalchemy import Column, String, Boolean, DateTime, Integer
from app.core.database import Base
from datetime import datetime
import uuid

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key_prefix = Column(String, index=True) # First 8 chars for display
    key_hash = Column(String, index=True)   # Hashed full key
    user_id = Column(String, index=True)    # Clerk User ID
    name = Column(String)                   # Friendly name
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=60) # Requests per minute
    usage_count = Column(Integer, default=0) # Total requests
    created_at = Column(DateTime, default=datetime.utcnow)
