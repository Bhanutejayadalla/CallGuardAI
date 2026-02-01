"""
Analytics Endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.database import get_db
from app.api.schemas import DashboardStats, TrendData, AnalyticsDashboard
from app.models.call import Call, CallClassification, CallStatus

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive dashboard analytics
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get total counts
    base_query = select(Call).where(
        and_(
            Call.status == CallStatus.COMPLETED,
            Call.created_at >= start_date
        )
    )
    
    result = await db.execute(base_query)
    calls = result.scalars().all()
    
    # Calculate statistics
    total_calls = len(calls)
    
    classification_counts = defaultdict(int)
    risk_distribution = defaultdict(int)
    total_risk_score = 0
    
    for call in calls:
        if call.classification:  # type: ignore[truthy-bool]
            classification_counts[call.classification.value] += 1
        
        # Risk distribution buckets
        risk_score = float(call.risk_score or 0)  # type: ignore[arg-type]
        if risk_score < 20:
            risk_distribution["0-20"] += 1
        elif risk_score < 40:
            risk_distribution["20-40"] += 1
        elif risk_score < 60:
            risk_distribution["40-60"] += 1
        elif risk_score < 80:
            risk_distribution["60-80"] += 1
        else:
            risk_distribution["80-100"] += 1
        
        total_risk_score += risk_score
    
    avg_risk_score = total_risk_score / total_calls if total_calls > 0 else 0
    
    # Detection rate (non-safe calls)
    detected_calls = sum(
        count for cls, count in classification_counts.items() 
        if cls != "safe" and cls != "unknown"
    )
    detection_rate = (detected_calls / total_calls * 100) if total_calls > 0 else 0
    
    stats = {
        "total_calls": total_calls,
        "analyzed_calls": total_calls,
        "safe_calls": classification_counts.get("safe", 0),
        "spam_calls": classification_counts.get("spam", 0),
        "fraud_calls": classification_counts.get("fraud", 0),
        "phishing_calls": classification_counts.get("phishing", 0),
        "robocall_calls": classification_counts.get("robocall", 0),
        "average_risk_score": round(avg_risk_score, 2),
        "detection_rate": round(detection_rate, 2)
    }
    
    # Get recent calls
    recent_result = await db.execute(
        select(Call)
        .where(Call.status == CallStatus.COMPLETED)
        .order_by(desc(Call.created_at))
        .limit(10)
    )
    recent_calls = recent_result.scalars().all()
    
    recent_calls_data = [{
        "id": call.id,
        "call_id": call.call_id,
        "caller_number": call.caller_number,
        "classification": call.classification.value if call.classification else "unknown",  # type: ignore[truthy-bool]
        "risk_score": call.risk_score,
        "created_at": call.created_at.isoformat()  # type: ignore[union-attr]
    } for call in recent_calls]
    
    # Get top fraud indicators
    fraud_indicator_counts: defaultdict[str, int] = defaultdict(int)
    for call in calls:
        indicators = call.fraud_indicators  # type: ignore[assignment]
        if indicators:  # type: ignore[truthy-bool]
            for indicator in indicators:
                if isinstance(indicator, dict):
                    fraud_indicator_counts[indicator.get("type", "unknown")] += 1
                else:
                    fraud_indicator_counts[str(indicator)] += 1
    
    top_indicators = [
        {"indicator": k, "count": v}
        for k, v in sorted(fraud_indicator_counts.items(), key=lambda x: -x[1])[:10]
    ]
    
    return {
        "stats": stats,
        "recent_calls": recent_calls_data,
        "risk_distribution": dict(risk_distribution),
        "top_fraud_indicators": top_indicators,
        "classification_breakdown": dict(classification_counts)
    }


@router.get("/trends")
async def get_trends(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    Get fraud trends over time
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    result = await db.execute(
        select(Call)
        .where(
            and_(
                Call.status == CallStatus.COMPLETED,
                Call.created_at >= start_date
            )
        )
        .order_by(Call.created_at)
    )
    calls = result.scalars().all()
    
    # Group by date
    daily_data = defaultdict(lambda: {
        "total": 0, "spam": 0, "fraud": 0, 
        "phishing": 0, "robocall": 0, "safe": 0,
        "risk_sum": 0
    })
    
    for call in calls:
        date_key = call.created_at.strftime("%Y-%m-%d")  # type: ignore[union-attr]
        daily_data[date_key]["total"] += 1
        daily_data[date_key]["risk_sum"] += float(call.risk_score or 0)  # type: ignore[arg-type]
        
        if call.classification:  # type: ignore[truthy-bool]
            cls = call.classification.value
            if cls in daily_data[date_key]:
                daily_data[date_key][cls] += 1
    
    trends = []
    current_date = start_date
    while current_date <= end_date:
        date_key = current_date.strftime("%Y-%m-%d")
        data = daily_data[date_key]
        
        trends.append({
            "date": date_key,
            "total": data["total"],
            "spam": data["spam"],
            "fraud": data["fraud"],
            "phishing": data["phishing"],
            "robocall": data["robocall"],
            "safe": data["safe"],
            "average_risk": round(data["risk_sum"] / data["total"], 2) if data["total"] > 0 else 0
        })
        
        current_date += timedelta(days=1)
    
    return {"trends": trends}


@router.get("/heatmap")
async def get_heatmap(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Get hourly heatmap data for call activity
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(Call)
        .where(
            and_(
                Call.status == CallStatus.COMPLETED,
                Call.created_at >= start_date
            )
        )
    )
    calls = result.scalars().all()
    
    # Create hour x day matrix
    heatmap = defaultdict(lambda: defaultdict(int))
    
    for call in calls:
        day = call.created_at.strftime("%A")
        hour = call.created_at.hour
        heatmap[day][hour] += 1
    
    return {"heatmap": dict(heatmap)}


@router.get("/keywords")
async def get_top_keywords(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most frequently detected suspicious keywords
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(Call)
        .where(
            and_(
                Call.status == CallStatus.COMPLETED,
                Call.created_at >= start_date,
                Call.risk_score >= 50
            )
        )
    )
    calls = result.scalars().all()
    
    keyword_counts: defaultdict[str, int] = defaultdict(int)
    
    for call in calls:
        keywords = call.suspicious_keywords  # type: ignore[assignment]
        if keywords:  # type: ignore[truthy-bool]
            for keyword in keywords:
                keyword_counts[str(keyword).lower()] += 1
    
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: -x[1])[:limit]
    
    return {
        "keywords": [
            {"keyword": k, "count": v, "percentage": round(v / len(calls) * 100, 2) if calls else 0}
            for k, v in sorted_keywords
        ]
    }


@router.get("/classification-stats")
async def get_classification_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed classification statistics
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(Call)
        .where(
            and_(
                Call.status == CallStatus.COMPLETED,
                Call.created_at >= start_date
            )
        )
    )
    calls = result.scalars().all()
    
    stats = {}
    for cls in CallClassification:
        cls_calls = [c for c in calls if c.classification == cls]  # type: ignore[truthy-bool]
        if cls_calls:
            stats[cls.value] = {
                "count": len(cls_calls),
                "avg_risk_score": round(sum(float(c.risk_score or 0) for c in cls_calls) / len(cls_calls), 2),  # type: ignore[arg-type]
                "avg_confidence": round(sum(float(c.confidence_score or 0) for c in cls_calls) / len(cls_calls), 2),  # type: ignore[arg-type]
                "percentage": round(len(cls_calls) / len(calls) * 100, 2) if calls else 0
            }
    
    return {"classification_stats": stats}
