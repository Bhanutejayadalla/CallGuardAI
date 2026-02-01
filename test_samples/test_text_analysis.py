import requests
import json

# Test various text scenarios
test_texts = [
    {
        "name": "Prize Scam",
        "text": "Congratulations! You won a free iPhone 15. Click this link and enter your credit card details to claim your prize."
    },
    {
        "name": "Tech Support Scam",
        "text": "Your Microsoft Windows license has expired. Call this number immediately to renew or your computer will be locked permanently."
    },
    {
        "name": "UPI Scam",
        "text": "You have received a payment request of Rs.50,000. Accept the request now to receive money in your account."
    },
    {
        "name": "Job Offer Scam",
        "text": "Work from home opportunity! Earn $5000 per month. Pay $500 registration fee now to start working immediately."
    },
    {
        "name": "Safe Reminder",
        "text": "This is a friendly reminder that your dentist appointment is scheduled for tomorrow at 10 AM. Please arrive 10 minutes early."
    },
    {
        "name": "Safe Delivery",
        "text": "Your package from Amazon will be delivered today between 2-4 PM. No signature required. Track at amazon.com/tracking"
    }
]

print("=" * 70)
print("TEXT ANALYSIS TESTING")
print("=" * 70)

for test in test_texts:
    print(f"\nTest: {test['name']}")
    print(f"Text: {test['text'][:60]}...")
    
    try:
        r = requests.post('http://localhost:8000/api/v1/analyze/text', params={'text': test['text']})
        result = r.json()
        
        print(f"✓ Classification: {result['classification'].upper()}")
        print(f"✓ Risk Score: {result['risk_score']}/100")
        print(f"✓ Keywords: {', '.join(result['suspicious_keywords'][:5])}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 70)
