from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Optional for OAuth
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # 'google', 'apple', etc.
    oauth_id = Column(String, nullable=True)
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    preferences = relationship("Preferences", back_populates="user", uselist=False)
    interview_sessions = relationship("InterviewSession", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Structured traits extracted from interview
    traits = Column(JSON, nullable=True)  # Personality traits, values, communication style
    
    # Vector embedding for similarity search
    embedding = Column(Text, nullable=True)  # Stored as text array, will be converted to vector
    
    # Interview responses (full conversation history)
    interview_responses = Column(JSON, nullable=True)
    
    # Profile completion status
    is_complete = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    matches_as_user1 = relationship("Match", foreign_keys="Match.user1_id", back_populates="user1")
    matches_as_user2 = relationship("Match", foreign_keys="Match.user2_id", back_populates="user2")

class Preferences(Base):
    __tablename__ = "preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Hard filters for matching
    age_min = Column(Integer, nullable=True)
    age_max = Column(Integer, nullable=True)
    distance_max = Column(Integer, nullable=True)  # in miles
    gender_preference = Column(String, nullable=True)
    
    # Dealbreakers
    dealbreakers = Column(JSON, nullable=True)  # Array of dealbreaker criteria
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session state
    status = Column(String, default="in_progress")  # in_progress, completed, abandoned
    current_question = Column(Integer, default=0)
    
    # Conversation history
    messages = Column(JSON, nullable=True)  # Array of {role, content, timestamp}
    
    # Extracted traits (intermediate, before final profile creation)
    extracted_traits = Column(JSON, nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="interview_sessions")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Match status
    status = Column(String, default="pending")  # pending, accepted, rejected, expired
    
    # Match metrics
    similarity_score = Column(Float, nullable=True)  # Cosine similarity score
    match_reason = Column(Text, nullable=True)  # AI-generated rationale
    
    # User responses
    user1_response = Column(String, nullable=True)  # accepted, rejected
    user2_response = Column(String, nullable=True)
    user1_responded_at = Column(DateTime, nullable=True)
    user2_responded_at = Column(DateTime, nullable=True)
    
    # Interaction tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches_as_user2")
    interactions = relationship("Interaction", back_populates="match")

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    # Interaction type
    interaction_type = Column(String, nullable=False)  # message, date_scheduled, date_completed, feedback
    
    # Interaction data
    data = Column(JSON, nullable=True)  # Varies by interaction_type
    
    # Feedback for learning
    feedback_score = Column(Integer, nullable=True)  # 1-5 rating
    feedback_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    match = relationship("Match", back_populates="interactions")
