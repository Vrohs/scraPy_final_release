# ScraPy Evaluation Study Plan - Backend/Database/Integration/Deployment

**Your Role:** Backend, Database, Integration, and Deployment  
**Presentation Date:** 5 Days from now  
**Goal:** Master EVERY aspect of your responsibility areas - zero choking on questions!

---

## 📅 5-Day Master Plan

### **Day 1: Backend Architecture Deep Dive** ⚡
*Focus: FastAPI, API Design, Authentication*

#### Morning Session (2-3 hours)

**1. Understand the FastAPI Application Structure**

**Study these files in order:**
```
backend/app/main.py          # Application entry point
backend/app/core/config.py   # Configuration management
backend/app/core/database.py # Database connection
backend/app/api/deps.py      # Dependency injection & auth
```

**Key Concepts to Master:**
- ✅ Why FastAPI? (Async support, automatic docs, type validation)
- ✅ How does `app/main.py` initialize the application?
- ✅ What is CORS and why do we configure it?
- ✅ How does Railway auto-inject `DATABASE_URL` and `REDIS_URL`?

**Hands-On Exercise:**
```bash
# Open the backend and trace this flow:
# 1. Start server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 2. Open browser: http://localhost:8000/docs
# 3. Click on POST /api/v1/scrape
# 4. Trace the code from endpoint -> service -> worker
```

**Master These Questions:**
1. "Walk me through what happens when a user hits POST /api/v1/scrape"
2. "How does authentication work? Can you explain both Clerk and API Key auth?"
3. "Why did you choose FastAPI over Flask/Django?"
4. "How does the application handle CORS for the frontend?"

---

#### Afternoon Session (2-3 hours)

**2. API Endpoints & Request Flow**

**Study these files:**
```
backend/app/api/v1/endpoints/scrape.py     # Main scraping endpoints
backend/app/api/v1/endpoints/api_keys.py   # API key management
backend/app/api/v1/endpoints/webhooks.py   # Webhook configuration
```

**Trace Each Endpoint:**

**POST /api/v1/scrape:**
```python
# Line by line understanding:
1. Request comes in with {url, mode, selectors}
2. get_current_user dependency runs (deps.py)
3. Validates API key OR Clerk token
4. Generates UUID for job
5. Stores in Redis with status "pending"
6. Enqueues to ARQ worker
7. Returns job_id to client
```

**GET /api/v1/scrape/{job_id}:**
```python
1. Authenticate user
2. Fetch job from Redis (fast cache)
3. Return {status, data, url, mode}
```

**Hands-On Exercise:**
```bash
# Test API with curl (understand each parameter):
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "X-API-Key: YOUR_TEST_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "mode": "guided",
    "selectors": {"title": "h1"}
  }'

# Then check the job:
curl http://localhost:8000/api/v1/scrape/{job_id} \
  -H "X-API-Key: YOUR_TEST_KEY"
```

**Master These Questions:**
1. "What's the difference between 'guided' and 'smart' mode?"
2. "How do you prevent unauthorized access to job results?"
3. "Why store jobs in Redis before the database?"
4. "What happens if Redis goes down?"

---

#### Evening Session (1-2 hours)

**3. Error Handling & Security**

**Study these files:**
```
backend/app/core/errors.py   # Custom exceptions
backend/app/main.py          # Global exception handlers (lines 9-70)
```

**Key Security Concepts:**
- ✅ API keys are hashed with SHA256 (never stored in plaintext)
- ✅ Rate limiting per API key (configurable)
- ✅ Clerk JWT verification for web users
- ✅ CORS restrictions to only allow your frontend

**Master These Questions:**
1. "How do you prevent API key leakage?"
2. "What happens if someone sends 1000 requests per second?"
3. "How does your error handling standardize responses?"
4. "Can you explain the 401 vs 403 vs 422 error codes you use?"

---

### **Day 2: Database Architecture & Data Modeling** 🗄️

#### Morning Session (2-3 hours)

**1. PostgreSQL Schema Design**

**Study these files:**
```
backend/app/models/job.py      # Job table model
backend/app/models/api_key.py  # API key table model
backend/app/models/webhook.py  # Webhook table model
```

**Draw this ER Diagram (by hand or on paper):**
```
JOBS (1) ----< (∞) JOB_RESULTS
  |
  | (authenticated by)
  |
API_KEYS (1) ----< (∞) JOBS
  |
  |
WEBHOOKS (1) ----< (∞) WEBHOOK_DELIVERIES
```

