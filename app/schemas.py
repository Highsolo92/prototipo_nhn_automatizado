from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime  # 👈 nuevo

class LeadIn(BaseModel):
    name: str
    email: str
    source: Optional[str] = "manual"
    notes: Optional[str] = ""
    metadata: Optional[Dict[str, str]] = None

class LeadOut(BaseModel):
    id: int
    created_at: datetime   # 👈 antes estaba str
    name: str
    email: str
    source: Optional[str]
    priority: Optional[str]
    status: Optional[str]
    owner: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True
