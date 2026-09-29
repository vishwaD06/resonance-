from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MatchResponse(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    similarity_score: Optional[float] = None
    match_reason: Optional[str] = None
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MatchAcceptRequest(BaseModel):
    match_id: int
    response: str  # 'accepted' or 'rejected'
