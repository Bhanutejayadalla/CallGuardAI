"""
Test various call history filters and search features
"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

print("="*80)
print("TESTING CALL HISTORY FILTERS & SEARCH")
print("="*80)

# Test 1: Filter by classification
print("\n1. Filter by classification (phishing):")
r = requests.get(f"{API_BASE}/calls/?classification=phishing&limit=5")
phishing_calls = r.json()['calls']
print(f"   Found {len(phishing_calls)} phishing calls")
for call in phishing_calls[:3]:
    print(f"   - {call['call_id']}: Risk {call['risk_score']}")

# Test 2: Filter by minimum risk score
print("\n2. Filter by minimum risk score (≥90):")
r = requests.get(f"{API_BASE}/calls/?min_risk_score=90&limit=10")
high_risk_calls = r.json()['calls']
print(f"   Found {len(high_risk_calls)} high-risk calls")
for call in high_risk_calls[:5]:
    print(f"   - {call['call_id']}: {call['classification']} ({call['risk_score']})")

# Test 3: Filter by status
print("\n3. Filter by status (completed):")
r = requests.get(f"{API_BASE}/calls/?status=completed&limit=5")
completed_calls = r.json()['calls']
print(f"   Found {len(completed_calls)} completed calls")

# Test 4: Pagination
print("\n4. Test pagination:")
r1 = requests.get(f"{API_BASE}/calls/?limit=5&skip=0")
r2 = requests.get(f"{API_BASE}/calls/?limit=5&skip=5")
page1 = r1.json()['calls']
page2 = r2.json()['calls']
print(f"   Page 1: {len(page1)} calls (IDs: {[c['call_id'][-4:] for c in page1[:3]]})")
print(f"   Page 2: {len(page2)} calls (IDs: {[c['call_id'][-4:] for c in page2[:3]]})")

# Test 5: Get call count
print("\n5. Get total call count:")
r = requests.get(f"{API_BASE}/calls/count")
count_data = r.json()
print(f"   Total calls: {count_data.get('count', 0)}")

# Test 6: Search by keyword (if available)
print("\n6. Test call detail retrieval:")
if phishing_calls:
    call_id = phishing_calls[0]['call_id']
    r = requests.get(f"{API_BASE}/calls/{call_id}")
    detail = r.json()
    print(f"   Retrieved call {call_id}")
    print(f"   Transcript length: {len(detail.get('transcript', ''))} chars")
    print(f"   Fraud indicators: {len(detail.get('fraud_indicators', []))}")
    print(f"   Suspicious keywords: {len(detail.get('suspicious_keywords', []))}")

print("\n" + "="*80)
print("FILTER & SEARCH TESTS COMPLETED")
print("="*80)
