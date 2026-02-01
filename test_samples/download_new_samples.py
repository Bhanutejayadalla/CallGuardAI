"""
Download additional multilingual voice samples with different scam scenarios
"""
import os
from gtts import gTTS

# Create directory if not exists
os.makedirs("d:/hackathon/test_samples/batch2", exist_ok=True)

# New fraud/scam scenarios
samples = {
    # English - Tech support scam
    "en_tech_scam": {
        "lang": "en",
        "text": "This is Microsoft technical support. Your computer has a virus. We need remote access to fix it now. Please download TeamViewer and give us the code. Your system will crash in 30 minutes if you don't act immediately."
    },
    # English - Delivery scam
    "en_delivery_safe": {
        "lang": "en",
        "text": "Good afternoon, this is FedEx delivery service. Your package will arrive between 2 and 4 PM today. Please ensure someone is available to sign for the delivery. Have a great day."
    },
    # Hindi - Lottery scam
    "hi_lottery_scam": {
        "lang": "hi",
        "text": "बधाई हो! आपने दस लाख रुपये जीते हैं। इनाम लेने के लिए पहले पांच हजार रुपये टैक्स के रूप में भेजें। आज ही Google Pay से भेजें वरना इनाम रद्द हो जाएगा।"
    },
    # Hindi - Restaurant reservation safe
    "hi_restaurant_safe": {
        "lang": "hi",
        "text": "नमस्ते, आपकी टेबल आज शाम सात बजे के लिए बुक है। कृपया समय पर पहुंचें। अगर कैंसिल करना हो तो हमें कॉल करें। धन्यवाद।"
    },
    # Spanish - Investment scam
    "es_investment_scam": {
        "lang": "es",
        "text": "Tienes la oportunidad única de invertir en Bitcoin. Garantizamos el doble de tu dinero en una semana. Envía mil dólares ahora mismo. Esta oferta expira en una hora. No pierdas esta oportunidad."
    },
    # Tamil - Job scam
    "ta_job_scam": {
        "lang": "ta",
        "text": "உங்களுக்கு வீட்டிலிருந்தே வேலை வாய்ப்பு. மாதம் ஐம்பதாயிரம் சம்பளம். முதலில் ஐந்தாயிரம் ரூபாய் பயிற்சி கட்டணம் செலுத்துங்கள். இன்றே பணம் அனுப்பவும்."
    },
    # Telugu - Insurance scam
    "te_insurance_scam": {
        "lang": "te",
        "text": "మీకు ఉచిత జీవిత బీమా లభించింది. మీ పూర్తి వివరాలు ఇవ్వండి. ఆధార్ కార్డ్ నంబర్, పాన్ కార్డ్ నంబర్ మరియు బ్యాంక్ అకౌంట్ నంబర్ కావాలి."
    },
    # French - Romance scam
    "fr_romance_scam": {
        "lang": "fr",
        "text": "Mon chéri, j'ai besoin de ton aide. Je suis bloqué à l'étranger sans argent. S'il te plaît, envoie-moi cinq cents euros par Western Union. Je te rembourserai quand je rentrerai. C'est urgent."
    },
    # German - Tax scam
    "de_tax_scam": {
        "lang": "de",
        "text": "Finanzamt hier. Sie schulden uns zweitausend Euro Steuern. Zahlen Sie sofort oder wir pfänden Ihr Bankkonto. Sie haben nur zwei Stunden Zeit. Überweisen Sie jetzt."
    },
    # English - Package safe
    "en_package_safe": {
        "lang": "en",
        "text": "Hello, this is Amazon customer service. Your order has been shipped and will arrive in three business days. You can track your package using the tracking number sent to your email. Thank you for shopping with us."
    },
    # Hindi - Credit card scam
    "hi_credit_scam": {
        "lang": "hi",
        "text": "आपका क्रेडिट कार्ड ब्लॉक हो गया है। तुरंत अपना CVV नंबर और कार्ड की पूरी डिटेल बताइए। नहीं तो आपका कार्ड हमेशा के लिए बंद हो जाएगा।"
    },
    # Spanish - Charity scam
    "es_charity_scam": {
        "lang": "es",
        "text": "Estamos recaudando fondos para niños enfermos. Necesitamos tu ayuda urgente. Dona ahora con tarjeta de crédito. Dame tu número de tarjeta y código de seguridad. Cada minuto cuenta."
    }
}

print("Downloading new batch of multilingual voice samples...")
print("=" * 60)

for name, data in samples.items():
    output_file = f"d:/hackathon/test_samples/batch2/{name}.mp3"
    print(f"Creating {name}.mp3 ({data['lang']})...")
    
    try:
        tts = gTTS(text=data["text"], lang=data["lang"])
        tts.save(output_file)
        print(f"  ✓ Saved: {output_file}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("=" * 60)
print("All samples downloaded!")
print(f"\nFiles saved to: d:/hackathon/test_samples/batch2/")
