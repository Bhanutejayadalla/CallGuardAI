"""
Call Analysis Model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class CallClassification(str, enum.Enum):
    SAFE = "safe"
    SPAM = "spam"
    FRAUD = "fraud"
    PHISHING = "phishing"
    ROBOCALL = "robocall"
    UNKNOWN = "unknown"


class CallStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Call(Base):
    """Call record model"""
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Call metadata
    caller_number = Column(String(20), nullable=True)
    callee_number = Column(String(20), nullable=True)
    duration_seconds = Column(Float, default=0)
    call_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Audio info
    audio_file_path = Column(String(500), nullable=True)
    audio_format = Column(String(10), nullable=True)
    sample_rate = Column(Integer, default=16000)
    
    # Transcription
    transcript = Column(Text, nullable=True)
    transcript_language = Column(String(10), default="en")
    transcript_confidence = Column(Float, default=0)
    
    # Analysis results
    status = Column(Enum(CallStatus), default=CallStatus.PENDING)
    classification = Column(Enum(CallClassification), default=CallClassification.UNKNOWN)
    risk_score = Column(Float, default=0)  # 0-100
    
    # Detailed scores
    spam_score = Column(Float, default=0)
    fraud_score = Column(Float, default=0)
    phishing_score = Column(Float, default=0)
    robocall_score = Column(Float, default=0)
    
    # Fraud indicators
    suspicious_keywords = Column(JSON, default=list)
    fraud_indicators = Column(JSON, default=list)
    highlighted_phrases = Column(JSON, default=list)
    
    # Acoustic analysis
    acoustic_features = Column(JSON, default=dict)
    voice_characteristics = Column(JSON, default=dict)
    
    # Behavioral analysis
    behavioral_patterns = Column(JSON, default=dict)
    intent_analysis = Column(JSON, default=dict)
    
    # AI explanation
    ai_explanation = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="calls")
    
    def to_dict(self):
        return {
            "id": self.id,
            "call_id": self.call_id,
            "caller_number": self.caller_number,
            "callee_number": self.callee_number,
            "duration_seconds": self.duration_seconds,
            "call_timestamp": self.call_timestamp.isoformat() if self.call_timestamp else None,
            "transcript": self.transcript,
            "transcript_language": self.transcript_language,
            "status": self.status.value if self.status else None,
            "classification": self.classification.value if self.classification else None,
            "risk_score": self.risk_score,
            "spam_score": self.spam_score,
            "fraud_score": self.fraud_score,
            "phishing_score": self.phishing_score,
            "robocall_score": self.robocall_score,
            "suspicious_keywords": self.suspicious_keywords,
            "fraud_indicators": self.fraud_indicators,
            "highlighted_phrases": self.highlighted_phrases,
            "acoustic_features": self.acoustic_features,
            "voice_characteristics": self.voice_characteristics,
            "behavioral_patterns": self.behavioral_patterns,
            "intent_analysis": self.intent_analysis,
            "ai_explanation": self.ai_explanation,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None
        }


class CallSegment(Base):
    """Call segment for detailed analysis"""
    __tablename__ = "call_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    speaker = Column(String(50), nullable=True)
    text = Column(Text, nullable=True)
    
    # Segment analysis
    sentiment = Column(String(20), nullable=True)
    urgency_score = Column(Float, default=0)
    stress_score = Column(Float, default=0)
    is_suspicious = Column(Boolean, default=False)
    flags = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
