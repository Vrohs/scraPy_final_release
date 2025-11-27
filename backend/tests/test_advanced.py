from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_user


# Mock user
async def mock_get_current_user():
    return {"sub": "test_user_123"}

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

def test_create_api_key():
    response = client.post("/api/v1/api_keys/", json={"name": "Test Key"})
    if response.status_code != 200:
        print(f"Failed: {response.status_code} - {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "key" in data
    assert data["key"].startswith("sk_live_")
    print(f"\nCreated API Key: {data['key']}")
    return data["key"]

def test_create_webhook():
    response = client.post("/api/v1/webhooks/", json={
        "url": "https://example.com/webhook",
        "events": ["job.completed"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com/webhook"
    print(f"\nCreated Webhook ID: {data['id']}")

def test_api_key_usage():
    # 1. Create Key
    key = test_create_api_key()
    
    # 2. Use Key to access protected route (e.g. history or scrape)
    # We need to remove the override to test the REAL auth logic for API keys
    app.dependency_overrides = {} 
    
    # Note: We need to ensure the DB session in the dependency can find the key we just created.
    # Since TestClient and the App might use different sessions if not careful, 
    # but here they share the same engine/sessionmaker in app.core.database.
    
    # However, get_current_user is async, and TestClient is sync. 
    # The real app uses AsyncSession.
    # This might be flaky without a proper pytest-asyncio setup, but let's try the simple path first.
    
    response = client.get("/api/v1/history/all", headers={"X-API-Key": key})
    if response.status_code != 200:
        print(f"API Key Auth Failed: {response.text}")
    assert response.status_code == 200
    print("\nAPI Key Auth Success!")

if __name__ == "__main__":
    try:
        print("Testing API Key Creation...")
        key = test_create_api_key()
        
        print("Testing Webhook Creation...")
        test_create_webhook()
        
        # We skip the usage test in this simple script because mixing async DB + sync TestClient 
        # without proper fixture setup is prone to "Event loop is closed" errors.
        # But verifying creation confirms the DB write works.
        
    except Exception as e:
        print(f"Test Failed: {e}")
