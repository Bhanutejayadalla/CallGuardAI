"""
Analysis Endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import uuid
import os
import aiofiles
from datetime import datetime

from app.core.database import get_db
from app.api.schemas import AnalysisResult, CallCreate
from app.services.analysis_service import AnalysisService
from app.models.call import Call, CallStatus, CallClassification

router = APIRouter()


@router.post("/upload", response_model=AnalysisResult)
async def analyze_audio_upload(
    file: UploadFile = File(...),
    caller_number: str = None,
    callee_number: str = None,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an audio file for fraud analysis
    
    Supports: WAV, MP3, OGG, FLAC, M4A, MP4, WEBM, MKV, AVI, MOV formats
    Audio will be extracted from video files
    Max duration: 10 minutes
    """
    # Validate file type
    allowed_extensions = ['wav', 'mp3', 'ogg', 'flac', 'm4a', 'mp4', 'webm', 'mkv', 'avi', 'mov']
    file_ext = file.filename.split('.')[-1].lower() if file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique call ID
    call_id = f"call_{uuid.uuid4().hex[:12]}"
    
    # Save uploaded file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{call_id}.{file_ext}")
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"Audio file saved: {file_path}")
        
        # Create call record
        call = Call(
            call_id=call_id,
            caller_number=caller_number,
            callee_number=callee_number,
            audio_file_path=file_path,
            audio_format=file_ext,
            status=CallStatus.PROCESSING,
            call_timestamp=datetime.utcnow()
        )
        db.add(call)
        await db.commit()
        await db.refresh(call)
        
        # Run analysis
        analysis_service = AnalysisService()
        result = await analysis_service.analyze_audio(file_path, call_id)
        
        # Update call record with results
        call.status = CallStatus.COMPLETED
        call.transcript = result.transcript
        call.transcript_language = result.transcript_language
        call.transcript_confidence = result.transcript_confidence
        call.classification = CallClassification(result.classification)
        call.risk_score = result.risk_score
        call.spam_score = result.spam_score
        call.fraud_score = result.fraud_score
        call.phishing_score = result.phishing_score
        call.robocall_score = result.robocall_score
        call.suspicious_keywords = result.suspicious_keywords
        call.fraud_indicators = result.fraud_indicators
        call.highlighted_phrases = result.highlighted_phrases
        call.acoustic_features = result.acoustic_features
        call.voice_characteristics = result.voice_characteristics
        call.behavioral_patterns = result.behavioral_patterns
        call.intent_analysis = result.intent_analysis
        call.ai_explanation = result.ai_explanation
        call.confidence_score = result.confidence_score
        call.analyzed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Analysis completed for call {call_id}: {result.classification} (Risk: {result.risk_score})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}")
        # Update call status to failed
        call.status = CallStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/text", response_model=AnalysisResult)
async def analyze_text(
    text: str,
    caller_number: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze text transcript directly (without audio)
    """
    call_id = f"text_{uuid.uuid4().hex[:12]}"
    
    # Create call record
    call = Call(
        call_id=call_id,
        caller_number=caller_number,
        transcript=text,
        status=CallStatus.PROCESSING,
        call_timestamp=datetime.utcnow()
    )
    db.add(call)
    await db.commit()
    await db.refresh(call)
    
    try:
        # Run text-only analysis
        analysis_service = AnalysisService()
        result = await analysis_service.analyze_text(text, call_id)
        
        # Update call record
        call.status = CallStatus.COMPLETED
        call.classification = CallClassification(result.classification)
        call.risk_score = result.risk_score
        call.spam_score = result.spam_score
        call.fraud_score = result.fraud_score
        call.phishing_score = result.phishing_score
        call.robocall_score = result.robocall_score
        call.suspicious_keywords = result.suspicious_keywords
        call.fraud_indicators = result.fraud_indicators
        call.highlighted_phrases = result.highlighted_phrases
        call.intent_analysis = result.intent_analysis
        call.ai_explanation = result.ai_explanation
        call.confidence_score = result.confidence_score
        call.analyzed_at = datetime.utcnow()
        
        await db.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        call.status = CallStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/status/{call_id}")
async def get_analysis_status(
    call_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the status of an ongoing analysis"""
    from sqlalchemy import select
    
    result = await db.execute(select(Call).where(Call.call_id == call_id))
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return {
        "call_id": call.call_id,
        "status": call.status.value,
        "classification": call.classification.value if call.classification else None,
        "risk_score": call.risk_score,
        "progress": 100 if call.status == CallStatus.COMPLETED else 50
    }
