"""
Test admin features: rules, blocklist, settings
"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

# First, login to get admin token
login_data = {
    "username": "testuser",
    "password": "testpass123"
}
r = requests.post(f"{API_BASE}/auth/login", json=login_data)
if r.status_code != 200:
    print("Login failed, trying to register...")
    register_data = {
        "email": "admin@test.com",
        "username": "adminuser",
        "password": "admin123",
        "full_name": "Admin User"
    }
    r = requests.post(f"{API_BASE}/auth/register", json=register_data)
    if r.status_code == 200:
        print("✓ Admin registered successfully")
        # Try login again
        login_data = {"username": "adminuser", "password": "admin123"}
        r = requests.post(f"{API_BASE}/auth/login", json=login_data)

token = r.json().get('access_token')
headers = {"Authorization": f"Bearer {token}"}

print("="*80)
print("TESTING ADMIN FEATURES")
print("="*80)

# Test 1: Create a fraud detection rule
print("\n1. Create fraud detection rules:")
rules = [
    {
        "name": "Banking Fraud Rule",
        "rule_type": "keyword",
        "keywords": ["bank account", "verify", "OTP", "pin", "cvv"],
        "description": "Detects banking fraud attempts",
        "is_active": True,
        "severity": "high"
    },
    {
        "name": "Tech Support Scam Rule",
        "rule_type": "keyword",
        "keywords": ["computer virus", "remote access", "microsoft", "windows support"],
        "description": "Detects tech support scams",
        "is_active": True,
        "severity": "high"
    },
    {
        "name": "Prize Scam Rule",
        "rule_type": "keyword",
        "keywords": ["won", "lottery", "prize", "claim", "congratulations"],
        "description": "Detects prize/lottery scams",
        "is_active": True,
        "severity": "medium"
    }
]

created_rules = []
for rule in rules:
    r = requests.post(f"{API_BASE}/admin/rules", json=rule, headers=headers)
    if r.status_code in [200, 201]:
        result = r.json()
        created_rules.append(result)
        print(f"   ✓ Created: {rule['name']} (ID: {result.get('id', 'N/A')})")
    else:
        print(f"   ✗ Failed to create {rule['name']}: {r.status_code}")

# Test 2: Get all rules
print("\n2. Retrieve all rules:")
r = requests.get(f"{API_BASE}/admin/rules", headers=headers)
if r.status_code == 200:
    all_rules = r.json()
    if isinstance(all_rules, list):
        print(f"   Total rules in database: {len(all_rules)}")
        for rule in all_rules[:5]:
            print(f"   - {rule.get('name', 'Unnamed')}: {len(rule.get('keywords', []))} keywords")
    else:
        print(f"   Rules: {all_rules}")
else:
    print(f"   Failed to retrieve rules: {r.status_code}")

# Test 3: Update a rule
if created_rules:
    print("\n3. Update rule status:")
    rule_id = created_rules[0].get('id')
    if rule_id:
        update_data = {"is_active": False}
        r = requests.patch(f"{API_BASE}/admin/rules/{rule_id}", json=update_data, headers=headers)
        if r.status_code == 200:
            print(f"   ✓ Disabled rule ID {rule_id}")
        else:
            print(f"   ✗ Failed to update rule: {r.status_code}")

# Test 4: Add numbers to blocklist
print("\n4. Add numbers to blocklist:")
blocklist_numbers = [
    {"phone_number": "+1-888-SCAM-001", "reason": "Known IRS scam number", "blocked_by": "admin"},
    {"phone_number": "+91-9999-FRAUD", "reason": "Banking fraud number", "blocked_by": "admin"},
    {"phone_number": "1-800-FAKE-999", "reason": "Tech support scam", "blocked_by": "admin"}
]

for number in blocklist_numbers:
    r = requests.post(f"{API_BASE}/admin/blocklist", json=number, headers=headers)
    if r.status_code in [200, 201]:
        print(f"   ✓ Blocked: {number['phone_number']}")
    else:
        print(f"   ✗ Failed to block {number['phone_number']}: {r.status_code} - {r.text[:100]}")

# Test 5: Get blocklist
print("\n5. Retrieve blocklist:")
r = requests.get(f"{API_BASE}/admin/blocklist", headers=headers)
if r.status_code == 200:
    blocklist = r.json()
    if isinstance(blocklist, list):
        print(f"   Total blocked numbers: {len(blocklist)}")
        for entry in blocklist[:3]:
            print(f"   - {entry.get('phone_number', 'N/A')}: {entry.get('reason', 'N/A')}")
    else:
        print(f"   Blocklist: {blocklist}")
else:
    print(f"   Failed to retrieve blocklist: {r.status_code}")

# Test 6: Test settings API (if available)
print("\n6. Test settings API:")
r = requests.get(f"{API_BASE}/admin/settings", headers=headers)
if r.status_code == 200:
    settings = r.json()
    print(f"   ✓ Retrieved settings: {list(settings.keys())[:5]}")
elif r.status_code == 404:
    print(f"   Settings endpoint not available")
else:
    print(f"   Failed: {r.status_code}")

print("\n" + "="*80)
print("ADMIN FEATURES TESTS COMPLETED")
print("="*80)
