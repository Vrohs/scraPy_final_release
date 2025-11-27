import requests
import concurrent.futures
import time

API_URL = "http://localhost:8000/api/v1"
TEST_API_KEY = "sk_test_f937fb1e5f1b6a0daecb6f3c3d450f19"
headers = {"X-API-Key": TEST_API_KEY}

def submit_job(job_num):
    """Submit a single scraping job."""
    try:
        response = requests.post(
            f"{API_URL}/scrape",
            json={
                "url": f"https://example.com",
                "mode": "guided",
                "selectors": {"title": "h1"}
            },
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            job_id = response.json()['job_id']
            return f"✅ Job {job_num}: {job_id}"
        else:
            return f"❌ Job {job_num}: {response.status_code}"
    except Exception as e:
        return f"❌ Job {job_num}: {str(e)}"

print("🚀 Stress Testing: Submitting 10 concurrent jobs...\n")

start_time = time.time()

# Submit 10 jobs concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(submit_job, i) for i in range(1, 11)]
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

elapsed = time.time() - start_time

print("\n📊 Results:")
for result in sorted(results):
    print(result)

print(f"\n⏱️  Total time: {elapsed:.2f}s")
print(f"✅ All {len([r for r in results if '✅' in r])} jobs submitted successfully!")
print(f"❌ {len([r for r in results if '❌' in r])} jobs failed")
