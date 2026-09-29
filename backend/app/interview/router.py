from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.auth.service import get_current_active_user
from app.database.schema import User
from app.interview.models import InterviewStart, InterviewSubmit, InterviewResponse
from app.interview.service import (
    start_interview,
    submit_response,
    get_session
)

router = APIRouter()

@router.post("/start", response_model=InterviewResponse)
async def start_interview_endpoint(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a new interview session"""
    session = await start_interview(db, current_user.id)
    
    # Get the first question from the session
    first_message = session.messages[0]["content"] if session.messages else "Welcome to the interview!"
    
    return InterviewResponse(
        session_id=session.id,
        message=first_message,
        is_complete=False
    )

@router.post("/respond", response_model=InterviewResponse)
async def submit_interview_response(
    response: InterviewSubmit,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit a response to the interview"""
    try:
        session, next_message, is_complete = await submit_response(
            db, response.session_id, response.message
        )
        
        # Verify session belongs to current user
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        return InterviewResponse(
            session_id=session.id,
            message=next_message,
            is_complete=is_complete
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/session/{session_id}")
async def get_interview_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get interview session details"""
    session = await get_session(db, session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify session belongs to current user
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session"
        )
    
    return {
        "session_id": session.id,
        "status": session.status,
        "current_question": session.current_question,
        "messages": session.messages,
        "extracted_traits": session.extracted_traits,
        "started_at": session.started_at,
        "completed_at": session.completed_at
    }
