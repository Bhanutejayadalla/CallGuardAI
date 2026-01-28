"""
Calls History Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.schemas import CallResponse, CallDetailResponse
from app.models.call import Call, CallClassification, CallStatus

router = APIRouter()


@router.get("/", response_model=List[CallResponse])
async def get_calls(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    classification: Optional[str] = None,
    min_risk_score: Optional[float] = None,
    max_risk_score: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get call history with filtering and pagination
    """
    query = select(Call).where(Call.status == CallStatus.COMPLETED)
    
    # Apply filters
    if classification:
        query = query.where(Call.classification == CallClassification(classification))
    
    if min_risk_score is not None:
        query = query.where(Call.risk_score >= min_risk_score)
    
    if max_risk_score is not None:
        query = query.where(Call.risk_score <= max_risk_score)
    
    if start_date:
        query = query.where(Call.call_timestamp >= start_date)
    
    if end_date:
        query = query.where(Call.call_timestamp <= end_date)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Call.transcript.ilike(search_term)) |
            (Call.caller_number.ilike(search_term)) |
            (Call.callee_number.ilike(search_term))
        )
    
    # Order and paginate
    query = query.order_by(desc(Call.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    calls = result.scalars().all()
    
    return [CallResponse(
        id=call.id,
        call_id=call.call_id,
        caller_number=call.caller_number,
        callee_number=call.callee_number,
        call_timestamp=call.call_timestamp,
        status=call.status.value,
        classification=call.classification.value,
        risk_score=call.risk_score,
        transcript=call.transcript[:200] + "..." if call.transcript and len(call.transcript) > 200 else call.transcript,
        ai_explanation=call.ai_explanation,
        created_at=call.created_at,
        analyzed_at=call.analyzed_at
    ) for call in calls]


@router.get("/count")
async def get_calls_count(
    classification: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get total count of calls"""
    query = select(func.count(Call.id)).where(Call.status == CallStatus.COMPLETED)
    
    if classification:
        query = query.where(Call.classification == CallClassification(classification))
    
    result = await db.execute(query)
    count = result.scalar()
    
    return {"count": count}


@router.get("/{call_id}", response_model=CallDetailResponse)
async def get_call_detail(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed analysis results for a specific call
    """
    result = await db.execute(select(Call).where(Call.call_id == call_id))
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return CallDetailResponse(
        id=call.id,
        call_id=call.call_id,
        caller_number=call.caller_number,
        callee_number=call.callee_number,
        call_timestamp=call.call_timestamp,
        status=call.status.value,
        classification=call.classification.value if call.classification else "unknown",
        risk_score=call.risk_score,
        spam_score=call.spam_score,
        fraud_score=call.fraud_score,
        phishing_score=call.phishing_score,
        robocall_score=call.robocall_score,
        transcript=call.transcript,
        transcript_language=call.transcript_language,
        transcript_confidence=call.transcript_confidence,
        suspicious_keywords=call.suspicious_keywords or [],
        fraud_indicators=call.fraud_indicators or [],
        highlighted_phrases=call.highlighted_phrases or [],
        voice_characteristics=call.voice_characteristics or {},
        acoustic_features=call.acoustic_features or {},
        behavioral_patterns=call.behavioral_patterns or {},
        intent_analysis=call.intent_analysis or {},
        ai_explanation=call.ai_explanation or "",
        confidence_score=call.confidence_score,
        duration_seconds=call.duration_seconds,
        created_at=call.created_at,
        analyzed_at=call.analyzed_at
    )


@router.delete("/{call_id}")
async def delete_call(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a call record"""
    result = await db.execute(select(Call).where(Call.call_id == call_id))
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    await db.delete(call)
    await db.commit()
    
    return {"message": "Call deleted successfully", "call_id": call_id}


@router.get("/recent/alerts")
async def get_recent_alerts(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get recent high-risk calls as alerts"""
    query = (
        select(Call)
        .where(Call.status == CallStatus.COMPLETED)
        .where(Call.risk_score >= 70)
        .order_by(desc(Call.created_at))
        .limit(limit)
    )
    
    result = await db.execute(query)
    calls = result.scalars().all()
    
    alerts = []
    for call in calls:
        severity = "critical" if call.risk_score >= 90 else "high" if call.risk_score >= 80 else "medium"
        alerts.append({
            "alert_id": f"alert_{call.call_id}",
            "call_id": call.call_id,
            "alert_type": call.classification.value if call.classification else "unknown",
            "severity": severity,
            "message": f"{call.classification.value.upper()} detected with {call.risk_score:.0f}% risk score",
            "risk_score": call.risk_score,
            "timestamp": call.created_at.isoformat(),
            "caller_number": call.caller_number
        })
    
    return alerts
