"""
Test remaining endpoints: AI voice detection, status, user preferences
"""
import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8000/api/v1"

# Login to get token
login_data = {"username": "testuser", "password": "testpass123"}
r = requests.post(f"{API_BASE}/auth/login", json=login_data)
if r.status_code == 200:
    token = r.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Logged in successfully")
else:
    print("✗ Login failed")
    headers = {}

print("="*80)
print("TESTING REMAINING API ENDPOINTS")
print("="*80)

# Test 1: Check analysis status
print("\n1. Test analysis status endpoint:")
r = requests.get(f"{API_BASE}/calls/?limit=1")
if r.status_code == 200 and r.json()['calls']:
    call_id = r.json()['calls'][0]['call_id']
    r_status = requests.get(f"{API_BASE}/analyze/status/{call_id}")
    if r_status.status_code == 200:
        status = r_status.json()
        print(f"   ✓ Status for {call_id}: {status.get('status', 'N/A')}")
    else:
        print(f"   ✗ Failed to get status: {r_status.status_code}")
else:
    print("   No calls found to test status")

# Test 2: AI voice detection
print("\n2. Test AI voice detection:")
test_audio = Path("batch3/en_bank_freeze.mp3")
if test_audio.exists():
    with open(test_audio, 'rb') as f:
        files = {'file': ('test.mp3', f, 'audio/mpeg')}
        r = requests.post(f"{API_BASE}/ai-voice/detect", files=files)
    
    if r.status_code == 200:
        result = r.json()
        print(f"   ✓ AI Voice Detection:")
        print(f"     - Is AI: {result.get('is_ai_voice', False)}")
        print(f"     - Confidence: {result.get('confidence', 0):.2%}")
        print(f"     - Model: {result.get('model_version', 'N/A')}")
    else:
        print(f"   ✗ Failed: {r.status_code} - {r.text[:100]}")
else:
    print(f"   Test audio not found: {test_audio}")

# Test 3: Get AI voice detection statistics  
print("\n3. Test AI voice statistics:")
r = requests.get(f"{API_BASE}/ai-voice/stats")
if r.status_code == 200:
    stats = r.json()
    print(f"   ✓ AI Voice Stats:")
    print(f"     - Total analyzed: {stats.get('total_analyzed', 0)}")
    print(f"     - AI detected: {stats.get('ai_detected', 0)}")
    print(f"     - Detection rate: {stats.get('detection_rate', 0):.1%}")
elif r.status_code == 404:
    print("   Endpoint not available")
else:
    print(f"   ✗ Failed: {r.status_code}")

# Test 4: User profile
if headers:
    print("\n4. Test user profile endpoint:")
    r = requests.get(f"{API_BASE}/auth/me", headers=headers)
    if r.status_code == 200:
        user = r.json()
        print(f"   ✓ User profile:")
        print(f"     - Username: {user.get('username', 'N/A')}")
        print(f"     - Email: {user.get('email', 'N/A')}")
        print(f"     - Full name: {user.get('full_name', 'N/A')}")
    else:
        print(f"   ✗ Failed: {r.status_code}")

# Test 5: Update user preferences
if headers:
    print("\n5. Test user preferences update:")
    prefs = {
        "notification_enabled": True,
        "alert_threshold": 75,
        "language": "en"
    }
    r = requests.put(f"{API_BASE}/auth/me/preferences", json=prefs, headers=headers)
    if r.status_code == 200:
        print(f"   ✓ Updated preferences")
    elif r.status_code == 404:
        print("   Endpoint not available")
    else:
        print(f"   ✗ Failed: {r.status_code}")

# Test 6: Admin statistics
if headers:
    print("\n6. Test admin statistics:")
    r = requests.get(f"{API_BASE}/admin/stats", headers=headers)
    if r.status_code == 200:
        stats = r.json()
        print(f"   ✓ Admin stats:")
        print(f"     - Total calls: {stats.get('total_calls', 0)}")
        print(f"     - Total users: {stats.get('total_users', 0)}")
        print(f"     - Total rules: {stats.get('total_rules', 0)}")
    else:
        print(f"   ✗ Failed: {r.status_code}")

# Test 7: Initialize default rules
if headers:
    print("\n7. Test initialize default rules:")
    r = requests.post(f"{API_BASE}/admin/rules/init-defaults", headers=headers)
    if r.status_code == 200:
        result = r.json()
        print(f"   ✓ Default rules initialized: {result.get('message', 'Success')}")
    else:
        print(f"   ✗ Failed: {r.status_code} - {r.text[:100]}")

# Test 8: Delete a call
print("\n8. Test delete call:")
r = requests.get(f"{API_BASE}/calls/?limit=1&classification=safe")
if r.status_code == 200 and r.json()['calls']:
    call_to_delete = r.json()['calls'][0]['call_id']
    r_delete = requests.delete(f"{API_BASE}/calls/{call_to_delete}", headers=headers if headers else {})
    if r_delete.status_code == 200:
        print(f"   ✓ Deleted call: {call_to_delete}")
    else:
        print(f"   ✗ Failed to delete: {r_delete.status_code}")
else:
    print("   No safe calls found to delete")

print("\n" + "="*80)
print("REMAINING ENDPOINTS TESTS COMPLETED")
print("="*80)
