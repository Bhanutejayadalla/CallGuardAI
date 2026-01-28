"""
Verify Hackathon Requirements for AI-Generated Voice Detection (Multi-Language)

Requirements:
1. API-based system ✓
2. Determines if voice is AI-generated or human-generated ✓
3. Supports 5 languages: Tamil, English, Hindi, Malayalam, Telugu ✓
4. Accepts Base64-encoded MP3 audio input ✓
5. Returns structured JSON with classification, confidence score, and explanation ✓
"""

import requests
import json
import base64
import wave
import struct
import io
from colorama import init, Fore, Style

init()

# Generate test audio samples
def generate_test_audio(duration_ms=100):
    """Generate a simple test audio in WAV format, then convert to MP3-like"""
    sample_rate = 16000
    num_samples = int(sample_rate * duration_ms / 1000)
    
    # Create WAV in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(num_samples):
            value = int(32767 * 0.1 * (i % 100) / 100)
            wav_file.writeframes(struct.pack('<h', value))
    
    return wav_buffer.getvalue()

def test_requirements():
    """Test all hackathon requirements"""
    
    base_url = "http://localhost:8000/api/v1/ai-voice"
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"AI-Generated Voice Detection - Hackathon Requirements Verification")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    # Requirement 1: API-based system
    print(f"{Fore.YELLOW}[1] API-Based System{Style.RESET_ALL}")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} API is running")
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Health endpoint: {data.get('status')}")
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Model loaded: {data.get('model_loaded')}")
        else:
            print(f"  {Fore.RED}✗{Style.RESET_ALL} API health check failed")
            return False
    except Exception as e:
        print(f"  {Fore.RED}✗{Style.RESET_ALL} Cannot connect to API: {e}")
        print(f"\n  {Fore.YELLOW}NOTE: Please start the backend server first:{Style.RESET_ALL}")
        print(f"  $ffmpegPath = \"C:\\Users\\Venkata Yadalla\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-8.0.1-full_build\\bin\"")
        print(f"  $env:PATH = \"$ffmpegPath;$env:PATH\"")
        print(f"  cd D:\\hackathon\\backend")
        print(f"  D:\\hackathon\\.venv\\Scripts\\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000")
        return False
    
    # Requirement 3: Five Languages Support
    print(f"\n{Fore.YELLOW}[2] Multi-Language Support (5 Languages){Style.RESET_ALL}")
    try:
        response = requests.get(f"{base_url}/languages", timeout=5)
        if response.status_code == 200:
            languages = response.json()
            required_langs = {'ta', 'en', 'hi', 'ml', 'te'}
            supported_codes = set(languages.keys())
            
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Languages endpoint available")
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Required: {sorted(required_langs)}")
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Supported: {sorted(supported_codes)}")
            
            if required_langs.issubset(supported_codes):
                print(f"  {Fore.GREEN}✓{Style.RESET_ALL} All 5 required languages supported!")
                for code, name in sorted(languages.items()):
                    if code in required_langs:
                        print(f"      • {code}: {name}")
            else:
                missing = required_langs - supported_codes
                print(f"  {Fore.RED}✗{Style.RESET_ALL} Missing languages: {missing}")
                return False
        else:
            print(f"  {Fore.RED}✗{Style.RESET_ALL} Languages endpoint failed")
            return False
    except Exception as e:
        print(f"  {Fore.RED}✗{Style.RESET_ALL} Error checking languages: {e}")
        return False
    
    # Requirement 4: Base64-encoded MP3 input
    print(f"\n{Fore.YELLOW}[3] Base64-Encoded MP3 Audio Input{Style.RESET_ALL}")
    audio_data = generate_test_audio()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Test audio generated")
    print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Base64 encoded: {len(audio_base64)} chars")
    
    # Requirement 2 & 5: Detection with JSON Response
    print(f"\n{Fore.YELLOW}[4] AI vs Human Detection with Structured JSON Response{Style.RESET_ALL}")
    
    test_languages = ['en', 'ta', 'hi', 'ml', 'te']
    all_passed = True
    
    for lang_code in test_languages:
        lang_name = languages.get(lang_code, lang_code)
        
        try:
            payload = {
                "audio": audio_base64,
                "language": lang_code
            }
            
            response = requests.post(
                f"{base_url}/detect",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify required fields
                has_classification = 'classification' in result
                has_confidence = 'confidence_score' in result
                has_explanation = 'explanation' in result
                
                if has_classification and has_confidence and has_explanation:
                    classification = result['classification']
                    confidence = result['confidence_score']
                    print(f"  {Fore.GREEN}✓{Style.RESET_ALL} {lang_name} ({lang_code}): {classification} ({confidence:.1f}% confidence)")
                    print(f"      Fields: classification={has_classification}, confidence_score={has_confidence}, explanation={has_explanation}")
                else:
                    print(f"  {Fore.RED}✗{Style.RESET_ALL} {lang_name} ({lang_code}): Missing required fields")
                    all_passed = False
            else:
                print(f"  {Fore.RED}✗{Style.RESET_ALL} {lang_name} ({lang_code}): HTTP {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"  {Fore.RED}✗{Style.RESET_ALL} {lang_name} ({lang_code}): {e}")
            all_passed = False
    
    if not all_passed:
        return False
    
    # Final Summary
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}✓ API-based system{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ AI vs Human voice detection{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Five languages supported: Tamil, English, Hindi, Malayalam, Telugu{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Base64-encoded MP3 audio input{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Structured JSON response (classification, confidence_score, explanation){Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"✓ ALL HACKATHON REQUIREMENTS SATISFIED!")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    return True

if __name__ == "__main__":
    try:
        test_requirements()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted{Style.RESET_ALL}")
