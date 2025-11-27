import requests
import hashlib

API_URL = "http://localhost:8000/api/v1"

# Use the test API key we created earlier
TEST_API_KEY = "sk_test_f937fb1e5f1b6a0daecb6f3c3d450f19"

print("🔑 Testing API Key Functionality...\n")

# 1. Test authenticated request
print("1️⃣  Testing authenticated request with API key...")
headers = {"X-API-Key": TEST_API_KEY}
response = requests.post(
    f"{API_URL}/scrape",
    json={"url": "https://example.com", "mode": "guided", "selectors": {"title": "h1"}},
    headers=headers
)

if response.status_code == 200:
    print(f"✅ Authenticated request successful! Job ID: {response.json()['job_id']}")
else:
    print(f"❌ Authenticated request failed: {response.status_code} - {response.text}")

# 2. Test request without API key (should fail with 401)
print("\n2️⃣  Testing request without API key (should fail with 401)...")
response = requests.post(
    f"{API_URL}/scrape",
    json={"url": "https://example.com", "mode": "guided", "selectors": {"title": "h1"}}
)

if response.status_code == 401:
    print(f"✅ Correctly rejected unauthenticated request: {response.json()['error']['message']}")
else:
    print(f"❌ Expected 401, got {response.status_code}")

# 3. Test request with invalid API key (should fail with 401)
print("\n3️⃣  Testing request with invalid API key (should fail with 401)...")
headers = {"X-API-Key": "sk_test_invalid_key_12345"}
response = requests.post(
    f"{API_URL}/scrape",
    json={"url": "https://example.com", "mode": "guided", "selectors": {"title": "h1"}},
    headers=headers
)

if response.status_code == 401:
    print(f"✅ Correctly rejected invalid API key: {response.json()['error']['message']}")
else:
    print(f"❌ Expected 401, got {response.status_code}")

print("\n🎉 API Key Testing Complete!")
