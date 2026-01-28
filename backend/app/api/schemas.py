"""
Pydantic Schemas for API
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class ClassificationType(str, Enum):
    SAFE = "safe"
    SPAM = "spam"
    FRAUD = "fraud"
    PHISHING = "phishing"
    ROBOCALL = "robocall"
    UNKNOWN = "unknown"


class StatusType(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Call Schemas
class CallBase(BaseModel):
    caller_number: Optional[str] = None
    callee_number: Optional[str] = None
    call_timestamp: Optional[datetime] = None


class CallCreate(CallBase):
    pass


class AnalysisResult(BaseModel):
    """Analysis result schema"""
    call_id: str
    status: StatusType
    classification: ClassificationType
    risk_score: float = Field(ge=0, le=100)
    
    # Individual scores
    spam_score: float = Field(ge=0, le=1)
    fraud_score: float = Field(ge=0, le=1)
    phishing_score: float = Field(ge=0, le=1)
    robocall_score: float = Field(ge=0, le=1)
    
    # Transcript
    transcript: Optional[str] = None
    transcript_language: str = "en"
    transcript_confidence: float = 0
    
    # Detailed analysis
    suspicious_keywords: List[str] = []
    fraud_indicators: List[Dict[str, Any]] = []
    highlighted_phrases: List[Dict[str, Any]] = []
    
    # Voice analysis
    voice_characteristics: Dict[str, Any] = {}
    acoustic_features: Dict[str, Any] = {}
    
    # Behavioral analysis
    behavioral_patterns: Dict[str, Any] = {}
    intent_analysis: Dict[str, Any] = {}
    
    # Explanation
    ai_explanation: str = ""
    confidence_score: float = 0
    
    # Metadata
    duration_seconds: float = 0
    analyzed_at: Optional[datetime] = None


class CallResponse(CallBase):
    id: int
    call_id: str
    status: StatusType
    classification: ClassificationType
    risk_score: float
    transcript: Optional[str] = None
    ai_explanation: Optional[str] = None
    created_at: datetime
    analyzed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CallDetailResponse(AnalysisResult):
    id: int
    caller_number: Optional[str] = None
    callee_number: Optional[str] = None
    call_timestamp: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    preferred_language: str
    dark_mode: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Rule Schemas
class RuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: str = "keyword"
    category: str = "general"
    keywords: List[str] = []
    patterns: List[str] = []
    weight: float = 1.0
    language: str = "en"
    is_active: bool = True


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    patterns: Optional[List[str]] = None
    weight: Optional[float] = None
    is_active: Optional[bool] = None


class RuleResponse(RuleBase):
    id: int
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analytics Schemas
class DashboardStats(BaseModel):
    total_calls: int
    analyzed_calls: int
    safe_calls: int
    spam_calls: int
    fraud_calls: int
    phishing_calls: int
    robocall_calls: int
    average_risk_score: float
    detection_rate: float


class TrendData(BaseModel):
    date: str
    total: int
    spam: int
    fraud: int
    phishing: int
    robocall: int
    average_risk: float


class AnalyticsDashboard(BaseModel):
    stats: DashboardStats
    recent_calls: List[CallResponse]
    trends: List[TrendData]
    top_fraud_indicators: List[Dict[str, Any]]
    risk_distribution: Dict[str, int]


# Real-time Schemas
class StreamChunk(BaseModel):
    """Real-time streaming chunk"""
    chunk_id: int
    audio_data: str  # Base64 encoded
    is_final: bool = False


class StreamResult(BaseModel):
    """Real-time streaming result"""
    chunk_id: int
    partial_transcript: str
    current_risk_score: float
    detected_flags: List[str]
    is_processing: bool


class AlertNotification(BaseModel):
    """Alert notification"""
    alert_id: str
    call_id: str
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    timestamp: datetime
    details: Dict[str, Any] = {}
