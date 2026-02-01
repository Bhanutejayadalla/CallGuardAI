"""
Download multilingual voice samples using Google TTS for testing CallGuard AI
"""
import os

# Create directory if not exists
os.makedirs("d:/hackathon/test_samples", exist_ok=True)

try:
    from gtts import gTTS
except ImportError:
    print("Installing gTTS...")
    os.system("pip install gTTS")
    from gtts import gTTS

# Sample fraud/scam messages in different languages
samples = {
    # English - Scam message
    "en_scam": {
        "lang": "en",
        "text": "Hello, this is the IRS calling. Your Social Security number has been suspended due to suspicious activity. Press 1 immediately to speak with an agent or a warrant will be issued for your arrest. You must pay the fine now using gift cards to avoid legal action."
    },
    # English - Safe message  
    "en_safe": {
        "lang": "en",
        "text": "Hi, this is Doctor Smith's office calling to confirm your appointment for next Tuesday at 3 PM. Please call us back at your convenience if you need to reschedule. Thank you and have a great day."
    },
    # Hindi - Scam message (bank fraud)
    "hi_scam": {
        "lang": "hi",
        "text": "नमस्ते, मैं स्टेट बैंक से बोल रहा हूं। आपका अकाउंट ब्लॉक हो गया है। अभी अपना OTP और पिन नंबर बताइए वरना आपका सारा पैसा डूब जाएगा। जल्दी करिए, समय कम है।"
    },
    # Hindi - Safe message
    "hi_safe": {
        "lang": "hi",  
        "text": "नमस्ते, यह आपके बिजली विभाग से है। आपका बिल जमा करने की अंतिम तिथि अगले सोमवार है। कृपया समय पर भुगतान करें। धन्यवाद।"
    },
    # Spanish - Scam message
    "es_scam": {
        "lang": "es",
        "text": "Felicitaciones! Has ganado un premio de un millón de dólares. Para reclamar tu premio, necesitas enviar mil dólares en tarjetas de regalo. Llama ahora, esta oferta expira en una hora."
    },
    # Spanish - Safe message
    "es_safe": {
        "lang": "es",
        "text": "Hola, le llamamos del consultorio del doctor García para recordarle su cita de mañana a las diez de la mañana. Por favor confirme su asistencia. Gracias."
    },
    # Tamil - Scam message
    "ta_scam": {
        "lang": "ta",
        "text": "வணக்கம், நான் வங்கியிலிருந்து பேசுகிறேன். உங்கள் கணக்கு முடக்கப்பட்டது. உடனடியாக உங்கள் OTP மற்றும் ATM பின் எண்ணை கொடுங்கள். இல்லையென்றால் உங்கள் பணம் போய்விடும்."
    },
    # Tamil - Safe message  
    "ta_safe": {
        "lang": "ta",
        "text": "வணக்கம், உங்கள் மருத்துவமனையிலிருந்து அழைக்கிறோம். நாளை உங்கள் சந்திப்பு காலை பத்து மணிக்கு உள்ளது. தயவுசெய்து நேரத்திற்கு வாருங்கள். நன்றி."
    },
    # Telugu - Scam message
    "te_scam": {
        "lang": "te",
        "text": "హలో, నేను పోలీస్ స్టేషన్ నుండి మాట్లాడుతున్నాను. మీ పేరు మీద అరెస్ట్ వారెంట్ ఉంది. వెంటనే ఐదు లక్షలు చెల్లించండి లేదా జైలుకు వెళ్ళాల్సి ఉంటుంది."
    },
    # Telugu - Safe message
    "te_safe": {
        "lang": "te", 
        "text": "నమస్కారం, మీ ఆర్డర్ రేపు డెలివరీ అవుతుంది. దయచేసి ఎవరైనా ఇంట్లో ఉండండి. మీ సహకారానికి ధన్యవాదాలు."
    },
    # French - Scam message
    "fr_scam": {
        "lang": "fr",
        "text": "Attention! Votre compte bancaire a été compromis. Vous devez transférer votre argent immédiatement vers un compte sécurisé. Appelez ce numéro maintenant avec vos informations de carte."
    },
    # French - Safe message
    "fr_safe": {
        "lang": "fr",
        "text": "Bonjour, nous vous rappelons votre rendez-vous chez le dentiste demain à quatorze heures. Merci de nous prévenir en cas d'empêchement. Bonne journée."
    },
    # German - Scam message
    "de_scam": {
        "lang": "de",
        "text": "Achtung! Ihr Computer wurde gehackt. Rufen Sie sofort unsere Hotline an und geben Sie uns Fernzugriff. Zahlen Sie dreihundert Euro in Bitcoin um das Problem zu lösen."
    },
    # German - Safe message
    "de_safe": {
        "lang": "de",
        "text": "Guten Tag, hier ist die Arztpraxis Müller. Wir möchten Sie an Ihren Termin morgen um zehn Uhr erinnern. Bitte bringen Sie Ihre Versichertenkarte mit. Auf Wiedersehen."
    }
}

print("Downloading multilingual voice samples...")
print("=" * 50)

for name, data in samples.items():
    output_file = f"d:/hackathon/test_samples/{name}.mp3"
    print(f"Creating {name}.mp3 ({data['lang']})...")
    
    try:
        tts = gTTS(text=data["text"], lang=data["lang"])
        tts.save(output_file)
        print(f"  ✓ Saved: {output_file}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("=" * 50)
print("All samples downloaded!")
print(f"\nFiles saved to: d:/hackathon/test_samples/")
