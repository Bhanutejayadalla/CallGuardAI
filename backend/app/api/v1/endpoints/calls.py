"""
Calls History Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.schemas import CallResponse, CallDetailResponse, ClassificationType
from app.models.call import Call, CallClassification, CallStatus

router = APIRouter()


@router.get("/")
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
    # Build base query
    base_query = select(Call).where(Call.status == CallStatus.COMPLETED)
    
    # Apply filters
    if classification:
        base_query = base_query.where(Call.classification == CallClassification(classification))
    
    if min_risk_score is not None:
        base_query = base_query.where(Call.risk_score >= min_risk_score)
    
    if max_risk_score is not None:
        base_query = base_query.where(Call.risk_score <= max_risk_score)
    
    if start_date:
        base_query = base_query.where(Call.call_timestamp >= start_date)
    
    if end_date:
        base_query = base_query.where(Call.call_timestamp <= end_date)
    
    if search:
        search_term = f"%{search}%"
        base_query = base_query.where(
            (Call.transcript.ilike(search_term)) |
            (Call.caller_number.ilike(search_term)) |
            (Call.callee_number.ilike(search_term))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(base_query.alias())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Order and paginate
    query = base_query.order_by(desc(Call.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    calls = result.scalars().all()
    
    calls_data = [CallResponse(
        id=int(call.id),  # type: ignore[arg-type]
        call_id=str(call.call_id),  # type: ignore[arg-type]
        caller_number=str(call.caller_number) if call.caller_number else None,  # type: ignore[arg-type]
        callee_number=str(call.callee_number) if call.callee_number else None,  # type: ignore[arg-type]
        call_timestamp=call.call_timestamp,  # type: ignore[arg-type]
        status=call.status.value,
        classification=ClassificationType(call.classification.value) if call.classification else ClassificationType.UNKNOWN,  # type: ignore[truthy-bool]
        risk_score=float(call.risk_score or 0),  # type: ignore[arg-type]
        transcript=(str(call.transcript)[:200] + "...") if call.transcript and len(str(call.transcript)) > 200 else (str(call.transcript) if call.transcript else None),  # type: ignore[arg-type]
        ai_explanation=str(call.ai_explanation) if call.ai_explanation else None,  # type: ignore[arg-type]
        created_at=call.created_at,  # type: ignore[arg-type]
        analyzed_at=call.analyzed_at  # type: ignore[arg-type]
    ) for call in calls]
    
    return {
        "calls": calls_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }


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
        id=int(call.id),  # type: ignore[arg-type]
        call_id=str(call.call_id),  # type: ignore[arg-type]
        caller_number=str(call.caller_number) if call.caller_number else None,  # type: ignore[arg-type]
        callee_number=str(call.callee_number) if call.callee_number else None,  # type: ignore[arg-type]
        call_timestamp=call.call_timestamp,  # type: ignore[arg-type]
        status=call.status.value,
        classification=call.classification.value if call.classification else "unknown",  # type: ignore[truthy-bool]
        risk_score=float(call.risk_score or 0),  # type: ignore[arg-type]
        spam_score=float(call.spam_score or 0),  # type: ignore[arg-type]
        fraud_score=float(call.fraud_score or 0),  # type: ignore[arg-type]
        phishing_score=float(call.phishing_score or 0),  # type: ignore[arg-type]
        robocall_score=float(call.robocall_score or 0),  # type: ignore[arg-type]
        transcript=str(call.transcript) if call.transcript else None,  # type: ignore[arg-type]
        transcript_language=str(call.transcript_language),  # type: ignore[arg-type]
        transcript_confidence=float(call.transcript_confidence or 0),  # type: ignore[arg-type]
        suspicious_keywords=list(call.suspicious_keywords) if call.suspicious_keywords else [],  # type: ignore[arg-type]
        fraud_indicators=list(call.fraud_indicators) if call.fraud_indicators else [],  # type: ignore[arg-type]
        highlighted_phrases=list(call.highlighted_phrases) if call.highlighted_phrases else [],  # type: ignore[arg-type]
        voice_characteristics=dict(call.voice_characteristics) if call.voice_characteristics else {},  # type: ignore[arg-type]
        acoustic_features=dict(call.acoustic_features) if call.acoustic_features else {},  # type: ignore[arg-type]
        behavioral_patterns=dict(call.behavioral_patterns) if call.behavioral_patterns else {},  # type: ignore[arg-type]
        intent_analysis=dict(call.intent_analysis) if call.intent_analysis else {},  # type: ignore[arg-type]
        ai_explanation=str(call.ai_explanation) if call.ai_explanation else "",  # type: ignore[arg-type]
        confidence_score=float(call.confidence_score or 0),  # type: ignore[arg-type]
        duration_seconds=float(call.duration_seconds or 0),  # type: ignore[arg-type]
        created_at=call.created_at,  # type: ignore[arg-type]
        analyzed_at=call.analyzed_at  # type: ignore[arg-type]
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
        risk_score_val = float(call.risk_score or 0)  # type: ignore[arg-type]
        severity = "critical" if risk_score_val >= 90 else "high" if risk_score_val >= 80 else "medium"
        classification_val = call.classification.value if call.classification else "unknown"  # type: ignore[truthy-bool]
        alerts.append({
            "alert_id": f"alert_{call.call_id}",
            "call_id": call.call_id,
            "alert_type": classification_val,
            "severity": severity,
            "message": f"{classification_val.upper()} detected with {risk_score_val:.0f}% risk score",
            "risk_score": risk_score_val,
            "timestamp": call.created_at.isoformat(),  # type: ignore[union-attr]
            "caller_number": call.caller_number
        })
    
    return alerts
