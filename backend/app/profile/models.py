from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ProfileCreate(BaseModel):
    traits: Dict[str, Any]
    interview_responses: List[Dict[str, Any]]

class ProfileUpdate(BaseModel):
    traits: Optional[Dict[str, Any]] = None
    is_complete: Optional[bool] = None

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    traits: Optional[Dict[str, Any]] = None
    is_complete: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
