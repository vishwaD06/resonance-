from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

from app.database.schema import Profile, Match, User, Preferences
from app.profile.service import parse_embedding
from app.matching.models import MatchResponse

load_dotenv()

# Initialize OpenAI client for match rationale generation
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def find_best_match(db: Session, user_id: int) -> Optional[Match]:
    """Find the best match for a user using cosine similarity"""
    # Get user's profile
    user_profile = db.query(Profile).filter(
        Profile.user_id == user_id,
        Profile.is_complete == True
    ).first()
    
    if not user_profile or not user_profile.embedding:
        return None
    
    # Get user's preferences for hard filters
    user_preferences = db.query(Preferences).filter(
        Preferences.user_id == user_id
    ).first()
    
    # Get all other complete profiles
    other_profiles = db.query(Profile).filter(
        Profile.user_id != user_id,
        Profile.is_complete == True,
        Profile.embedding.isnot(None)
    ).all()
    
    if not other_profiles:
        return None
    
    # Parse user's embedding
    user_embedding = parse_embedding(user_profile.embedding)
    if not user_embedding:
        return None
    
    # Calculate similarity scores
    similarities = []
    for profile in other_profiles:
        # Apply hard filters if preferences exist
        if user_preferences:
            if not passes_hard_filters(profile, user_preferences):
                continue
        
        # Calculate cosine similarity
        other_embedding = parse_embedding(profile.embedding)
        if other_embedding:
            similarity = cosine_similarity(
                [user_embedding], 
                [other_embedding]
            )[0][0]
            similarities.append((profile, similarity))
    
    if not similarities:
        return None
    
    # Sort by similarity score (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get the best match
    best_profile, best_score = similarities[0]
    
    # Check if match already exists
    existing_match = db.query(Match).filter(
        ((Match.user1_id == user_id) & (Match.user2_id == best_profile.user_id)) |
        ((Match.user1_id == best_profile.user_id) & (Match.user2_id == user_id)),
        Match.status.in_(["pending", "accepted"])
    ).first()
    
    if existing_match:
        return existing_match
    
    # Generate match rationale using OpenAI
    match_reason = await generate_match_rationale(user_profile, best_profile)
    
    # Create new match
    match = Match(
        user1_id=user_id,
        user2_id=best_profile.user_id,
        similarity_score=float(best_score),
        match_reason=match_reason,
        status="pending",
        expires_at=datetime.utcnow() + timedelta(days=7)  # Expire in 7 days
    )
    
    db.add(match)
    db.commit()
    db.refresh(match)
    return match

def passes_hard_filters(profile: Profile, preferences: Preferences) -> bool:
    """Check if a profile passes user's hard filters"""
    # For v0.1, we'll implement basic filtering
    # In production, this would check age, distance, etc.
    # For now, we'll just return True to allow all matches
    return True

async def generate_match_rationale(profile1: Profile, profile2: Profile) -> str:
    """Generate AI rationale for why two users matched"""
    try:
        traits1 = profile1.traits or {}
        traits2 = profile2.traits or {}
        
        prompt = f"""
        Generate a brief, compelling explanation (2-3 sentences) for why these two people would be a good match based on their personality traits.
        
        Person 1 traits: {traits1}
        Person 2 traits: {traits2}
        
        Focus on complementary personality traits, shared values, or compatible communication styles.
        Be specific and encouraging but not overly romantic.
        """
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a relationship expert who writes thoughtful match introductions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating match rationale: {e}")
        return "You share complementary personality traits and values that suggest strong compatibility."

async def respond_to_match(
    db: Session, 
    match_id: int, 
    user_id: int, 
    response: str
) -> Optional[Match]:
    """Record user's response to a match"""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return None
    
    # Verify user is part of this match
    if match.user1_id != user_id and match.user2_id != user_id:
        return None
    
    # Update the appropriate user's response
    if match.user1_id == user_id:
        match.user1_response = response
        match.user1_responded_at = datetime.utcnow()
    else:
        match.user2_response = response
        match.user2_responded_at = datetime.utcnow()
    
    # Update match status if both have responded
    if match.user1_response and match.user2_response:
        if match.user1_response == "accepted" and match.user2_response == "accepted":
            match.status = "accepted"
        else:
            match.status = "rejected"
    
    db.commit()
    db.refresh(match)
    return match

async def get_user_matches(db: Session, user_id: int) -> List[Match]:
    """Get all matches for a user"""
    matches = db.query(Match).filter(
        ((Match.user1_id == user_id) | (Match.user2_id == user_id))
    ).order_by(Match.created_at.desc()).all()
    return matches

async def get_pending_match(db: Session, user_id: int) -> Optional[Match]:
    """Get the most recent pending match for a user"""
    match = db.query(Match).filter(
        ((Match.user1_id == user_id) | (Match.user2_id == user_id)),
        Match.status == "pending"
    ).order_by(Match.created_at.desc()).first()
    return match
