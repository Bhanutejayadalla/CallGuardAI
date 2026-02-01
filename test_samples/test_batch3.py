"""
Test batch 3 audio samples against the CallGuard API
"""
import requests
import os
import json
from pathlib import Path

API_BASE = "http://localhost:8000/api/v1"

def test_audio_file(file_path, filename):
    """Test a single audio file"""
    print(f"\n{'='*80}")
    print(f"Testing: {filename}")
    print('='*80)
    
    with open(file_path, 'rb') as f:
        files = {'file': (filename, f, 'audio/mpeg')}
        response = requests.post(f"{API_BASE}/analyze/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Analysis successful")
        print(f"  Call ID: {result['call_id']}")
        print(f"  Classification: {result['classification'].upper()}")
        print(f"  Risk Score: {result['risk_score']}/100")
        if 'confidence' in result:
            print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  AI Voice Detected: {result.get('ai_voice_detected', False)}")
        
        if result.get('transcript'):
            print(f"  Transcript: {result['transcript'][:100]}...")
        
        if result.get('fraud_indicators'):
            print(f"  Fraud Indicators ({len(result['fraud_indicators'])}):")
            for indicator in result['fraud_indicators'][:3]:
                print(f"    - {indicator}")
                
        if result.get('suspicious_keywords'):
            print(f"  Suspicious Keywords: {', '.join(result['suspicious_keywords'][:5])}")
        
        return result
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

# Test all batch3 samples
batch3_dir = Path("batch3")
results = {}

for audio_file in sorted(batch3_dir.glob("*.mp3")):
    result = test_audio_file(audio_file, audio_file.name)
    if result:
        results[audio_file.name] = {
            'classification': result['classification'],
            'risk_score': result['risk_score']
        }

# Summary
print(f"\n{'='*80}")
print("BATCH 3 TEST SUMMARY")
print('='*80)

scam_samples = [k for k in results.keys() if any(x in k for x in ['bank', 'credit', 'medicare', 'govt', 'microsoft', 'internet', 'crypto', 'inversion'])]
safe_samples = [k for k in results.keys() if any(x in k for x in ['doctor', 'reminder', 'school', 'delivery'])]

print(f"\nScam samples tested: {len(scam_samples)}")
for sample in scam_samples:
    result = results[sample]
    status = "✓ DETECTED" if result['classification'] in ['fraud', 'phishing', 'robocall'] else "✗ MISSED"
    print(f"  {status} - {sample}: {result['classification'].upper()} ({result['risk_score']})")

print(f"\nSafe samples tested: {len(safe_samples)}")
for sample in safe_samples:
    result = results[sample]
    status = "✓ CORRECT" if result['classification'] == 'safe' else "✗ FALSE POSITIVE"
    print(f"  {status} - {sample}: {result['classification'].upper()} ({result['risk_score']})")

# Calculate detection rate
detected = sum(1 for s in scam_samples if results[s]['classification'] in ['fraud', 'phishing', 'robocall'])
detection_rate = (detected / len(scam_samples) * 100) if scam_samples else 0

safe_correct = sum(1 for s in safe_samples if results[s]['classification'] == 'safe')
false_positive_rate = ((len(safe_samples) - safe_correct) / len(safe_samples) * 100) if safe_samples else 0

print(f"\n📊 Statistics:")
print(f"  Scam Detection Rate: {detection_rate:.1f}% ({detected}/{len(scam_samples)})")
print(f"  False Positive Rate: {false_positive_rate:.1f}% ({len(safe_samples) - safe_correct}/{len(safe_samples)})")