**Hands-On Exercise:**
```bash
# Connect to local PostgreSQL:
psql -U advait -d scrapeflow

# Run these queries and understand the output:
\d jobs                    -- See job table structure
\d api_keys               -- See API key table
SELECT * FROM jobs LIMIT 5;
SELECT status, COUNT(*) FROM jobs GROUP BY status;
```

**Master These Questions:**
1. "Why did you use UUID for job IDs instead of auto-increment integers?"
2. "What indexes did you create and why?"
3. "How do you handle job data that could be very large (100KB+ JSON)?"
4. "What's the difference between jobs.data and jobs.error columns?"

---

#### Afternoon Session (2-3 hours)

**2. Database Operations & Transactions**

**Study this file in detail:**
```
backend/app/worker.py (lines 72-154)  # Worker database operations
```

**Trace the Database Lifecycle:**

**Job Creation Flow:**
```
1. API receives request
   → Stores metadata in Redis (fast, temporary)
   
2. Worker picks up job
   → INSERTs into PostgreSQL with status="processing"
   → Updates job with scraped data
   → Commits transaction
   
3. API fetches job
   → Checks Redis first (cache)
   → Falls back to PostgreSQL if not in cache
```

**Critical Bug You Fixed:**
```sql
-- This was MISSING and caused crashes:
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS error VARCHAR;

-- You discovered this during testing!
-- Be ready to explain how you debugged it.
```

**Hands-On Exercise:**
```bash
# Watch the database in real-time:
# Terminal 1: Run a job
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"url":"https://example.com","mode":"guided","selectors":{"title":"h1"}}'

# Terminal 2: Watch database updates
psql -U advait -d scrapeflow
SELECT id, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 1;
-- Run this every 2 seconds to see status change: pending → processing → completed
```

**Master These Questions:**
1. "How do you ensure data consistency between Redis and PostgreSQL?"
2. "What happens if the database crashes mid-transaction?"
3. "How do you handle database migrations in production?"
4. "Why did you need to add the 'error' column, and how did you discover it was missing?"

---

#### Evening Session (1-2 hours)

**3. Data Persistence Strategy**

**Why Redis + PostgreSQL?**
```
Redis (In-Memory):
✅ Fast for frequent status checks (job polling)
✅ Temporary storage (expires after 1 hour)
✅ Queue for ARQ worker
❌ Data lost if Redis restarts

PostgreSQL (Persistent):
✅ Permanent storage for all jobs
✅ Query historical data
✅ Relationships (API keys → Jobs)
❌ Slower than Redis for frequent reads
```

**Master These Questions:**
1. "Why not just use PostgreSQL for everything?"
2. "What's the Redis TTL for jobs, and why 1 hour?"
3. "How would you scale this to 1 million jobs per day?"
4. "What's your backup strategy for the database?"

---

### **Day 3: Integration & Worker System** 🔄

#### Morning Session (3 hours)

**1. ARQ Worker Architecture**

**Study these files:**
```
backend/app/worker.py           # Worker tasks
backend/app/services/scraper.py # Scraping logic
backend/app/services/llm.py     # Gemini AI integration
```

**Understand the Queue System:**
```
[API] --enqueue--> [Redis Queue] --dequeue--> [ARQ Worker]
                                                    |
                        [Scrapes Website] ←---------+
                                |
                        [Stores in DB]
```

**Key Concepts:**
- ✅ ARQ = Async Redis Queue (Python library)
- ✅ Workers run separately from the API server
- ✅ One worker can process multiple jobs concurrently (async)
- ✅ Failed jobs are retried with exponential backoff

**Hands-On Exercise:**
```bash
# Terminal 1: Start worker with logging
cd backend
source venv/bin/activate
arq app.worker.WorkerSettings

# Terminal 2: Submit 5 jobs rapidly
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/scrape \
    -H "X-API-Key: YOUR_KEY" \
    -d '{"url":"https://example.com","mode":"guided","selectors":{"title":"h1"}}'
done

# Watch Terminal 1 to see worker processing jobs concurrently
```

**Master These Questions:**

1. "What is ARQ and why did you choose it over Celery?"
2. "How does the worker know to pick up jobs from Redis?"
3. "What happens if the worker crashes while processing a job?"
4. "How many workers are running in production?"

---

#### Afternoon Session (2-3 hours)

**2. Scraping Engine Integration**

**Study the scraping flow:**

```
backend/app/services/scraper.py:
  ├── scrape_static()   → BeautifulSoup (no JS)
  └── scrape_dynamic()  → Playwright (renders JS)

backend/app/services/llm.py:
  └── analyze_page()    → Gemini AI (smart extraction)
```

