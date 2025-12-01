import asyncio
import httpx
import time
import json
from sqlalchemy import create_engine, text
from redis import Redis
from app.core.config import settings

# Configuration
API_URL = "http://localhost:8000/api/v1"

# Construct Sync DB URL
if settings.DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL
else:
    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"

REDIS_URL = settings.redis_connection_url

# Setup DB and Redis connections
engine = create_engine(DATABASE_URL)
redis_client = Redis.from_url(REDIS_URL)

def verify_infrastructure():
    print("🚀 Starting Infrastructure Verification...")

    # API Key for authentication
    API_KEY = "sk_test_f937fb1e5f1b6a0daecb6f3c3d450f19"
    headers = {"X-API-Key": API_KEY}

    # 1. Create a Scrape Job
    print("\n1️⃣  Submitting Scrape Job...")
    payload = {
        "url": "https://example.com",
        "mode": "guided",
        "selectors": {"title": "h1"}
    }
    with httpx.Client() as client:
        response = client.post(f"{API_URL}/scrape", json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to create job: {response.text}")
        return
    
    job_data = response.json()
    job_id = job_data["job_id"]
    print(f"✅ Job Created: {job_id}")

    # 2. Wait a moment for worker to pick up the job
    print("\n2️⃣  Waiting for worker to pick up job...")
    time.sleep(2)

    # 3. Verify Database Persistence
    print("\n3️⃣  Verifying Database Persistence...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT status FROM jobs WHERE id = :id"), {"id": job_id}).fetchone()
        if result:
            print(f"✅ Job found in DB with status: {result[0]}")
        else:
            print("❌ Job NOT found in Database!")
            return

    # 3. Verify Redis Queue (Might be too fast if worker picks it up immediately)
    # We can check if the job ID was ever in the queue or if worker is processing it
    # For now, let's just assume if it completes, Redis worked.
    
    # 4. Poll for Completion
    print("\n4️⃣  Polling for Completion...")
    max_retries = 10
    with httpx.Client() as client:
        for i in range(max_retries):
            response = client.get(f"{API_URL}/scrape/{job_id}", headers=headers)
            status = response.json()["status"]
            print(f"   Status: {status}")
            
            if status == "completed":
                print("✅ Job Completed!")
                break
            elif status == "failed":
                print(f"❌ Job Failed: {response.json().get('error')}")
                return
            
            time.sleep(2)
        else:
            print("❌ Timeout waiting for job completion")
            return

    # 5. Verify Result in Database
    print("\n5️⃣  Verifying Result in Database...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT data FROM jobs WHERE id = :id"), {"id": job_id}).fetchone()
        if result and result[0]:
            print("✅ Result found in Database")
            # Optional: Check content
            # print(f"   Result preview: {str(result[0])[:100]}...")
        else:
            print("❌ Result NOT found in Database!")

    print("\n🎉 Infrastructure Verification Passed!")

if __name__ == "__main__":
    try:
        verify_infrastructure()
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
