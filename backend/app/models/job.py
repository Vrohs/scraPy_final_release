from sqlalchemy import Column, String, Integer, JSON, DateTime
from app.core.database import Base
from datetime import datetime

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, index=True)
    mode = Column(String)
    status = Column(String)
    data = Column(JSON)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
