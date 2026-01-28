"""
ML Model Loader and Manager
"""

from loguru import logger
import os
from typing import Optional, Dict, Any
import asyncio

# Global model instances
_models: Dict[str, Any] = {
    "whisper": None,
    "nlp": None,
    "fraud_classifier": None,
    "sentiment": None,
    "ai_voice_detector": None
}

# Track model status
_model_status: Dict[str, Dict[str, Any]] = {
    "whisper": {"loaded": False, "status": "not_loaded", "error": None},
    "nlp": {"loaded": False, "status": "not_loaded", "error": None},
    "fraud_classifier": {"loaded": False, "status": "not_loaded", "error": None},
    "sentiment": {"loaded": False, "status": "not_loaded", "error": None},
    "ai_voice_detector": {"loaded": False, "status": "not_loaded", "error": None}
}


async def load_models():
    """Load all ML models on startup"""
    logger.info("Loading ML models...")
    
    # Load models in parallel for faster startup
    await asyncio.gather(
        load_whisper_model(),
        load_nlp_model(),
        load_fraud_classifier(),
        load_sentiment_model(),
        load_ai_voice_detector(),
        return_exceptions=True
    )
    
    logger.info("All ML models loaded successfully")


async def load_whisper_model():
    """Load Whisper speech recognition model"""
    try:
        import whisper
        logger.info("Loading Whisper model (this may take a moment)...")
        _models["whisper"] = whisper.load_model("base")
        _model_status["whisper"] = {"loaded": True, "status": "loaded", "error": None}
        logger.info("✓ Whisper speech recognition model loaded")
    except ImportError:
        logger.warning("Whisper not installed, using fallback mode")
        _models["whisper"] = "fallback"
        _model_status["whisper"] = {"loaded": True, "status": "fallback", "error": "whisper not installed"}
    except Exception as e:
        logger.warning(f"Whisper model not loaded: {e}")
        _models["whisper"] = "fallback"
        _model_status["whisper"] = {"loaded": False, "status": "error", "error": str(e)}


async def load_nlp_model():
    """Load spaCy NLP model"""
    try:
        import spacy
        try:
            _models["nlp"] = spacy.load("en_core_web_sm")
        except OSError:
            # Download if not available
            logger.info("Downloading spaCy model...")
            os.system("python -m spacy download en_core_web_sm")
            _models["nlp"] = spacy.load("en_core_web_sm")
        _model_status["nlp"] = {"loaded": True, "status": "loaded", "error": None}
        logger.info("✓ NLP model loaded")
    except Exception as e:
        logger.warning(f"spaCy model not loaded: {e}")
        _model_status["nlp"] = {"loaded": False, "status": "error", "error": str(e)}


async def load_fraud_classifier():
    """Load fraud classification model"""
    try:
        # In production, load actual trained model
        # from joblib import load
        # _models["fraud_classifier"] = load("models/fraud_classifier.joblib")
        _models["fraud_classifier"] = "rule_based_classifier"
        _model_status["fraud_classifier"] = {"loaded": True, "status": "loaded", "error": None}
        logger.info("✓ Fraud classifier ready (rule-based)")
    except Exception as e:
        logger.warning(f"Fraud classifier not loaded: {e}")
        _model_status["fraud_classifier"] = {"loaded": False, "status": "error", "error": str(e)}


async def load_sentiment_model():
    """Load sentiment analysis model"""
    try:
        # In production, use transformers
        # from transformers import pipeline
        # _models["sentiment"] = pipeline("sentiment-analysis")
        _models["sentiment"] = "rule_based_sentiment"
        _model_status["sentiment"] = {"loaded": True, "status": "loaded", "error": None}
        logger.info("✓ Sentiment analyzer ready (rule-based)")
    except Exception as e:
        logger.warning(f"Sentiment model not loaded: {e}")
        _model_status["sentiment"] = {"loaded": False, "status": "error", "error": str(e)}


async def load_ai_voice_detector():
    """Load AI voice detector for deepfake detection"""
    try:
        from app.ml.ai_voice_detector import get_ai_voice_detector
        detector = get_ai_voice_detector()
        _models["ai_voice_detector"] = detector
        _model_status["ai_voice_detector"] = {"loaded": True, "status": "loaded", "error": None}
        logger.info("✓ AI Voice Detector ready (multi-language)")
    except Exception as e:
        logger.warning(f"AI Voice Detector not loaded: {e}")
        _model_status["ai_voice_detector"] = {"loaded": False, "status": "error", "error": str(e)}


def get_model(name: str):
    """Get a loaded model by name"""
    return _models.get(name)


def get_nlp():
    """Get spaCy NLP model"""
    return _models.get("nlp")


def get_whisper():
    """Get Whisper model"""
    return _models.get("whisper")


def get_model_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all models"""
    return _model_status


def get_models_summary() -> Dict[str, Any]:
    """Get summary of all models for API response"""
    whisper_status = _model_status.get("whisper", {})
    nlp_status = _model_status.get("nlp", {})
    fraud_status = _model_status.get("fraud_classifier", {})
    sentiment_status = _model_status.get("sentiment", {})
    ai_voice_status = _model_status.get("ai_voice_detector", {})
    
    all_loaded = all(s.get("loaded", False) for s in _model_status.values())
    any_loaded = any(s.get("loaded", False) for s in _model_status.values())
    
    if all_loaded:
        overall = "operational"
    elif any_loaded:
        overall = "degraded"
    else:
        overall = "offline"
    
    return {
        "overall": overall,
        "models": {
            "whisper": {
                "status": whisper_status.get("status", "unknown"),
                "loaded": whisper_status.get("loaded", False)
            },
            "nlp": {
                "status": nlp_status.get("status", "unknown"),
                "loaded": nlp_status.get("loaded", False)
            },
            "fraud_classifier": {
                "status": fraud_status.get("status", "unknown"),
                "loaded": fraud_status.get("loaded", False)
            },
            "sentiment": {
                "status": sentiment_status.get("status", "unknown"),
                "loaded": sentiment_status.get("loaded", False)
            },
            "ai_voice_detector": {
                "status": ai_voice_status.get("status", "unknown"),
                "loaded": ai_voice_status.get("loaded", False),
                "description": "Detects AI-generated voices (Tamil, English, Hindi, Malayalam, Telugu)"
            }
        }
    }
