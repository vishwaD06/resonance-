from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.auth.service import get_current_active_user
from app.database.schema import User
from app.matching.models import MatchResponse, MatchAcceptRequest
from app.matching.service import (
    find_best_match,
    respond_to_match,
    get_user_matches,
    get_pending_match
)

router = APIRouter()

@router.post("/find", response_model=MatchResponse)
async def find_match(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Find the best match for the current user"""
    match = await find_best_match(db, current_user.id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No match found. Complete your profile first."
        )
    return match

@router.get("/pending", response_model=MatchResponse)
async def get_pending_match_endpoint(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the current user's pending match"""
    match = await get_pending_match(db, current_user.id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending match found"
        )
    return match

@router.get("/my-matches", response_model=List[MatchResponse])
async def get_my_matches(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all matches for the current user"""
    matches = await get_user_matches(db, current_user.id)
    return matches

@router.post("/respond", response_model=MatchResponse)
async def respond_to_match_endpoint(
    request: MatchAcceptRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Respond to a match (accept or reject)"""
    if request.response not in ["accepted", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response must be 'accepted' or 'rejected'"
        )
    
    match = await respond_to_match(db, request.match_id, current_user.id, request.response)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    return match
