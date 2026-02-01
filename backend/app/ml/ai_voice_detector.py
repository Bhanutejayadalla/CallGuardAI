"""
AI-Generated Voice Detector
Detects whether audio is AI-generated or human-generated
Supports multiple languages: Tamil, English, Hindi, Malayalam, Telugu
"""

import os
import tempfile
import base64
import asyncio
from typing import Dict, Any, Optional, Tuple, List
from loguru import logger
import numpy as np
from enum import Enum


class VoiceClassification(str, Enum):
    AI_GENERATED = "ai_generated"
    HUMAN = "human"
    UNCERTAIN = "uncertain"


class SupportedLanguage(str, Enum):
    TAMIL = "ta"
    ENGLISH = "en"
    HINDI = "hi"
    MALAYALAM = "ml"
    TELUGU = "te"


# Language display names
LANGUAGE_NAMES = {
    "ta": "Tamil",
    "en": "English",
    "hi": "Hindi",
    "ml": "Malayalam",
    "te": "Telugu"
}


class AIVoiceDetector:
    """
    Detects AI-generated voices using multiple acoustic and spectral features.
    
    Detection approach:
    1. Spectral analysis - AI voices often have unnatural spectral patterns
    2. Pitch consistency - AI voices may have too-perfect pitch
    3. Formant analysis - AI voices may lack natural formant variations
    4. Temporal patterns - AI voices may have unnatural timing
    5. Noise patterns - AI voices often lack natural background noise
    6. Prosody analysis - AI voices may have unnatural rhythm/stress
    """
    
    def __init__(self):
        self.sample_rate = 16000
        self._librosa_available = False
        self._model_loaded = False
        
        # Check if librosa is available for advanced analysis
        try:
            import librosa
            self._librosa_available = True
        except ImportError:
            logger.warning("librosa not installed - using basic analysis")
        
        # Feature thresholds calibrated for AI voice detection
        self.thresholds = {
            "pitch_std_min": 15,  # AI voices often have less pitch variation
            "pitch_std_max": 150,  # But extremely high variation is also suspicious
            "spectral_flatness_threshold": 0.3,  # AI may have more tonal content
            "zero_crossing_rate_min": 0.02,  # Too low = likely synthetic
            "hnr_min": 10,  # Harmonic-to-noise ratio
            "spectral_rolloff_min": 1500,  # Minimum rolloff for natural voice
            "mfcc_variance_min": 50,  # MFCC variance threshold
            "formant_regularity_max": 0.9,  # Too regular = likely AI
        }
        
        self._model_loaded = True
    
    def is_loaded(self) -> bool:
        """Check if detector is ready"""
        return self._model_loaded
    
    async def detect_from_base64(
        self, 
        audio_base64: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect if audio (Base64-encoded MP3) is AI-generated or human.
        
        Args:
            audio_base64: Base64-encoded MP3 audio data
            language: Optional language code (ta, en, hi, ml, te) for optimization
        
        Returns:
            Dict with classification, confidence, explanation, and analysis details
        """
        logger.info("Starting AI voice detection from Base64 audio")
        
        try:
            # Decode Base64 to audio file
            audio_data = base64.b64decode(audio_base64)
            
            # Detect file format from magic bytes
            suffix = ".mp3"  # Default to MP3 as per requirements
            if audio_data[:4] == b'RIFF':
                suffix = ".wav"
            elif audio_data[:4] == b'fLaC':
                suffix = ".flac"
            elif audio_data[:3] == b'OGG':
                suffix = ".ogg"
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # Run detection
                result = await self.detect(tmp_path, language)
                return result
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            logger.error(f"Error decoding Base64 audio: {e}")
            return self._error_result(f"Failed to decode audio: {str(e)}")
    
    async def detect(
        self, 
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect if audio file is AI-generated or human.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code for optimization
        
        Returns:
            Dict with classification, confidence, explanation, and features
        """
        logger.info(f"Starting AI voice detection for: {audio_path}")
        
        if not os.path.exists(audio_path):
            return self._error_result("Audio file not found")
        
        try:
            # Extract features
            features = await self._extract_features(audio_path)
            
            # Detect language if not provided
            detected_language = language or await self._detect_language(audio_path)
            
            # Run AI detection analysis
            analysis = self._analyze_features(features, detected_language)
            
            # Calculate final classification and confidence
            classification, confidence = self._calculate_classification(analysis)
            
            # Generate explanation
            explanation = self._generate_explanation(
                classification, 
                confidence, 
                analysis, 
                detected_language
            )
            
            return {
                "classification": classification.value,
                "is_ai_generated": classification == VoiceClassification.AI_GENERATED,
                "confidence_score": round(confidence, 4),
                "confidence_percentage": round(confidence * 100, 2),
                "language": detected_language,
                "language_name": LANGUAGE_NAMES.get(detected_language, "Unknown"),
                "explanation": explanation,
                "analysis_details": {
                    "features_analyzed": list(analysis.keys()),
                    "ai_indicators": analysis.get("ai_indicators", []),
                    "human_indicators": analysis.get("human_indicators", []),
                    "spectral_analysis": analysis.get("spectral", {}),
                    "temporal_analysis": analysis.get("temporal", {}),
                    "prosody_analysis": analysis.get("prosody", {})
                },
                "supported_languages": list(LANGUAGE_NAMES.values()),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"AI voice detection failed: {e}")
            return self._error_result(str(e))
    
    async def _extract_features(self, audio_path: str) -> Dict[str, Any]:
        """Extract acoustic features for AI detection"""
        features = {}
        
        try:
            if self._librosa_available:
                features = await self._extract_librosa_features(audio_path)
            else:
                features = await self._extract_basic_features(audio_path)
                
        except Exception as e:
            logger.warning(f"Feature extraction warning: {e}")
            features = self._default_features()
        
        return features
    
    async def _extract_librosa_features(self, audio_path: str) -> Dict[str, Any]:
        """Extract features using librosa"""
        import librosa
        import time
        
        loop = asyncio.get_event_loop()
        
        def _extract():
            try:
                start_time = time.time()
                
                # Load audio
                y, sr = librosa.load(audio_path, sr=self.sample_rate)
                logger.info(f"Audio loaded in {time.time() - start_time:.2f}s, duration: {len(y)/sr:.2f}s")
                
                if len(y) == 0:
                    return self._default_features()
                
                features = {}
                
                # Duration
                features["duration"] = len(y) / sr
                
                # Pitch analysis using simpler piptrack (faster than pyin)
                try:
                    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=512)
                    # Get pitch values where magnitude is significant
                    pitch_values = []
                    for t in range(pitches.shape[1]):
                        index = magnitudes[:, t].argmax()
                        pitch = pitches[index, t]
                        if pitch > 50:  # Valid pitch range
                            pitch_values.append(pitch)
                    
                    if len(pitch_values) > 0:
                        pitch_arr = np.array(pitch_values)
                        features["pitch_mean"] = float(np.mean(pitch_arr))
                        features["pitch_std"] = float(np.std(pitch_arr))
                        features["pitch_range"] = float(np.ptp(pitch_arr))
                        features["voiced_ratio"] = float(len(pitch_values) / pitches.shape[1])
                    else:
                        features["pitch_mean"] = 150.0
                        features["pitch_std"] = 30.0
                        features["pitch_range"] = 100.0
                        features["voiced_ratio"] = 0.5
                except Exception:
                    features["pitch_mean"] = 150.0
                    features["pitch_std"] = 30.0
                    features["pitch_range"] = 100.0
                    features["voiced_ratio"] = 0.5
                
                # Spectral features
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                features["spectral_centroid_mean"] = float(np.mean(spectral_centroids))
                features["spectral_centroid_std"] = float(np.std(spectral_centroids))
                
                spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
                features["spectral_rolloff_mean"] = float(np.mean(spectral_rolloff))
                
                spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
                features["spectral_flatness_mean"] = float(np.mean(spectral_flatness))
                features["spectral_flatness_std"] = float(np.std(spectral_flatness))
                
                spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
                features["spectral_bandwidth_mean"] = float(np.mean(spectral_bandwidth))
                
                # Zero crossing rate
                zcr = librosa.feature.zero_crossing_rate(y)[0]
                features["zero_crossing_rate"] = float(np.mean(zcr))
                features["zcr_std"] = float(np.std(zcr))
                
                # MFCCs for timbral analysis
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                features["mfcc_mean"] = [float(np.mean(mfcc)) for mfcc in mfccs]
                features["mfcc_std"] = [float(np.std(mfcc)) for mfcc in mfccs]
                features["mfcc_variance_total"] = float(np.var(mfccs))
                
                # RMS energy
                rms = librosa.feature.rms(y=y)[0]
                features["rms_mean"] = float(np.mean(rms))
                features["rms_std"] = float(np.std(rms))
                
                # Tempo estimation (simplified - use onset strength)
                try:
                    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                    features["tempo"] = float(librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0])
                except Exception:
                    features["tempo"] = 120.0
                
                # Harmonic-to-noise ratio approximation
                harmonic = librosa.effects.harmonic(y)
                percussive = librosa.effects.percussive(y)
                h_power = np.sum(harmonic ** 2)
                p_power = np.sum(percussive ** 2)
                features["hnr_approx"] = float(10 * np.log10(h_power / (p_power + 1e-10)))
                
                # Spectral contrast
                contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
                features["spectral_contrast_mean"] = [float(np.mean(c)) for c in contrast]
                
                # Onset detection for timing analysis
                onsets = librosa.onset.onset_detect(y=y, sr=sr)
                features["onset_count"] = len(onsets)
                if len(onsets) > 1:
                    onset_intervals = np.diff(onsets) * 512 / sr  # Convert to time
                    features["onset_regularity"] = float(1 - np.std(onset_intervals) / (np.mean(onset_intervals) + 1e-10))
                else:
                    features["onset_regularity"] = 0.5
                
                return features
                
            except Exception as e:
                logger.error(f"Librosa feature extraction error: {e}")
                return self._default_features()
        
        return await loop.run_in_executor(None, _extract)
    
    async def _extract_basic_features(self, audio_path: str) -> Dict[str, Any]:
        """Extract basic features without librosa"""
        import wave
        import struct
        
        try:
            # Try to load WAV file
            with wave.open(audio_path, 'rb') as wav:
                n_channels = wav.getnchannels()
                sample_width = wav.getsampwidth()
                framerate = wav.getframerate()
                n_frames = wav.getnframes()
                
                frames = wav.readframes(n_frames)
                
                # Convert to numpy array
                if sample_width == 2:
                    samples = np.frombuffer(frames, dtype=np.int16)
                else:
                    samples = np.frombuffer(frames, dtype=np.int8)
                
                # Basic features
                features = {
                    "duration": n_frames / framerate,
                    "sample_rate": framerate,
                    "rms_mean": float(np.sqrt(np.mean(samples.astype(float) ** 2))),
                    "rms_std": float(np.std(np.abs(samples.astype(float)))),
                    "zero_crossing_rate": float(np.sum(np.abs(np.diff(np.signbit(samples)))) / len(samples)),
                    "pitch_mean": 150.0,  # Default
                    "pitch_std": 30.0,
                    "spectral_flatness_mean": 0.2,
                    "mfcc_variance_total": 100.0
                }
                
                return features
                
        except Exception as e:
            logger.warning(f"Basic feature extraction failed: {e}")
            return self._default_features()
    
    def _default_features(self) -> Dict[str, Any]:
        """Return default features when extraction fails"""
        return {
            "duration": 0,
            "pitch_mean": 150.0,
            "pitch_std": 30.0,
            "pitch_range": 100.0,
            "spectral_centroid_mean": 2000.0,
            "spectral_centroid_std": 500.0,
            "spectral_flatness_mean": 0.2,
            "spectral_flatness_std": 0.1,
            "spectral_rolloff_mean": 4000.0,
            "zero_crossing_rate": 0.1,
            "zcr_std": 0.05,
            "mfcc_variance_total": 100.0,
            "rms_mean": 0.1,
            "rms_std": 0.02,
            "onset_regularity": 0.5,
            "hnr_approx": 15.0,
            "voiced_ratio": 0.7
        }
    
    async def _detect_language(self, audio_path: str) -> str:
        """Detect language from audio using Whisper (with speed optimizations)"""
        try:
            from app.ml.model_loader import get_whisper
            
            model = get_whisper()
            if model and model != "fallback":
                loop = asyncio.get_event_loop()
                
                def _detect():
                    try:
                        # Use first 15 seconds for faster language detection
                        import whisper
                        audio = whisper.load_audio(audio_path)
                        # Smaller chunk for faster detection (15 seconds instead of 30)
                        audio = whisper.pad_or_trim(audio, length=16000 * 15)
                        mel = whisper.log_mel_spectrogram(audio).to(model.device)
                        _, probs = model.detect_language(mel)
                        
                        # Check for supported languages
                        supported = ["ta", "en", "hi", "ml", "te"]
                        best_lang = max(supported, key=lambda l: probs.get(l, 0))
                        
                        # If confidence is too low, default to English
                        if probs.get(best_lang, 0) < 0.1:
                            return "en"
                        return best_lang
                    except Exception as e:
                        logger.warning(f"Language detection error: {e}")
                        return "en"
                
                return await loop.run_in_executor(None, _detect)
                
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
        
        return "en"  # Default to English
    
    def _analyze_features(self, features: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Analyze extracted features for AI detection"""
        analysis: Dict[str, Any] = {
            "ai_indicators": [],
            "human_indicators": [],
            "ai_score_components": [],
            "human_score_components": []
        }
        
        # ===== SPECTRAL ANALYSIS =====
        spectral = {}
        
        # Spectral flatness - AI often has more tonal (less flat) content
        sf = features.get("spectral_flatness_mean", 0.2)
        spectral["flatness"] = sf
        if sf < 0.1:
            analysis["ai_indicators"].append("Unusually tonal spectral content (low flatness)")
            analysis["ai_score_components"].append(0.15)
        elif sf > 0.35:
            analysis["human_indicators"].append("Natural spectral variation")
            analysis["human_score_components"].append(0.1)
        
        # Spectral flatness consistency - AI often too consistent
        sf_std = features.get("spectral_flatness_std", 0.1)
        spectral["flatness_std"] = sf_std
        if sf_std < 0.05:
            analysis["ai_indicators"].append("Spectral consistency too uniform (likely synthetic)")
            analysis["ai_score_components"].append(0.12)
        
        # Spectral centroid variation
        sc_std = features.get("spectral_centroid_std", 500)
        spectral["centroid_std"] = sc_std
        if sc_std < 200:
            analysis["ai_indicators"].append("Limited spectral centroid variation")
            analysis["ai_score_components"].append(0.1)
        elif sc_std > 800:
            analysis["human_indicators"].append("Natural spectral dynamics")
            analysis["human_score_components"].append(0.1)
        
        analysis["spectral"] = spectral
        
        # ===== PITCH/PROSODY ANALYSIS =====
        prosody = {}
        
        # Pitch variation - AI voices often have unnatural pitch patterns
        pitch_std = features.get("pitch_std", 30)
        prosody["pitch_std"] = pitch_std
        if pitch_std < self.thresholds["pitch_std_min"]:
            analysis["ai_indicators"].append("Pitch variation too consistent (monotonic)")
            analysis["ai_score_components"].append(0.18)
        elif pitch_std > self.thresholds["pitch_std_max"]:
            analysis["ai_indicators"].append("Pitch variation too erratic")
            analysis["ai_score_components"].append(0.1)
        else:
            analysis["human_indicators"].append("Natural pitch variation")
            analysis["human_score_components"].append(0.12)
        
        # Pitch range
        pitch_range = features.get("pitch_range", 100)
        prosody["pitch_range"] = pitch_range
        if pitch_range < 50:
            analysis["ai_indicators"].append("Limited pitch range")
            analysis["ai_score_components"].append(0.08)
        
        analysis["prosody"] = prosody
        
        # ===== TEMPORAL ANALYSIS =====
        temporal = {}
        
        # Onset regularity - AI voices may have too-regular timing
        onset_reg = features.get("onset_regularity", 0.5)
        temporal["onset_regularity"] = onset_reg
        if onset_reg > self.thresholds["formant_regularity_max"]:
            analysis["ai_indicators"].append("Timing patterns too regular (machine-like)")
            analysis["ai_score_components"].append(0.15)
        elif onset_reg < 0.3:
            analysis["human_indicators"].append("Natural speech rhythm variations")
            analysis["human_score_components"].append(0.1)
        
        # Zero crossing rate
        zcr = features.get("zero_crossing_rate", 0.1)
        temporal["zero_crossing_rate"] = zcr
        if zcr < self.thresholds["zero_crossing_rate_min"]:
            analysis["ai_indicators"].append("Abnormally low zero-crossing rate")
            analysis["ai_score_components"].append(0.1)
        
        # ZCR consistency
        zcr_std = features.get("zcr_std", 0.05)
        temporal["zcr_std"] = zcr_std
        if zcr_std < 0.02:
            analysis["ai_indicators"].append("Zero-crossing rate too consistent")
            analysis["ai_score_components"].append(0.08)
        
        analysis["temporal"] = temporal
        
        # ===== MFCC/TIMBRE ANALYSIS =====
        mfcc_var = features.get("mfcc_variance_total", 100)
        if mfcc_var < self.thresholds["mfcc_variance_min"]:
            analysis["ai_indicators"].append("Limited timbral variation in voice")
            analysis["ai_score_components"].append(0.12)
        else:
            analysis["human_indicators"].append("Rich timbral characteristics")
            analysis["human_score_components"].append(0.1)
        
        # ===== HARMONIC ANALYSIS =====
        hnr = features.get("hnr_approx", 15)
        if hnr > 25:
            analysis["ai_indicators"].append("Unusually clean harmonic structure (too perfect)")
            analysis["ai_score_components"].append(0.1)
        elif hnr < self.thresholds["hnr_min"]:
            analysis["human_indicators"].append("Natural voice characteristics with breath/noise")
            analysis["human_score_components"].append(0.08)
        
        # ===== ENERGY DYNAMICS =====
        rms_std = features.get("rms_std", 0.02)
        if rms_std < 0.01:
            analysis["ai_indicators"].append("Energy dynamics too uniform")
            analysis["ai_score_components"].append(0.08)
        elif rms_std > 0.05:
            analysis["human_indicators"].append("Natural energy variation in speech")
            analysis["human_score_components"].append(0.08)
        
        # ===== VOICED RATIO =====
        voiced = features.get("voiced_ratio", 0.7)
        if voiced > 0.95:
            analysis["ai_indicators"].append("Unnatural amount of voiced content")
            analysis["ai_score_components"].append(0.05)
        
        return analysis
    
    def _calculate_classification(
        self, 
        analysis: Dict[str, Any]
    ) -> Tuple[VoiceClassification, float]:
        """Calculate final classification and confidence"""
        
        ai_score = sum(analysis.get("ai_score_components", []))
        human_score = sum(analysis.get("human_score_components", []))
        
        # Count indicators
        ai_indicators = len(analysis.get("ai_indicators", []))
        human_indicators = len(analysis.get("human_indicators", []))
        
        # Calculate base confidence
        total_score = ai_score + human_score + 0.1  # Avoid division by zero
        
        if ai_score > human_score:
            # Leaning towards AI-generated
            confidence = min(0.95, 0.5 + (ai_score / total_score) * 0.45)
            
            # Strong AI indicators threshold
            if ai_indicators >= 4 and ai_score >= 0.35:
                return VoiceClassification.AI_GENERATED, confidence
            elif ai_indicators >= 2 and ai_score >= 0.25:
                return VoiceClassification.AI_GENERATED, confidence * 0.9
            elif ai_indicators >= 1 and ai_score >= 0.15:
                return VoiceClassification.UNCERTAIN, 0.5 + (ai_score - human_score) * 0.3
            else:
                return VoiceClassification.UNCERTAIN, 0.5
                
        elif human_score > ai_score:
            # Leaning towards human
            confidence = min(0.95, 0.5 + (human_score / total_score) * 0.45)
            
            if human_indicators >= 3 and human_score >= 0.3:
                return VoiceClassification.HUMAN, confidence
            elif human_indicators >= 2 and human_score >= 0.2:
                return VoiceClassification.HUMAN, confidence * 0.9
            else:
                return VoiceClassification.UNCERTAIN, 0.5 + (human_score - ai_score) * 0.3
        else:
            # Equal scores - uncertain
            return VoiceClassification.UNCERTAIN, 0.5
    
    def _generate_explanation(
        self, 
        classification: VoiceClassification,
        confidence: float,
        analysis: Dict[str, Any],
        language: str
    ) -> str:
        """Generate human-readable explanation"""
        
        lang_name = LANGUAGE_NAMES.get(language, "Unknown")
        confidence_pct = round(confidence * 100, 1)
        
        if classification == VoiceClassification.AI_GENERATED:
            explanation = f"This voice sample ({lang_name}) is classified as AI-GENERATED with {confidence_pct}% confidence.\n\n"
            explanation += "Key indicators of synthetic voice:\n"
            for indicator in analysis.get("ai_indicators", [])[:5]:
                explanation += f"• {indicator}\n"
            explanation += "\nRecommendation: Exercise caution. This audio appears to be artificially generated."
            
        elif classification == VoiceClassification.HUMAN:
            explanation = f"This voice sample ({lang_name}) is classified as HUMAN with {confidence_pct}% confidence.\n\n"
            explanation += "Indicators of natural human voice:\n"
            for indicator in analysis.get("human_indicators", [])[:5]:
                explanation += f"• {indicator}\n"
            explanation += "\nThe audio exhibits characteristics consistent with natural human speech."
            
        else:  # UNCERTAIN
            explanation = f"This voice sample ({lang_name}) classification is UNCERTAIN ({confidence_pct}% confidence).\n\n"
            
            ai_ind = analysis.get("ai_indicators", [])
            human_ind = analysis.get("human_indicators", [])
            
            if ai_ind:
                explanation += "Potential AI indicators:\n"
                for ind in ai_ind[:3]:
                    explanation += f"• {ind}\n"
            
            if human_ind:
                explanation += "\nPotential human indicators:\n"
                for ind in human_ind[:3]:
                    explanation += f"• {ind}\n"
            
            explanation += "\nRecommendation: Further analysis may be needed for definitive classification."
        
        return explanation
    
    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """Return error result structure"""
        return {
            "classification": "error",
            "is_ai_generated": None,
            "confidence_score": 0,
            "confidence_percentage": 0,
            "language": "unknown",
            "language_name": "Unknown",
            "explanation": f"Error during analysis: {error_msg}",
            "analysis_details": {},
            "supported_languages": list(LANGUAGE_NAMES.values()),
            "status": "error",
            "error": error_msg
        }


# Singleton instance
_ai_voice_detector: Optional[AIVoiceDetector] = None


def get_ai_voice_detector() -> AIVoiceDetector:
    """Get or create AIVoiceDetector instance"""
    global _ai_voice_detector
    if _ai_voice_detector is None:
        _ai_voice_detector = AIVoiceDetector()
    return _ai_voice_detector


async def load_ai_voice_detector() -> AIVoiceDetector:
    """Load AI voice detector (called at startup)"""
    detector = get_ai_voice_detector()
    logger.info("✓ AI Voice Detector loaded")
    return detector
