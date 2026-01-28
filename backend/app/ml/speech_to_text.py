"""
Speech-to-Text Processor
Converts audio to text using speech recognition
"""

import os
import io
import asyncio
from typing import Optional, Dict, Tuple
from loguru import logger
import numpy as np

from app.ml.model_loader import get_whisper


class SpeechToText:
    """
    Speech-to-text processor supporting multiple engines
    """
    
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.whisper_model = None
        self.sample_rate = 16000
    
    def _get_whisper_model(self):
        """Get Whisper model - prefer preloaded, fallback to loading"""
        # First try to get preloaded model
        preloaded = get_whisper()
        if preloaded is not None and preloaded != "fallback":
            return preloaded
        
        # Load our own if not preloaded
        if self.whisper_model is None:
            try:
                import whisper
                logger.info(f"Loading Whisper model: {self.model_name}")
                self.whisper_model = whisper.load_model(self.model_name)
            except Exception as e:
                logger.error(f"Failed to load Whisper: {e}")
                return None
        return self.whisper_model
    
    async def transcribe(self, audio_path: str, language: str = None) -> Dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (auto-detect if None)
        
        Returns:
            Dict with transcript, language, confidence, and segments
        """
        import os
        
        # Verify file exists
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return self._empty_transcription("File not found")
        
        logger.info(f"Starting transcription for: {audio_path}")
        
        try:
            # Try using Whisper
            result = await self._transcribe_whisper(audio_path, language)
            logger.info(f"Whisper transcription successful: {len(result.get('transcript', ''))} chars")
            return result
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            
            # Try fallback
            try:
                result = await self._transcribe_fallback(audio_path)
                if result.get("transcript"):
                    logger.info(f"Fallback transcription successful: {len(result.get('transcript', ''))} chars")
                    return result
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
            
            # Return empty instead of demo
            return self._empty_transcription(f"Transcription failed: {str(e)}")
    
    def _empty_transcription(self, error_msg: str = "") -> Dict:
        """Return empty transcription when all methods fail"""
        return {
            "transcript": f"[Audio content - transcription unavailable: {error_msg}]" if error_msg else "[Audio content]",
            "language": "en",
            "confidence": 0,
            "segments": [],
            "duration": 0,
            "error": error_msg
        }
    
    async def _transcribe_whisper(self, audio_path: str, language: str = None) -> Dict:
        """Transcribe using OpenAI Whisper"""
        try:
            # Get the preloaded or load new model
            model = self._get_whisper_model()
            if model is None:
                raise Exception("Whisper model not available")
            
            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Run transcription in thread pool to not block
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: model.transcribe(
                    audio_path,
                    language=language,
                    task="transcribe"
                )
            )
            
            transcript = result["text"].strip()
            logger.info(f"Transcription complete: {len(transcript)} chars")
            
            return {
                "transcript": transcript,
                "language": result.get("language", "en"),
                "confidence": self._estimate_confidence(result),
                "segments": [
                    {
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"].strip(),
                        "confidence": seg.get("no_speech_prob", 0)
                    }
                    for seg in result.get("segments", [])
                ],
                "duration": result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0
            }
            
        except ImportError:
            logger.warning("Whisper not installed, using fallback")
            raise
        except Exception as e:
            logger.error(f"Whisper error: {e}")
            raise
    
    async def _transcribe_fallback(self, audio_path: str) -> Dict:
        """Fallback transcription using speech_recognition library"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            # Convert to WAV if needed
            wav_path = await self._ensure_wav(audio_path)
            
            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)
            
            # Try Google Speech Recognition
            try:
                text = recognizer.recognize_google(audio)
                return {
                    "transcript": text,
                    "language": "en",
                    "confidence": 0.8,
                    "segments": [],
                    "duration": 0
                }
            except sr.UnknownValueError:
                return {
                    "transcript": "",
                    "language": "en",
                    "confidence": 0,
                    "segments": [],
                    "duration": 0
                }
                
        except ImportError:
            logger.warning("speech_recognition not installed")
            raise ImportError("speech_recognition library not installed")
    
    async def _ensure_wav(self, audio_path: str) -> str:
        """Convert audio to WAV format if needed"""
        if audio_path.endswith('.wav'):
            return audio_path
        
        try:
            from pydub import AudioSegment
            
            # Load and convert
            audio = AudioSegment.from_file(audio_path)
            wav_path = audio_path.rsplit('.', 1)[0] + '_converted.wav'
            audio.export(wav_path, format='wav')
            return wav_path
            
        except ImportError:
            logger.warning("pydub not installed, assuming WAV format")
            return audio_path
    
    def _estimate_confidence(self, result: Dict) -> float:
        """Estimate overall transcription confidence"""
        segments = result.get("segments", [])
        if not segments:
            return 0.5
        
        # Average (1 - no_speech_prob) for all segments
        confidences = [1 - seg.get("no_speech_prob", 0) for seg in segments]
        return sum(confidences) / len(confidences)
    
    def _demo_transcription(self) -> Dict:
        """Return demo transcription for testing"""
        return {
            "transcript": "This is a demo transcription. In production, actual speech recognition would be used.",
            "language": "en",
            "confidence": 0.9,
            "segments": [],
            "duration": 5.0
        }
    
    async def transcribe_stream(self, audio_chunk: bytes) -> Tuple[str, bool]:
        """
        Transcribe streaming audio chunk
        
        Returns:
            Tuple of (partial_transcript, is_final)
        """
        # In production, this would use streaming speech recognition
        # For now, return placeholder
        return "", False


