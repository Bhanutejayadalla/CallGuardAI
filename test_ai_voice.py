"""Test script for AI Voice Detection API"""

import requests
import base64
import time
import io
import wave
import numpy as np

BASE_URL = "http://localhost:8000/api/v1/ai-voice"

def generate_test_audio(duration: float = 1.0, sample_rate: int = 16000) -> str:
    """Generate a test audio and return Base64 encoded WAV"""
    audio_data = (np.random.randn(int(sample_rate * duration)) * 5000).astype(np.int16)
    
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Status: {resp.status_code}")
    result = resp.json()
    print(f"Health: {result}")
    return resp.status_code == 200

def test_languages():
    """Test languages endpoint"""
    print("\n=== Testing Languages Endpoint ===")
    resp = requests.get(f"{BASE_URL}/languages", timeout=5)
    print(f"Status: {resp.status_code}")
    result = resp.json()
    print(f"Supported Languages: {result}")
    return resp.status_code == 200

def test_detect(language: str = "en"):
    """Test AI voice detection"""
    print(f"\n=== Testing AI Voice Detection (language: {language}) ===")
    
    # Generate test audio
    audio_base64 = generate_test_audio(duration=1.0)
    print(f"Audio size: {len(audio_base64)} chars")
    
    # Make detection request
    start = time.time()
    resp = requests.post(
        f"{BASE_URL}/detect",
        json={"audio": audio_base64, "language": language},
        timeout=60
    )
    elapsed = time.time() - start
    
    print(f"Response time: {elapsed:.2f}s")
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"\n--- Detection Result ---")
        print(f"Classification: {result.get('classification')}")
        print(f"Is AI Generated: {result.get('is_ai_generated')}")
        print(f"Confidence: {result.get('confidence_percentage')}%")
        print(f"Language: {result.get('language_name')} ({result.get('language')})")
        print(f"Explanation: {result.get('explanation')}")
        print(f"\nSupported Languages: {result.get('supported_languages')}")
        return True
    else:
        print(f"Error: {resp.text}")
        return False

def test_all_languages():
    """Test detection for all supported languages"""
    languages = ["en", "ta", "hi", "ml", "te"]
    language_names = {"en": "English", "ta": "Tamil", "hi": "Hindi", "ml": "Malayalam", "te": "Telugu"}
    
    print("\n" + "="*60)
    print("Testing AI Voice Detection for All Languages")
    print("="*60)
    
    for lang in languages:
        print(f"\n>>> Testing {language_names[lang]} ({lang})...")
        audio_base64 = generate_test_audio(duration=0.5)  # Shorter for speed
        
        start = time.time()
        resp = requests.post(
            f"{BASE_URL}/detect",
            json={"audio": audio_base64, "language": lang},
            timeout=60
        )
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"   ✓ {result.get('classification')} ({result.get('confidence_percentage')}%) in {elapsed:.1f}s")
        else:
            print(f"   ✗ Failed: {resp.text}")

if __name__ == "__main__":
    print("="*60)
    print("AI Voice Detection API Test Suite")
    print("="*60)
    
    # Test endpoints
    test_health()
    test_languages()
    
    # Test detection with English
    test_detect("en")
    
    # Test all languages
    test_all_languages()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)
