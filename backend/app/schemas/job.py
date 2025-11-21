from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class JobBase(BaseModel):
    url: str
    mode: str
    status: str
    data: Optional[Dict[str, Any] | list] = None

class JobCreate(JobBase):
    id: str

class Job(JobBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