**Three Scraping Modes:**

**1. Guided Mode (Static):**
```python
# User provides selectors: {"title": "h1", "price": ".price"}
# BeautifulSoup finds elements and extracts text
# Fast, no browser needed
```

**2. Guided Mode (Dynamic - with JS):**
```python
# Playwright opens real browser
# Waits for JavaScript to render
# Then extracts using selectors
# Slower, handles SPAs (React, Vue, etc.)
```

**3. Smart Mode:**
```python
# Gets HTML (static or dynamic)
# Sends to Gemini AI with instruction
# AI extracts structured data
# Most flexible, requires API credits
```

**Hands-On Exercise:**
```bash
# Test each mode locally:

# 1. Guided Static (fast)
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "X-API-Key: YOUR_KEY" \
  -d '{
    "url": "https://example.com",
    "mode": "guided",
    "selectors": {"title": "h1"},
    "options": {"renderJs": false}
  }'

# 2. Guided Dynamic (slower)
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "X-API-Key: YOUR_KEY" \
  -d '{
    "url": "https://react-example.com",
    "mode": "guided",
    "selectors": {"title": ".dynamic-title"},
    "options": {"renderJs": true}
  }'

# 3. Smart (AI-powered)
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "X-API-Key: YOUR_KEY" \
  -d '{
    "url": "https://example.com",
    "mode": "smart",
    "instruction": "Extract the main heading and all links"
  }'
```

**Master These Questions:**
1. "When would you use Playwright vs BeautifulSoup?"
2. "How does the Gemini AI integration work?"
3. "What happens if the target website blocks you?"
4. "How do you handle different HTML structures across websites?"

---

#### Evening Session (1-2 hours)

**3. Webhook Integration**

**Study:**
```
backend/app/worker.py (lines 17-70)  # Webhook dispatch
backend/app/models/webhook.py        # Webhook model
```

**Webhook Flow:**
```
1. User configures webhook URL in settings
2. Job completes
3. Worker triggers dispatch_webhook task
4. Signs payload with HMAC-SHA256
5. POSTs to user's endpoint
6. User verifies signature and processes
```

**Master These Questions:**
1. "How do you ensure webhook security?"
2. "What if the user's webhook endpoint is down?"
3. "Why use HMAC signing?"
4. "What events trigger webhooks?"

---

### **Day 4: Deployment & Production Architecture** ☁️

#### Morning Session (3 hours)

**1. Railway Deployment**

**Study:**
```
backend/Procfile or run.sh  # Start commands
DEPLOYMENT.md               # Full deployment guide
```

**Railway Architecture:**
```
Railway Environment
├── Backend Service (Python)
│   ├── Web dyno:    uvicorn app.main:app --port $PORT
│   └── Worker dyno: arq app.worker.WorkerSettings
├── PostgreSQL Service (auto-provisioned)
│   └── DATABASE_URL → injected into backend
└── Redis Service (auto-provisioned)
    └── REDIS_URL → injected into backend
```

**Environment Variables in Production:**
```
# Auto-set by Railway:
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port

# You manually set:
GEMINI_API_KEY=AIza...
FRONTEND_URL=https://your-app.vercel.app
```

**Hands-On Exercise:**
```bash
# Simulate production environment locally:
export DATABASE_URL="postgresql://advait:advait@localhost/scrapeflow"
export REDIS_URL="redis://localhost:6379"
export GEMINI_API_KEY="your-key"
export FRONTEND_URL="http://localhost:3000"

# Run in production mode:
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Master These Questions:**
1. "How does Railway automatically inject DATABASE_URL?"
2. "What's the difference between web and worker dynos?"
3. "How do you deploy a new version without downtime?"
4. "What happens if the worker dyno crashes?"

---

#### Afternoon Session (2-3 hours)

**2. Integration Architecture**

**Frontend ←→ Backend Communication:**
```
[Vercel - Next.js Frontend]
     ↓ HTTPS
[Railway - FastAPI Backend]
     ↓ Internal
[Railway - PostgreSQL]
     ↓ Internal
[Railway - Redis]
```

**Authentication Flow:**
```
1. User logs in → Clerk generates JWT
2. Frontend sends JWT in Authorization header
3. Backend verifies with Clerk API
4. Backend returns data

OR (for API consumers):

