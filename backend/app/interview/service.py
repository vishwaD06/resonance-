from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

from app.database.schema import InterviewSession, User
from app.interview.models import Message, ExtractedTraits

load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Interview questions for v0.1 (simplified version)
INTERVIEW_QUESTIONS = [
    "Tell me about yourself and what you're looking for in a connection.",
    "What are your core values in life and relationships?",
    "How would you describe your communication style?",
    "What activities or interests bring you the most joy?",
    "What are some things you absolutely cannot compromise on in a relationship?",
]

async def start_interview(db: Session, user_id: int) -> InterviewSession:
    """Start a new interview session for a user"""
    # Check for existing incomplete session
    existing_session = db.query(InterviewSession).filter(
        InterviewSession.user_id == user_id,
        InterviewSession.status == "in_progress"
    ).first()
    
    if existing_session:
        return existing_session
    
    # Create new session
    session = InterviewSession(
        user_id=user_id,
        status="in_progress",
        current_question=0,
        messages=[
            {
                "role": "assistant",
                "content": INTERVIEW_QUESTIONS[0],
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

async def submit_response(
    db: Session, 
    session_id: int, 
    user_message: str
) -> tuple[InterviewSession, str, bool]:
    """Submit a response to the interview and get next question"""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()
    
    if not session or session.status != "in_progress":
        raise ValueError("Invalid or completed session")
    
    # Add user message to history
    session.messages.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Move to next question
    session.current_question += 1
    
    # Check if interview is complete
    if session.current_question >= len(INTERVIEW_QUESTIONS):
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        
        # Extract traits from the conversation
        traits = await extract_traits_from_conversation(session.messages)
        session.extracted_traits = traits.dict()
        
        db.commit()
        db.refresh(session)
        return session, "Interview complete! Your profile is being created.", True
    
    # Add next question
    next_question = INTERVIEW_QUESTIONS[session.current_question]
    session.messages.append({
        "role": "assistant",
        "content": next_question,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    db.commit()
    db.refresh(session)
    return session, next_question, False

async def extract_traits_from_conversation(messages: List[Dict]) -> ExtractedTraits:
    """Use OpenAI to extract structured traits from the conversation"""
    # Convert messages to format for OpenAI
    conversation = "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in messages
    ])
    
    prompt = f"""
    Analyze this conversation and extract personality traits, values, communication style, interests, and dealbreakers.
    
    Conversation:
    {conversation}
    
    Return a JSON object with the following structure:
    {{
        "personality_traits": {{
            "openness": "high/medium/low",
            "conscientiousness": "high/medium/low", 
            "extraversion": "high/medium/low",
            "agreeableness": "high/medium/low",
            "emotional_stability": "high/medium/low"
        }},
        "values": ["value1", "value2", "value3"],
        "communication_style": "description of communication style",
        "interests": ["interest1", "interest2", "interest3"],
        "dealbreakers": ["dealbreaker1", "dealbreaker2"]
    }}
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a skilled psychologist and relationship expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        import json
        traits_data = json.loads(response.choices[0].message.content)
        return ExtractedTraits(**traits_data)
    except Exception as e:
        print(f"Error extracting traits: {e}")
        # Return default traits if AI extraction fails
        return ExtractedTraits(
            personality_traits={},
            values=[],
            communication_style="Not specified",
            interests=[],
            dealbreakers=[]
        )

async def get_session(db: Session, session_id: int) -> Optional[InterviewSession]:
    """Get an interview session by ID"""
    return db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()
