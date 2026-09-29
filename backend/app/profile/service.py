from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

from app.database.schema import Profile, User
from app.profile.models import ProfileCreate, ProfileUpdate

load_dotenv()

# Initialize OpenAI client for embeddings
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def create_profile(db: Session, user_id: int, profile_data: ProfileCreate) -> Profile:
    """Create a new profile for a user"""
    # Check if profile already exists
    existing_profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if existing_profile:
        raise ValueError("Profile already exists for this user")
    
    # Generate embedding from traits
    embedding = await generate_embedding(profile_data.traits)
    
    profile = Profile(
        user_id=user_id,
        traits=profile_data.traits,
        interview_responses=profile_data.interview_responses,
        embedding=embedding,
        is_complete=False
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

async def update_profile(
    db: Session, 
    user_id: int, 
    profile_update: ProfileUpdate
) -> Optional[Profile]:
    """Update an existing profile"""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        return None
    
    if profile_update.traits is not None:
        profile.traits = profile_update.traits
        # Regenerate embedding when traits change
        profile.embedding = await generate_embedding(profile_update.traits)
    
    if profile_update.is_complete is not None:
        profile.is_complete = profile_update.is_complete
        if profile_update.is_complete and not profile.completed_at:
            profile.completed_at = datetime.utcnow()
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile

async def get_profile(db: Session, user_id: int) -> Optional[Profile]:
    """Get a user's profile"""
    return db.query(Profile).filter(Profile.user_id == user_id).first()

async def complete_profile(db: Session, user_id: int) -> Optional[Profile]:
    """Mark a profile as complete"""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        return None
    
    profile.is_complete = True
    profile.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile

async def generate_embedding(traits: Dict[str, Any]) -> str:
    """Generate embedding vector from personality traits using OpenAI"""
    # Convert traits to text for embedding
    trait_text = str(traits)
    
    try:
        response = await client.embeddings.create(
            model="text-embedding-3-large",
            input=trait_text
        )
        
        # Convert embedding to string for storage (will be converted back for similarity search)
        embedding_vector = response.data[0].embedding
        return ",".join(map(str, embedding_vector))
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return empty string if embedding generation fails
        return ""

def parse_embedding(embedding_str: str) -> list:
    """Parse stored embedding string back to list of floats"""
    if not embedding_str:
        return []
    return [float(x) for x in embedding_str.split(",")]
