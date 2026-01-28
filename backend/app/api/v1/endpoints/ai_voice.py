"""
AI Voice Detection Endpoints
Detect AI-generated vs Human voices in audio samples
Supports: Tamil, English, Hindi, Malayalam, Telugu
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from loguru import logger
import uuid

from app.core.database import get_db
from app.ml.ai_voice_detector import get_ai_voice_detector, LANGUAGE_NAMES


router = APIRouter()


# ===== Request/Response Schemas =====

class AIVoiceDetectionRequest(BaseModel):
    """Request schema for AI voice detection API"""
    audio: str = Field(
        ..., 
        description="Base64-encoded MP3 audio data",
        min_length=100
    )
    language: Optional[str] = Field(
        None,
        description="Language code (ta=Tamil, en=English, hi=Hindi, ml=Malayalam, te=Telugu). Auto-detected if not provided."
    )


class AnalysisDetails(BaseModel):
    """Detailed analysis breakdown"""
    features_analyzed: List[str] = []
    ai_indicators: List[str] = []
    human_indicators: List[str] = []
    spectral_analysis: dict = {}
    temporal_analysis: dict = {}
    prosody_analysis: dict = {}


class AIVoiceDetectionResponse(BaseModel):
    """Response schema for AI voice detection API"""
    classification: str = Field(
        ..., 
        description="Classification result: 'ai_generated', 'human', or 'uncertain'"
    )
    is_ai_generated: Optional[bool] = Field(
        ..., 
        description="True if AI-generated, False if human, None if uncertain/error"
    )
    confidence_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Confidence score between 0 and 1"
    )
    confidence_percentage: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Confidence as percentage (0-100)"
    )
    language: str = Field(
        ..., 
        description="Detected or specified language code"
    )
    language_name: str = Field(
        ..., 
        description="Full language name"
    )
    explanation: str = Field(
        ..., 
        description="Human-readable explanation of the classification"
    )
    analysis_details: AnalysisDetails = Field(
        default_factory=AnalysisDetails,
        description="Detailed analysis breakdown"
    )
    supported_languages: List[str] = Field(
        default_factory=list,
        description="List of supported languages"
    )
    status: str = Field(
        ..., 
        description="Status: 'success' or 'error'"
    )
    request_id: Optional[str] = Field(
        None,
        description="Unique request identifier"
    )
    processed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the request was processed"
    )


class SupportedLanguagesResponse(BaseModel):
    """Response for listing supported languages"""
    languages: dict = Field(
        ..., 
        description="Dictionary of language codes to names"
    )
    count: int = Field(..., description="Number of supported languages")


# ===== API Endpoints =====

@router.post(
    "/detect",
    response_model=AIVoiceDetectionResponse,
    summary="Detect AI-Generated Voice",
    description="""
    Analyze an audio sample to determine if it is AI-generated or human-generated.
    
    **Supported Languages:** Tamil, English, Hindi, Malayalam, Telugu
    
    **Input:** Base64-encoded MP3 audio
    
    **Returns:** Classification with confidence score and detailed explanation
    """
)
async def detect_ai_voice(
    request: AIVoiceDetectionRequest,
    db: AsyncSession = Depends(get_db)
) -> AIVoiceDetectionResponse:
    """
    Main endpoint for AI voice detection.
    
    Accepts Base64-encoded MP3 audio and returns classification result.
    """
    request_id = f"ai_detect_{uuid.uuid4().hex[:12]}"
    logger.info(f"[{request_id}] Starting AI voice detection")
    
    try:
        # Validate language if provided
        valid_languages = ["ta", "en", "hi", "ml", "te"]
        if request.language and request.language not in valid_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language code. Supported: {', '.join(valid_languages)} "
                       f"(Tamil, English, Hindi, Malayalam, Telugu)"
            )
        
        # Get detector
        detector = get_ai_voice_detector()
        
        # Run detection
        result = await detector.detect_from_base64(
            audio_base64=request.audio,
            language=request.language
        )
        
        # Check for errors
        if result.get("status") == "error":
            logger.error(f"[{request_id}] Detection error: {result.get('error')}")
            raise HTTPException(
                status_code=400,
                detail=result.get("explanation", "Detection failed")
            )
        
        logger.info(
            f"[{request_id}] Detection complete: {result['classification']} "
            f"(confidence: {result['confidence_percentage']}%)"
        )
        
        # Build response
        return AIVoiceDetectionResponse(
            classification=result["classification"],
            is_ai_generated=result["is_ai_generated"],
            confidence_score=result["confidence_score"],
            confidence_percentage=result["confidence_percentage"],
            language=result["language"],
            language_name=result["language_name"],
            explanation=result["explanation"],
            analysis_details=AnalysisDetails(**result.get("analysis_details", {})),
            supported_languages=result.get("supported_languages", []),
            status="success",
            request_id=request_id,
            processed_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/languages",
    response_model=SupportedLanguagesResponse,
    summary="Get Supported Languages",
    description="Returns list of supported languages for AI voice detection"
)
async def get_supported_languages() -> SupportedLanguagesResponse:
    """Get list of supported languages"""
    return SupportedLanguagesResponse(
        languages=LANGUAGE_NAMES,
        count=len(LANGUAGE_NAMES)
    )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if AI voice detection service is operational"
)
async def health_check():
    """Health check endpoint"""
    detector = get_ai_voice_detector()
    return {
        "status": "healthy",
        "service": "ai-voice-detection",
        "model_loaded": detector.is_loaded(),
        "supported_languages": list(LANGUAGE_NAMES.values()),
        "timestamp": datetime.utcnow().isoformat()
    }