class AudioProcessor:
    """
    Audio preprocessing and feature extraction
    """
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
    
    async def extract_features(self, audio_path: str) -> Dict:
        """
        Extract acoustic features from audio
        
        Returns features like:
        - Speaking rate
        - Pitch statistics
        - Energy levels
        - Voice quality metrics
        """
        try:
            import librosa
            import numpy as np
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Duration
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Pitch (F0) analysis
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            pitch_mean = np.mean(pitch_values) if pitch_values else 0
            pitch_std = np.std(pitch_values) if pitch_values else 0
            
            # Energy/RMS
            rms = librosa.feature.rms(y=y)[0]
            energy_mean = np.mean(rms)
            energy_std = np.std(rms)
            
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            
            # Zero crossing rate (can indicate voice quality)
            zcr = np.mean(librosa.feature.zero_crossing_rate(y))
            
            # Tempo estimation
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # Voice activity detection (simple)
            voice_frames = np.sum(rms > np.mean(rms) * 0.5)
            voice_ratio = voice_frames / len(rms)
            
            return {
                "duration": duration,
                "sample_rate": sr,
                "pitch_mean": float(pitch_mean),
                "pitch_std": float(pitch_std),
                "energy_mean": float(energy_mean),
                "energy_std": float(energy_std),
                "spectral_centroid": float(spectral_centroid),
                "spectral_rolloff": float(spectral_rolloff),
                "zero_crossing_rate": float(zcr),
                "tempo": float(tempo),
                "voice_activity_ratio": float(voice_ratio),
                "speaking_rate": self._estimate_speaking_rate(duration, pitch_values),
                "stress_level": self._estimate_stress(pitch_std, energy_std),
                "synthetic_probability": self._estimate_synthetic(pitch_std, zcr)
            }
            
        except ImportError:
            logger.warning("librosa not installed, using default features")
            return self._default_features()
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return self._default_features()
    
    def _estimate_speaking_rate(self, duration: float, pitch_values: list) -> float:
        """Estimate words per minute from pitch transitions"""
        if duration <= 0:
            return 150  # Default
        
        # Rough estimation: pitch peaks often correlate with syllables
        # Average 1.5 syllables per word
        syllables = len(pitch_values) / 10  # Rough approximation
        words = syllables / 1.5
        wpm = (words / duration) * 60
        
        return min(max(wpm, 80), 250)  # Clamp to reasonable range
    
    def _estimate_stress(self, pitch_std: float, energy_std: float) -> float:
        """Estimate voice stress level"""
        # Higher variation in pitch and energy indicates stress
        pitch_stress = min(pitch_std / 50, 1.0)  # Normalize
        energy_stress = min(energy_std / 0.1, 1.0)
        
        return (pitch_stress + energy_stress) / 2
    
    def _estimate_synthetic(self, pitch_std: float, zcr: float) -> float:
        """Estimate probability of synthetic/robotic voice"""
        # Synthetic voices often have very consistent pitch
        if pitch_std < 5:  # Very low variation
            return 0.7
        elif pitch_std < 15:
            return 0.4
        else:
            return 0.1
    
    def _default_features(self) -> Dict:
        """Default features when extraction fails"""
        return {
            "duration": 0,
            "sample_rate": self.sample_rate,
            "pitch_mean": 150,
            "pitch_std": 30,
            "energy_mean": 0.1,
            "energy_std": 0.02,
            "spectral_centroid": 2000,
            "spectral_rolloff": 4000,
            "zero_crossing_rate": 0.1,
            "tempo": 120,
            "voice_activity_ratio": 0.7,
            "speaking_rate": 150,
            "stress_level": 0.3,
            "synthetic_probability": 0.1
        }
    
    async def analyze_voice_characteristics(self, features: Dict) -> Dict:
        """
        Analyze voice characteristics from extracted features
        """
        characteristics = {
            "tone": self._classify_tone(features),
            "speed": self._classify_speed(features.get("speaking_rate", 150)),
            "stress": self._classify_stress(features.get("stress_level", 0.3)),
            "urgency": self._estimate_urgency(features),
            "naturalness": 1 - features.get("synthetic_probability", 0.1)
        }
        
        return characteristics
    
    def _classify_tone(self, features: Dict) -> str:
        """Classify voice tone"""
        pitch = features.get("pitch_mean", 150)
        energy = features.get("energy_mean", 0.1)
        
        if energy > 0.15:
            if pitch > 200:
                return "aggressive"
            else:
                return "assertive"
        elif energy < 0.05:
            return "subdued"
        else:
            return "neutral"
    
    def _classify_speed(self, wpm: float) -> str:
        """Classify speaking speed"""
        if wpm > 180:
            return "fast"
        elif wpm < 120:
            return "slow"
        else:
            return "normal"
    
    def _classify_stress(self, stress_level: float) -> str:
        """Classify stress level"""
        if stress_level > 0.7:
            return "high"
        elif stress_level > 0.4:
            return "moderate"
        else:
            return "low"
    
    def _estimate_urgency(self, features: Dict) -> float:
        """Estimate urgency from voice features"""
        speed_factor = min(features.get("speaking_rate", 150) / 180, 1.0)
        stress_factor = features.get("stress_level", 0.3)
        energy_factor = min(features.get("energy_mean", 0.1) / 0.15, 1.0)
        
        return (speed_factor + stress_factor + energy_factor) / 3
