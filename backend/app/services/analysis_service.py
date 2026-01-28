"""
Analysis Service
Orchestrates the complete call analysis pipeline
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
import asyncio
import numpy as np

from app.api.schemas import AnalysisResult
from app.ml.speech_to_text import SpeechToText, AudioProcessor
from app.ml.fraud_detector import FraudDetector
from app.ml.nlp_analyzer import NLPAnalyzer


def convert_numpy_types(obj: Any) -> Any:
    """
    Recursively convert numpy types to native Python types for JSON serialization.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64, np.floating)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64, np.integer)):
        return int(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    return obj


class AnalysisService:
    """
    Main analysis service that orchestrates:
    1. Speech-to-text conversion
    2. NLP analysis
    3. Acoustic feature extraction
    4. Fraud detection
    5. Result aggregation
    """
    
    def __init__(self):
        self.speech_to_text = SpeechToText()
        self.audio_processor = AudioProcessor()
        self.fraud_detector = FraudDetector()
        self.nlp_analyzer = NLPAnalyzer()
    
    async def analyze_audio(self, audio_path: str, call_id: str) -> AnalysisResult:
        """
        Perform complete analysis on audio file
        
        Args:
            audio_path: Path to the audio file
            call_id: Unique identifier for the call
        
        Returns:
            Complete analysis result
        """
        logger.info(f"Starting analysis for call {call_id}")
        
        try:
            # Run transcription and audio feature extraction in parallel
            transcription_task = self.speech_to_text.transcribe(audio_path)
            features_task = self.audio_processor.extract_features(audio_path)
            
            transcription, acoustic_features = await asyncio.gather(
                transcription_task,
                features_task
            )
            
            logger.info(f"Transcription complete: {len(transcription.get('transcript', ''))} chars")
            
            # Extract voice characteristics
            voice_characteristics = await self.audio_processor.analyze_voice_characteristics(
                acoustic_features
            )
            
            # NLP analysis
            nlp_result = self.nlp_analyzer.analyze(transcription.get("transcript", ""))
            
            # Build behavioral data from NLP results
            behavioral_data = {
                "intent": nlp_result.get("intent", {}),
                "commands": nlp_result.get("commands", []),
                "pressure_score": self._calculate_pressure_score(nlp_result),
                "evasiveness_score": 0  # Would require conversation analysis
            }
            
            # Fraud detection with all signals
            fraud_result = self.fraud_detector.detect(
                text=transcription.get("transcript", ""),
                acoustic_features=acoustic_features,
                behavioral_data=behavioral_data
            )
            
            # Convert all numpy types to native Python types for JSON serialization
            acoustic_features = convert_numpy_types(acoustic_features)
            voice_characteristics = convert_numpy_types(voice_characteristics)
            behavioral_data = convert_numpy_types(behavioral_data)
            fraud_result = convert_numpy_types(fraud_result)
            nlp_result = convert_numpy_types(nlp_result)
            transcription = convert_numpy_types(transcription)
            
            # Compile final result
            result = AnalysisResult(
                call_id=call_id,
                status="completed",
                classification=fraud_result["classification"],
                risk_score=float(fraud_result["risk_score"]),
                spam_score=float(fraud_result["spam_score"]),
                fraud_score=float(fraud_result["fraud_score"]),
                phishing_score=float(fraud_result["phishing_score"]),
                robocall_score=float(fraud_result["robocall_score"]),
                transcript=transcription.get("transcript", ""),
                transcript_language=transcription.get("language", "en"),
                transcript_confidence=float(transcription.get("confidence", 0)),
                suspicious_keywords=fraud_result["suspicious_keywords"],
                fraud_indicators=fraud_result["fraud_indicators"],
                highlighted_phrases=fraud_result["highlighted_phrases"],
                voice_characteristics=voice_characteristics,
                acoustic_features=acoustic_features,
                behavioral_patterns=behavioral_data,
                intent_analysis=nlp_result.get("intent", {}),
                ai_explanation=fraud_result["explanation"],
                confidence_score=float(fraud_result["confidence"]),
                duration_seconds=float(acoustic_features.get("duration", 0)),
                analyzed_at=datetime.utcnow()
            )
            
            logger.info(f"Analysis complete for {call_id}: {result.classification} ({result.risk_score})")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed for {call_id}: {str(e)}")
            raise
    
    async def analyze_text(self, text: str, call_id: str) -> AnalysisResult:
        """
        Perform analysis on text transcript (without audio)
        
        Args:
            text: Call transcript text
            call_id: Unique identifier
        
        Returns:
            Analysis result
        """
        logger.info(f"Starting text analysis for {call_id}")
        
        try:
            # NLP analysis
            nlp_result = self.nlp_analyzer.analyze(text)
            
            # Detect language
            language = self.nlp_analyzer.detect_language(text)
            
            # Behavioral data from NLP
            behavioral_data = {
                "intent": nlp_result.get("intent", {}),
                "commands": nlp_result.get("commands", []),
                "pressure_score": self._calculate_pressure_score(nlp_result),
                "questions_asked": len(nlp_result.get("questions", []))
            }
            
            # Fraud detection (text only)
            fraud_result = self.fraud_detector.detect(
                text=text,
                acoustic_features=None,
                behavioral_data=behavioral_data
            )
            
            # Convert all numpy types to native Python types for JSON serialization
            behavioral_data = convert_numpy_types(behavioral_data)
            fraud_result = convert_numpy_types(fraud_result)
            nlp_result = convert_numpy_types(nlp_result)
            
            result = AnalysisResult(
                call_id=call_id,
                status="completed",
                classification=fraud_result["classification"],
                risk_score=float(fraud_result["risk_score"]),
                spam_score=float(fraud_result["spam_score"]),
                fraud_score=float(fraud_result["fraud_score"]),
                phishing_score=float(fraud_result["phishing_score"]),
                robocall_score=float(fraud_result["robocall_score"]),
                transcript=text,
                transcript_language=language,
                transcript_confidence=0.95,
                suspicious_keywords=fraud_result["suspicious_keywords"],
                fraud_indicators=fraud_result["fraud_indicators"],
                highlighted_phrases=fraud_result["highlighted_phrases"],
                voice_characteristics={},
                acoustic_features={},
                behavioral_patterns=behavioral_data,
                intent_analysis=nlp_result.get("intent", {}),
                ai_explanation=fraud_result["explanation"],
                confidence_score=float(fraud_result["confidence"]),
                duration_seconds=0,
                analyzed_at=datetime.utcnow()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Text analysis failed for {call_id}: {str(e)}")
            raise
    
    async def process_stream_chunk(self, audio_data: str, 
                                   accumulated_text: str,
                                   chunk_id: int) -> Dict[str, Any]:
        """
        Process streaming audio chunk for real-time analysis
        
        Args:
            audio_data: Base64 encoded audio chunk
            accumulated_text: Previously transcribed text
            chunk_id: Chunk sequence number
        
        Returns:
            Partial analysis result
        """
        # In production, this would use streaming speech recognition
        # For now, return incremental analysis
        
        # Quick fraud check on accumulated text
        quick_result = await self.quick_text_analysis(accumulated_text)
        
        return {
            "transcript": accumulated_text,
            "new_text": "",  # Would be the newly transcribed portion
            "risk_score": quick_result.get("risk_score", 0),
            "flags": quick_result.get("flags", []),
            "chunk_id": chunk_id
        }
    
    async def quick_text_analysis(self, text: str) -> Dict[str, Any]:
        """
        Quick analysis for real-time feedback
        """
        if not text:
            return {"risk_score": 0, "flags": [], "keywords": []}
        
        # Use fraud detector for quick keyword scan
        result = self.fraud_detector.detect(text)
        
        return {
            "risk_score": result["risk_score"],
            "flags": [
                ind["description"] 
                for ind in result["fraud_indicators"][:3]
            ],
            "keywords": result["suspicious_keywords"][:5]
        }
    
    def _calculate_pressure_score(self, nlp_result: Dict) -> float:
        """Calculate pressure tactics score from NLP results"""
        score = 0
        
        # Check intent
        intent = nlp_result.get("intent", {})
        if intent.get("primary_intent") == "create_urgency":
            score += 0.4
        if intent.get("primary_intent") == "threaten":
            score += 0.5
        
        # Check commands
        commands = nlp_result.get("commands", [])
        high_risk_commands = [c for c in commands if c.get("risk_level") == "high"]
        score += len(high_risk_commands) * 0.15
        
        # Check sentiment
        sentiment = nlp_result.get("sentiment", {})
        if sentiment.get("sentiment") == "threatening":
            score += 0.3
        
        return min(score, 1.0)
