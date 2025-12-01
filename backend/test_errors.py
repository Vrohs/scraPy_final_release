import httpx

BASE_URL = "http://localhost:8000/api/v1"

def test_404():
    print("Testing 404 Not Found...")
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/nonexistent")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 404
        assert response.json()["success"] is False
        assert response.json()["error"]["code"] == "HTTP_ERROR"

def test_validation_error():
    print("\nTesting Validation Error...")
    # Assuming there's an endpoint that requires data, e.g., /scrape
    # Sending empty body to trigger validation error
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/scrape", json={})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 422
        assert response.json()["success"] is False
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

if __name__ == "__main__":
    try:
        test_404()
        test_validation_error()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
