"""
Scam Detection Rules Model
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, JSON, Text, Enum
from datetime import datetime
import enum

from app.core.database import Base


class RuleType(str, enum.Enum):
    KEYWORD = "keyword"
    PATTERN = "pattern"
    BEHAVIORAL = "behavioral"
    ACOUSTIC = "acoustic"
    COMPOSITE = "composite"


class RuleCategory(str, enum.Enum):
    SPAM = "spam"
    FRAUD = "fraud"
    PHISHING = "phishing"
    ROBOCALL = "robocall"
    GENERAL = "general"


class DetectionRule(Base):
    """Scam detection rule model"""
    __tablename__ = "detection_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule configuration
    rule_type = Column(Enum(RuleType), default=RuleType.KEYWORD)
    category = Column(Enum(RuleCategory), default=RuleCategory.GENERAL)
    
    # Rule definition
    keywords: Column[JSON] = Column(JSON, default=lambda: [])  # type: ignore[assignment]
    patterns: Column[JSON] = Column(JSON, default=lambda: [])  # type: ignore[assignment]
    conditions: Column[JSON] = Column(JSON, default=lambda: {})  # type: ignore[assignment]
    
    # Scoring
    weight = Column(Float, default=1.0)
    min_confidence = Column(Float, default=0.5)
    
    # Multilingual support
    language = Column(String(10), default="en")
    translations: Column[JSON] = Column(JSON, default=lambda: {})  # type: ignore[assignment]
    
    # Status
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    
    # Metadata
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type.value if self.rule_type else None,  # type: ignore[truthy-bool]
            "category": self.category.value if self.category else None,  # type: ignore[truthy-bool]
            "keywords": self.keywords,
            "patterns": self.patterns,
            "conditions": self.conditions,
            "weight": self.weight,
            "language": self.language,
            "is_active": self.is_active,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None  # type: ignore[truthy-bool]
        }


class FraudPattern(Base):
    """Known fraud pattern for ML training"""
    __tablename__ = "fraud_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern_id = Column(String(50), unique=True, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(RuleCategory), default=RuleCategory.FRAUD)
    
    # Pattern data
    example_phrases = Column(JSON, default=list)
    indicators = Column(JSON, default=list)
    acoustic_signatures = Column(JSON, default=dict)
    behavioral_markers = Column(JSON, default=dict)
    
    # Statistics
    occurrences = Column(Integer, default=0)
    false_positive_rate = Column(Float, default=0)
    effectiveness = Column(Float, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