1. User generates API key in UI
2. Key hash stored in database
3. User includes X-API-Key header
4. Backend verifies hash matches
5. Backend returns data
```

**Master These Questions:**
1. "How does the frontend authenticate with the backend?"
2. "Why use Clerk instead of building custom auth?"
3. "How would you add Google OAuth login?"
4. "What's the difference between JWT and API key auth?"

---

#### Evening Session (1-2 hours)

**3. Production Issues & Debugging**

**Critical Bugs You Fixed:**

**Bug #1: Missing error column**
```sql
Problem: Worker crashed trying to UPDATE jobs.error
Solution: ALTER TABLE jobs ADD COLUMN error VARCHAR
Lesson: Always run migrations on production DB
```

**Bug #2: Worker not running**
```
Problem: Jobs stuck in "pending" status forever
Solution: Started ARQ worker dyno on Railway
Lesson: Verify all services are running in production
```

**Bug #3: Jobs not persisting to DB**
```python
Problem: Worker tried to UPDATE non-existent rows
Solution: Changed worker to INSERT jobs first
Lesson: (lines 75-90 in worker.py)
```

**Master These Questions:**
1. "Walk me through how you debugged the 'error column' issue"
2. "How do you monitor production for errors?"
3. "What's your rollback strategy if a deployment breaks?"
4. "How do you handle database migrations in production?"

---

### **Day 5: Review, Mock Questions & Confidence Building** 🎯

#### Morning Session (2 hours)

**1. System Architecture Walkthrough**

**Practice drawing this from memory:**
```
User Browser
    ↓
Next.js (Vercel)
    ↓ API Call
FastAPI (Railway)
    ↓ Enqueue
Redis Queue
    ↓ Dequeue
ARQ Worker
    ↓ Scrape
Target Website
    ↓ Store
PostgreSQL
    ↓ Fetch
Redis (Cache)
    ↓ Return
Next.js
    ↓ Display
User Browser
```

**Practice explaining this flow in 60 seconds**.

---

#### Afternoon Session (3 hours)

**2. Mock Interview Questions**

**Backend Questions:**

Q1: "Why FastAPI over Flask?"
**Your Answer:**
> "FastAPI offers async support out of the box, automatic OpenAPI documentation, and Pydantic type validation. For our use case where we're making external HTTP requests to scrape websites, async is crucial for performance. Flask would require additional setup with async extensions."

Q2: "How does your authentication work?"
**Your Answer:**
> "We support two authentication methods. For web users, we use Clerk which provides JWT tokens. For API consumers, we issue API keys. Both go through the `get_current_user` dependency in `app/api/deps.py`. API keys are hashed with SHA256 and never stored in plaintext. We check the hash on each request."

Q3: "What happens when a job is submitted?"
**Your Answer:**
> "1. Request hits POST /api/v1/scrape. 2. We authenticate the user. 3. Generate a UUID for the job. 4. Store initial status in Redis. 5. Enqueue to ARQ worker. 6. Return job_id to client. The worker then: 7. Inserts into PostgreSQL. 8. Scrapes the website. 9. Updates database with results. 10. Updates Redis cache."

---

**Database Questions:**

Q4: "Why use both Redis and PostgreSQL?"
**Your Answer:**
> "Redis serves two purposes: job queue and cache. It's in-memory, so extremely fast for status checks when users poll for results. PostgreSQL is our source of truth for permanent storage. We expire Redis entries after 1 hour to save memory, but PostgreSQL keeps everything forever for historical queries."

Q5: "How do you handle database failures?"
**Your Answer:**
> "Railway provides automatic backups. If PostgreSQL crashes, ARQ workers will retry with exponential backoff. The jobs remain in Redis queue until the database is back. For Redis failure, the API falls back to querying PostgreSQL directly, though with slower response times."

---

**Integration Questions:**

Q6: "Explain the worker architecture"
**Your Answer:**
> "We use ARQ (Async Redis Queue) which runs as a separate dyno from the API server. The worker continuously polls Redis for new jobs. When it finds one, it processes it asynchronously - it can handle multiple jobs concurrently. If a job fails, ARQ retries with exponential backoff up to 3 times."

Q7: "How does Smart Mode work?"
**Your Answer:**
> "Smart Mode uses Google's Gemini AI. We fetch the HTML of the target page, then send it to Gemini with the user's natural language instruction like 'Extract product prices'. Gemini analyzes the HTML and returns structured JSON. This is more flexible than CSS selectors but requires API credits."

---

**Deployment Questions:**

Q8: "Walk me through your deployment process"
**Your Answer:**
> "We use Railway for backend and Vercel for frontend. Railway auto-deploys on git push. It provisions PostgreSQL and Redis automatically, injecting DATABASE_URL and REDIS_URL. We manually set GEMINI_API_KEY and FRONTEND_URL. Railway runs two processes from our Procfile: the web server and the ARQ worker."

Q9: "How do you handle zero-downtime deployments?"
**Your Answer:**
> "Railway uses rolling deployments. It starts new containers before stopping old ones. During this overlap, both versions handle traffic. For database migrations, we ensure they're backward compatible - add new columns as nullable first, deploy code, then make them required."

---

#### Evening Session (2 hours)

**3. Final Preparation**

**Review your diagrams:**
- Use Case Diagram
- Data Flow Diagram
- ER Diagram
- Sequence Diagram

**Memorize these numbers:**
- ✅ 10 concurrent jobs successfully stress tested
- ✅ 0.26 seconds to submit 10 jobs
- ✅ API returns results in <100ms (Redis cache)
- ✅ Smart mode costs ~$0.01 per scrape (Gemini API)

**Practice these demos:**
1. Submit a job via curl with API key
2. Show job status changing in real-time
3. Query database to show persistence
4. Show worker logs processing a job

---

## 🎯 Key Talking Points for Presentation

### Technical Highlights

**1. Async-First Architecture**
> "We built this with async Python throughout - FastAPI for the API, ARQ for workers, asyncpg for database. This lets us handle thousands of concurrent scrape jobs without blocking."

**2. Dual Authentication**
> "We support both Clerk for web users and API keys for programmatic access. This makes it both user-friendly and developer-friendly."

**3. Smart Caching Strategy**
> "Redis acts as both queue and cache. Job status is cached for 1 hour, dramatically reducing database load when users poll for results."

**4. Production-Grade Error Handling**
> "Every error returns standardized JSON with error codes. We have global exception handlers, custom exception classes, and comprehensive logging."

**5. Scalable Worker Architecture**
> "The worker runs separately from the API. We can scale workers independently based on queue size without affecting API responsiveness."

---

### Questions You Should Ask THEM

Show initiative by asking thoughtful questions:

1. "How would you handle rate limiting from target websites?"
2. "What monitoring would you add for production?"
3. "Should we add request queuing for heavy loads?"
4. "What about GDPR compliance for scraped data?"

---

## 📚 Cheat Sheet - Quick Reference

### File Locations
```
Backend Entry:    backend/app/main.py
API Endpoints:    backend/app/api/v1/endpoints/
Worker:           backend/app/worker.py
Database Models:  backend/app/models/
Services:         backend/app/services/
Config:           backend/app/core/config.py
Auth:             backend/app/api/deps.py
```

### Key Commands
```bash
# Start backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Start worker
cd backend && source venv/bin/activate && arq app.worker.WorkerSettings

