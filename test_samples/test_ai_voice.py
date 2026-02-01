"""Test AI Voice Detection API"""
import requests
import base64
from pathlib import Path

# Read test audio file
audio_path = Path('d:/hackathon/test_samples/batch3/en_bank_freeze.mp3')
with open(audio_path, 'rb') as f:
    audio_data = base64.b64encode(f.read()).decode('utf-8')

# Test AI Voice Detection
print("Testing AI Voice Detection API...")
response = requests.post('http://localhost:8000/api/v1/ai-voice/detect', json={
    'audio': audio_data,
    'language': 'en'
})

if response.status_code == 200:
    result = response.json()
    print("AI Voice Detection Test: SUCCESS")
    print(f"  Classification: {result.get('classification')}")
    print(f"  Is AI Generated: {result.get('is_ai_generated')}")
    print(f"  Confidence: {result.get('confidence_percentage', 0):.1f}%")
    print(f"  Language: {result.get('language_name')}")
    explanation = result.get('explanation', '')
    print(f"  Explanation: {explanation[:150]}...")
    
    details = result.get('analysis_details', {})
    if details:
        print(f"  AI Indicators: {details.get('ai_indicators', [])}")
        print(f"  Human Indicators: {details.get('human_indicators', [])}")
else:
    print(f"Error: {response.status_code}")
    print(response.text[:500])
