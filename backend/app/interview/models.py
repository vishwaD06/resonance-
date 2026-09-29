from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[datetime] = None

class InterviewStart(BaseModel):
    user_id: int

class InterviewResponse(BaseModel):
    session_id: int
    message: str
    is_complete: bool

class InterviewSubmit(BaseModel):
    session_id: int
    message: str

class ExtractedTraits(BaseModel):
    personality_traits: Dict[str, Any]
    values: List[str]
    communication_style: str
    interests: List[str]
    dealbreakers: List[str]
