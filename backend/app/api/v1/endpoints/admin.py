"""
Admin Panel Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional, cast
from datetime import datetime

from app.core.database import get_db
from app.api.schemas import RuleCreate, RuleUpdate, RuleResponse
from app.models.rule import DetectionRule, FraudPattern, RuleType, RuleCategory
from app.models.call import Call, CallClassification, CallStatus
from app.ml.model_loader import get_models_summary

router = APIRouter()


# ============ Detection Rules Management ============

@router.get("/rules", response_model=List[RuleResponse])
async def get_rules(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all detection rules"""
    query = select(DetectionRule)
    
    if category:
        query = query.where(DetectionRule.category == RuleCategory(category))
    
    if is_active is not None:
        query = query.where(DetectionRule.is_active == is_active)
    
    query = query.order_by(DetectionRule.priority.desc(), DetectionRule.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    rules = result.scalars().all()
    
    return [RuleResponse(
        id=int(rule.id),  # type: ignore[arg-type]
        name=str(rule.name),  # type: ignore[arg-type]
        description=str(rule.description) if rule.description else None,  # type: ignore[arg-type]
        rule_type=rule.rule_type.value,
        category=rule.category.value,
        keywords=list(rule.keywords) if rule.keywords else [],  # type: ignore[arg-type]
        patterns=list(rule.patterns) if rule.patterns else [],  # type: ignore[arg-type]
        weight=float(rule.weight),  # type: ignore[arg-type]
        language=str(rule.language),  # type: ignore[arg-type]
        is_active=bool(rule.is_active),  # type: ignore[arg-type]
        priority=int(rule.priority),  # type: ignore[arg-type]
        created_at=rule.created_at  # type: ignore[arg-type]
    ) for rule in rules]


@router.post("/rules", response_model=RuleResponse)
async def create_rule(
    rule_data: RuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new detection rule"""
    rule = DetectionRule(
        name=rule_data.name,
        description=rule_data.description,
        rule_type=RuleType(rule_data.rule_type),
        category=RuleCategory(rule_data.category),
        keywords=rule_data.keywords,
        patterns=rule_data.patterns,
        weight=rule_data.weight,
        language=rule_data.language,
        is_active=rule_data.is_active
    )
    
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    
    return RuleResponse(
        id=int(rule.id),  # type: ignore[arg-type]
        name=str(rule.name),  # type: ignore[arg-type]
        description=str(rule.description) if rule.description else None,  # type: ignore[arg-type]
        rule_type=rule.rule_type.value,
        category=rule.category.value,
        keywords=list(rule.keywords) if rule.keywords else [],  # type: ignore[arg-type]
        patterns=list(rule.patterns) if rule.patterns else [],  # type: ignore[arg-type]
        weight=float(rule.weight),  # type: ignore[arg-type]
        language=str(rule.language),  # type: ignore[arg-type]
        is_active=bool(rule.is_active),  # type: ignore[arg-type]
        priority=int(rule.priority),  # type: ignore[arg-type]
        created_at=rule.created_at  # type: ignore[arg-type]
    )


@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: int,
    rule_data: RuleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing detection rule"""
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update fields
    if rule_data.name is not None:
        rule.name = rule_data.name  # type: ignore[assignment]
    if rule_data.description is not None:
        rule.description = rule_data.description  # type: ignore[assignment]
    if rule_data.keywords is not None:
        rule.keywords = rule_data.keywords  # type: ignore[assignment]
    if rule_data.patterns is not None:
        rule.patterns = rule_data.patterns  # type: ignore[assignment]
    if rule_data.weight is not None:
        rule.weight = rule_data.weight  # type: ignore[assignment]
    if rule_data.is_active is not None:
        rule.is_active = rule_data.is_active  # type: ignore[assignment]
    
    rule.updated_at = datetime.utcnow()  # type: ignore[assignment]
    
    await db.commit()
    await db.refresh(rule)
    
    return RuleResponse(
        id=int(rule.id),  # type: ignore[arg-type]
        name=str(rule.name),  # type: ignore[arg-type]
        description=str(rule.description) if rule.description else None,  # type: ignore[arg-type]
        rule_type=rule.rule_type.value,
        category=rule.category.value,
        keywords=list(rule.keywords) if rule.keywords else [],  # type: ignore[arg-type]
        patterns=list(rule.patterns) if rule.patterns else [],  # type: ignore[arg-type]
        weight=float(rule.weight),  # type: ignore[arg-type]
        language=str(rule.language),  # type: ignore[arg-type]
        is_active=bool(rule.is_active),  # type: ignore[arg-type]
        priority=int(rule.priority),  # type: ignore[arg-type]
        created_at=rule.created_at  # type: ignore[arg-type]
    )


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a detection rule"""
    result = await db.execute(select(DetectionRule).where(DetectionRule.id == rule_id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    await db.delete(rule)
    await db.commit()
    
    return {"message": "Rule deleted successfully", "id": rule_id}


# ============ System Statistics ============

@router.get("/stats")
async def get_system_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get system-wide statistics for admin"""
    # Total calls
    total_result = await db.execute(select(func.count(Call.id)))
    total_calls = total_result.scalar()
    
    # Calls by status
    status_counts = {}
    for status in CallStatus:
        result = await db.execute(
            select(func.count(Call.id)).where(Call.status == status)
        )
        status_counts[status.value] = result.scalar()
    
    # Classification distribution
    classification_counts = {}
    for cls in CallClassification:
        result = await db.execute(
            select(func.count(Call.id)).where(Call.classification == cls)
        )
        classification_counts[cls.value] = result.scalar()
    
    # Active rules count
    rules_result = await db.execute(
        select(func.count(DetectionRule.id)).where(DetectionRule.is_active == True)
    )
    active_rules = rules_result.scalar()
    
    # Average processing metrics (simulated for now)
    avg_risk_result = await db.execute(
        select(func.avg(Call.risk_score)).where(Call.status == CallStatus.COMPLETED)
    )
    avg_risk = avg_risk_result.scalar() or 0
    
    return {
        "total_calls": total_calls,
        "status_breakdown": status_counts,
        "classification_breakdown": classification_counts,
        "active_rules": active_rules,
        "average_risk_score": round(avg_risk, 2),
        "system_health": "healthy",
        "ml_models": get_models_summary(),
        "last_updated": datetime.utcnow().isoformat()
    }


# ============ Default Rules Initialization ============

@router.post("/rules/init-defaults")
async def initialize_default_rules(
    db: AsyncSession = Depends(get_db)
):
    """Initialize default detection rules"""
    
    default_rules = [
        # Fraud Keywords - English
        {
            "name": "Fraud Keywords - Bank/Finance",
            "description": "Common fraud keywords related to banking and finance",
            "rule_type": "keyword",
            "category": "fraud",
            "keywords": [
                "bank account suspended", "verify your account", "security breach",
                "unauthorized transaction", "confirm your identity", "account locked",
                "wire transfer", "send money immediately", "gift cards", "bitcoin payment",
                "western union", "money gram", "account compromised"
            ],
            "weight": 1.5,
            "language": "en"
        },
        # Phishing Keywords
        {
            "name": "Phishing Keywords",
            "description": "Keywords commonly used in phishing attempts",
            "rule_type": "keyword",
            "category": "phishing",
            "keywords": [
                "click the link", "verify your password", "update your information",
                "social security number", "credit card number", "CVV", "OTP",
                "one time password", "login credentials", "reset your password",
                "confirm your details", "personal information required"
            ],
            "weight": 1.4,
            "language": "en"
        },
        # Spam Keywords
        {
            "name": "Spam Keywords - Marketing",
            "description": "Common spam and unwanted marketing keywords",
            "rule_type": "keyword",
            "category": "spam",
            "keywords": [
                "congratulations you won", "free offer", "limited time only",
                "act now", "call back immediately", "exclusive deal",
                "you have been selected", "prize winner", "lottery winner",
                "claim your reward", "special promotion", "discount offer"
            ],
            "weight": 1.0,
            "language": "en"
        },
        # Robocall Detection
        {
            "name": "Robocall Indicators",
            "description": "Patterns indicating automated robocalls",
            "rule_type": "keyword",
            "category": "robocall",
            "keywords": [
                "press 1 to", "press 2 to", "this is an automated message",
                "please hold for", "your call is important", "do not hang up",
                "stay on the line", "recording", "pre-recorded message"
            ],
            "weight": 1.2,
            "language": "en"
        },
        # Hindi Fraud Keywords
        {
            "name": "Fraud Keywords - Hindi",
            "description": "Hindi fraud keywords",
            "rule_type": "keyword",
            "category": "fraud",
            "keywords": [
                "aapka khata", "bank se bol raha", "OTP batao", "paise transfer",
                "lottery jeeta", "KYC update", "aadhar link", "pan card",
                "turant bhejo", "account band", "verify karo"
            ],
            "weight": 1.5,
            "language": "hi"
        },
        # Urgency Patterns
        {
            "name": "Urgency Indicators",
            "description": "Phrases creating false urgency",
            "rule_type": "pattern",
            "category": "general",
            "keywords": [
                "immediately", "urgent", "right now", "within 24 hours",
                "last chance", "final warning", "time sensitive", "don't delay",
                "expires today", "act fast", "hurry", "emergency"
            ],
            "weight": 1.3,
            "language": "en"
        }
    ]
    
    created_count = 0
    for rule_data in default_rules:
        # Check if rule already exists
        existing = await db.execute(
            select(DetectionRule).where(DetectionRule.name == rule_data["name"])
        )
        if not existing.scalar_one_or_none():
            rule = DetectionRule(
                name=rule_data["name"],
                description=rule_data["description"],
                rule_type=RuleType(rule_data["rule_type"]),
                category=RuleCategory(rule_data["category"]),
                keywords=rule_data["keywords"],
                weight=rule_data["weight"],
                language=rule_data["language"],
                is_active=True
            )
            db.add(rule)
            created_count += 1
    
    await db.commit()
    
    return {
        "message": f"Initialized {created_count} default rules",
        "total_rules": created_count
    }