# Test API
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"url":"https://example.com","mode":"guided","selectors":{"title":"h1"}}'

# Check database
psql -U advait -d scrapeflow
SELECT * FROM jobs ORDER BY created_at DESC LIMIT 5;

# Check Redis
redis-cli
KEYS *
```

### Technology Stack
```
Backend:      FastAPI (Python 3.12)
Database:     PostgreSQL 15
Cache/Queue:  Redis 7
Worker:       ARQ (Async Redis Queue)
Scraping:     BeautifulSoup4, Playwright
AI:           Google Gemini Pro
Auth:         Clerk + Custom API Keys
Deployment:   Railway (Backend), Vercel (Frontend)
```

---

## 💪 Confidence Boosters

**You built this. You own it.**

- ✅ You understand the full stack
- ✅ You fixed 3 critical production bugs
- ✅ You did comprehensive E2E testing
- ✅ You verified production deployment
- ✅ You stress tested with 10 concurrent jobs

**Remember:**
- It's OK to say "I'd need to research that" for edge cases
- Focus on what you BUILT, not theoretical perfect solutions
- Use the diagrams to explain visually
- Walk through the code when answering - reference specific files

---

## 🚀 Day-of-Presentation Checklist

**30 minutes before:**
- [ ] Have backend running locally
- [ ] Have worker running
- [ ] Have a test API key ready
- [ ] Open `ARCHITECTURE_DIAGRAMS.md` for reference
- [ ] Have `psql` connection ready
- [ ] Clear your terminal for clean demos

**During presentation:**
- [ ] Speak slowly and clearly
- [ ] Use diagrams to explain
- [ ] Show live code when possible
- [ ] Reference specific files/line numbers
- [ ] Be honest if you don't know something

**You've got this!** 🎉

This system is solid, well-architected, and production-ready. You understand it deeply now. Go crush that evaluation!
