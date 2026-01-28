"""
Quick Demo: Test AI Voice Detection via Browser
This creates a test audio file you can upload
"""

import wave
import numpy as np
import base64

# Generate a 3-second test audio file
sample_rate = 16000
duration = 3.0
audio_data = (np.random.randn(int(sample_rate * duration)) * 5000).astype(np.int16)

# Save as WAV file
with wave.open('demo_audio.wav', 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())

print("✅ Created demo_audio.wav in current directory")
print("\nHow to test:")
print("1. Open http://localhost:3000/ai-voice in your browser")
print("2. Click 'Upload Audio File'")
print("3. Select demo_audio.wav")
print("4. Choose language (e.g., English)")
print("5. Click 'Detect AI Voice'")
print("\n✨ You should see AI detection results with confidence score!")
