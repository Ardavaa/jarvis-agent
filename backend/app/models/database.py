"""
Database models using SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase
from sqlalchemy.types import JSON as JSONType
import os


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jarvis.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    tasks = relationship("TaskHistory", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message model"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    extra_data = Column(JSONType, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class UserPreference(Base):
    """User preferences model"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, nullable=False, index=True)
    preferences = Column(JSONType, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TaskHistory(Base):
    """Task history model"""
    __tablename__ = "task_history"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    task_description = Column(Text, nullable=True)
    tools_used = Column(JSONType, nullable=True)
    status = Column(String, nullable=False)  # 'pending', 'completed', 'failed'
    result = Column(JSONType, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="tasks")


class InteractionLog(Base):
    """Interaction log model"""
    __tablename__ = "interaction_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    interaction_type = Column(String, nullable=False)  # 'chat', 'voice', 'telegram'
    extra_data = Column(JSONType, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
