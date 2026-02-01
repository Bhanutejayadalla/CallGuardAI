"""
Generate batch 3 of multilingual voice samples with different scam scenarios
"""
from gtts import gTTS
import os

# Create batch3 directory
os.makedirs('batch3', exist_ok=True)

# Different scam scenarios for batch 3
samples = {
    # Banking scams
    'en_bank_freeze': {
        'text': "This is an urgent alert from your bank. Your account has been temporarily frozen due to suspicious transactions. Please call us immediately at 1-800-555-0199 and provide your account number, PIN, and security code to unlock your account.",
        'lang': 'en',
        'category': 'scam'
    },
    'hi_credit_card': {
        'text': "Namaste, aapki credit card company se bol raha hun. Aapka credit card band ho gaya hai. Turant apna card number aur CVV bataiye nahi toh aapka card permanently block ho jayega.",
        'lang': 'hi',
        'category': 'scam'
    },
    
    # Government impersonation
    'en_medicare': {
        'text': "Hello, this is Medicare Administration. Your Medicare benefits will expire today unless you verify your information. Please provide your Medicare ID number and social security number immediately to avoid loss of benefits.",
        'lang': 'en',
        'category': 'scam'
    },
    'ta_govt_scheme': {
        'text': "Vanakkam, naan tamilnadu arasin tharaf irunthu pesuren. Ungaluku 50000 rupai subsidy kidaikkum. Ungal aadhar number, bank account details kodunga.",
        'lang': 'ta',
        'category': 'scam'
    },
    
    # Tech support scams
    'en_microsoft': {
        'text': "Warning! This is Microsoft Security. We detected a virus on your computer. Your files will be deleted in 30 minutes. Call this number immediately and give us remote access to fix the problem: 1-888-VIRUS-99.",
        'lang': 'en',
        'category': 'scam'
    },
    'te_internet': {
        'text': "Meeku internet company nundi pilusthunnanu. Mee internet connection lo problem undi. Mee router password ivvandi, leka mee connection cut avutundi.",
        'lang': 'te',
        'category': 'scam'
    },
    
    # Cryptocurrency/Investment scams  
    'en_crypto': {
        'text': "Congratulations! You have been selected for an exclusive Bitcoin investment opportunity. Invest just 500 dollars today and get 5000 dollars in 24 hours guaranteed. Send payment to this wallet address now before spots fill up.",
        'lang': 'en',
        'category': 'scam'
    },
    'es_inversion': {
        'text': "Hola, tengo una oportunidad de inversión increíble para usted. Puede ganar 10000 euros en solo una semana. Envíe su información bancaria ahora mismo para comenzar.",
        'lang': 'es',
        'category': 'scam'
    },
    
    # Safe calls
    'en_doctor': {
        'text': "Hello, this is Dr. Smith's office calling to confirm your appointment on Wednesday at 3 PM. Please call us back at 555-0123 if you need to reschedule. Thank you.",
        'lang': 'en',
        'category': 'safe'
    },
    'hi_reminder': {
        'text': "Aapko yeh reminder hai ki aapki car insurance renewal ki date aa rahi hai. Kripya hamare office mein aake documents complete karein.",
        'lang': 'hi',
        'category': 'safe'
    },
    'ta_school': {
        'text': "Vanakkam, naan ungal pillaiyin school irunthu pesuren. Naalai parent teacher meeting irukku. Kaalai 10 maniku varavum.",
        'lang': 'ta',
        'category': 'safe'
    },
    'fr_delivery': {
        'text': "Bonjour, votre colis est arrivé. Vous pouvez le récupérer au bureau de poste de votre quartier entre 9 heures et 17 heures.",
        'lang': 'fr',
        'category': 'safe'
    }
}

print("Generating batch 3 voice samples...")
success_count = 0
fail_count = 0

for filename, sample in samples.items():
    try:
        tts = gTTS(text=sample['text'], lang=sample['lang'], slow=False)
        output_path = f"batch3/{filename}.mp3"
        tts.save(output_path)
        print(f"✓ Generated: {output_path} ({sample['category']})")
        success_count += 1
    except Exception as e:
        print(f"✗ Failed to generate {filename}: {e}")
        fail_count += 1

print(f"\nBatch 3 complete: {success_count} generated, {fail_count} failed")
