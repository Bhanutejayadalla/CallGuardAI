"""
ML Module initialization
"""

from app.ml.model_loader import load_models, get_model, get_nlp
from app.ml.fraud_detector import FraudDetector
from app.ml.speech_to_text import SpeechToText, AudioProcessor
from app.ml.nlp_analyzer import NLPAnalyzer

__all__ = [
    "load_models",
    "get_model", 
    "get_nlp",
    "FraudDetector",
    "SpeechToText",
    "AudioProcessor",
    "NLPAnalyzer"
]
