import requests

PROD_API_URL = "https://scrapyfinalrelease-production.up.railway.app/api/v1"

print("🚀 Testing Production API Endpoint...\n")

# 1. Test root endpoint
print("1️⃣  Testing root endpoint...")
try:
    response = requests.get("https://scrapyfinalrelease-production.up.railway.app/", timeout=10)
    if response.status_code == 200:
        print(f"✅ Root endpoint accessible: {response.json()}")
    else:
        print(f"❌ Root endpoint returned {response.status_code}")
except Exception as e:
    print(f"❌ Failed to reach root endpoint: {e}")

# 2. Test API docs
print("\n2️⃣  Testing API docs endpoint...")
try:
    response = requests.get(f"{PROD_API_URL}/docs", timeout=10)
    if response.status_code == 200:
        print(f"✅ API docs accessible at {PROD_API_URL}/docs")
    else:
        print(f"⚠️  API docs returned {response.status_code}")
except Exception as e:
    print(f"❌ Failed to reach API docs: {e}")

# 3. Test unauthenticated request (should return 401)
print("\n3️⃣  Testing unauthenticated request (should return 401)...")
try:
    response = requests.post(
        f"{PROD_API_URL}/scrape",
        json={"url": "https://example.com", "mode": "guided", "selectors": {"title": "h1"}},
        timeout=10
    )
    if response.status_code == 401:
        error_data = response.json()
        print(f"✅ Correctly rejected with 401: {error_data.get('error', {}).get('message')}")
    else:
        print(f"⚠️  Expected 401, got {response.status_code}")
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n🎉 Production API Verification Complete!")
