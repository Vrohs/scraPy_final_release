# scraPy Backend API

**Production-grade FastAPI backend with async processing and AI-powered scraping**

---

## Architecture

### Components

- **FastAPI Server** - REST API with auto-generated docs
- **ARQ Worker** - Async background job processing
- **PostgreSQL** - Persistent data storage
- **Redis** - Job queue & caching
- **Playwright** - Dynamic content scraping
- **Google Gemini** - AI-powered extraction

### API Layers

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
├─────────────────────────────────────────┤
│  Authentication (Clerk JWT / API Keys)  │
├─────────────────────────────────────────┤
│  Rate Limiting (Redis)                  │
├─────────────────────────────────────────┤
│  Request Validation (Pydantic)          │
├─────────────────────────────────────────┤
│  Business Logic (Services)              │
├─────────────────────────────────────────┤
│  Data Access (SQLAlchemy Async)         │
└─────────────────────────────────────────┘
```

---

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Environment Setup

Create `.env` file:

```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=scrapy

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
GEMINI_API_KEY=your_gemini_api_key

# Authentication
CLERK_ISSUER_URL=https://your-app.clerk.accounts.dev

# CORS
FRONTEND_URL=http://localhost:3000

# App Config
PROJECT_NAME=scraPy API
API_V1_STR=/api/v1
```

### Running Services

```bash
# Terminal 1: API Server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: ARQ Worker
arq app.worker.WorkerSettings
```

### Verify

- **API:** http://localhost:8000/
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                 # Dependencies (auth, db)
│   │   └── v1/
│   │       ├── api.py              # Router aggregation
│   │       └── endpoints/
│   │           ├── scrape.py       # Scraping endpoints
│   │           ├── api_keys.py     # API key CRUD
│   │           └── webhooks.py     # Webhook management
│   ├── core/
│   │   ├── config.py              # Settings (Pydantic)
│   │   ├── database.py            # Async DB connection
│   │   ├── redis.py               # Redis pool
│   │   ├── logging.py             # Structured logging
│   │   └── ratelimit.py           # Rate limiter
│   ├── models/
│   │   ├── job.py                 # Job SQLAlchemy model
│   │   ├── api_key.py             # API Key model
│   │   └── webhook.py             # Webhook model
│   ├── services/
│   │   ├── scraper.py             # Scraping logic
│   │   └── llm.py                 # Gemini integration
│   ├── main.py                    # FastAPI app
│   └── worker.py                  # ARQ worker
├── tests/
│   ├── test_e2e_infrastructure.py  # Full flow test
│   ├── test_api_key.py             # API key tests
│   └── test_production_api.py      # Production tests
├── requirements.txt
├── Procfile                        # Railway deployment
└── railway.json                    # Railway config
```

---

## API Endpoints

### Authentication

**Methods:**
1. **API Key:** `X-API-Key: sk_live_xxx`
2. **JWT Token:** `Authorization: Bearer <token>`

### Scraping

#### Create Job
```http
POST /api/v1/scrape
Content-Type: application/json
X-API-Key: sk_live_xxx

{
  "url": "https://example.com",
  "mode": "guided",
  "selectors": { "title": "h1" },
  "options": { "renderJs": false }
}
```

#### Get Job Status
```http
GET /api/v1/scrape/{job_id}
X-API-Key: sk_live_xxx
```

#### Save Job
```http
POST /api/v1/scrape/{job_id}/save
X-API-Key: sk_live_xxx
```

#### Get History
```http
GET /api/v1/scrape/history/all
Authorization: Bearer <token>
```

### API Keys

#### Create API Key
```http
POST /api/v1/api_keys
Authorization: Bearer <token>

{ "name": "My API Key" }
```

#### List Keys
```http
GET /api/v1/api_keys
Authorization: Bearer <token>
```

#### Revoke Key
```http
DELETE /api/v1/api_keys/{key_id}
Authorization: Bearer <token>
```

### Webhooks

#### Create Webhook
```http
POST /api/v1/webhooks
Authorization: Bearer <token>

{
  "url": "https://your-app.com/webhook",
  "events": ["job.completed"]
}
```

#### List Webhooks
```http
GET /api/v1/webhooks
Authorization: Bearer <token>
```

---

## Security Features

### SSRF Protection

Blocks requests to:
- Private IP ranges: `10.x.x.x`, `192.168.x.x`, `172.16.x.x`
- Localhost: `127.0.0.1`, `::1`, `localhost`
- Link-local: `169.254.x.x`

**Implementation:** `app/api/v1/endpoints/scrape.py`

### Rate Limiting

```python
# Per-API-key limits stored in Redis
class ApiKey:
    rate_limit: int = 60  # requests per minute
```

**Implementation:** `app/core/ratelimit.py`

### Request Size Limits

- **Maximum Payload:** 10 MB
- Returns `413 Payload Too Large` if exceeded

**Implementation:** `app/main.py` (RequestSizeLimitMiddleware)

### Input Validation

```python
class ScrapeRequest(BaseModel):
    url: str = Field(max_length=2048)
    mode: Literal["guided", "smart"]
    selectors: Optional[Dict] = Field(max_length=50)
    instruction: Optional[str] = Field(max_length=5000)
```

---

## Database Models

### Job

```python
class Job(Base):
    __tablename__ = "jobs"
    
    id: str  # UUID
    url: str
    mode: str  # "guided" | "smart"
    status: str  # "pending" | "processing" | "completed" | "failed"
    data: Dict  # Extracted results
    error: Optional[str]
    created_at: datetime
```

### API Key

```python
class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id: str
    key_prefix: str  # First 12 chars
    key_hash: str  # SHA-256 hash
    user_id: str
    name: str
    is_active: bool
    rate_limit: int
    usage_count: int
    created_at: datetime
```

### Webhook

```python
class Webhook(Base):
    __tablename__ = "webhooks"
    
    id: str
    url: str
    events: List[str]  # ["job.completed"]
    secret: str  # HMAC signing
    user_id: str
    is_active: bool
    created_at: datetime
```

---

## Worker Tasks

### Scrape Task

```python
async def scrape_task(
    ctx, 
    job_id: str,
    url: str,
    mode: str,
    selectors: dict = None,
    instruction: str = None,
    options: dict = None,
    user_id: str = None
):
    # 1. Scrape content (httpx or Playwright)
    # 2. Extract data (selectors or AI)
    # 3. Save to DB and cache
    # 4. Dispatch webhook if configured
```

### Webhook Dispatch

```python
async def dispatch_webhook(
    ctx,
    job_id: str,
    user_id: str
):
    # 1. Fetch job and webhooks
    # 2. Sign payload with HMAC
    # 3. POST to webhook URL
```

---

## Logging

### Structured Format

```python
from app.core.logging import logger, log_job_created

log_job_created(job_id, url, mode, user_id)
# Output: 2025-12-01 21:45:30 - scrapy - INFO - Job created: abc-123 | URL: https://example.com | Mode: guided | User: user_xxx
```

### Available Log Functions

- `log_job_created(job_id, url, mode, user_id)`
- `log_job_completed(job_id, duration)`
- `log_job_failed(job_id, error)`
- `log_api_key_created(key_id, user_id, name)`
- `log_api_key_revoked(key_id, user_id)`
- `log_webhook_created(webhook_id, url, user_id)`
- `log_webhook_dispatched(job_id, url, success)`
- `log_rate_limit_exceeded(identifier)`
- `log_ssrf_attempt(url, user_id)`

---

## Testing

### E2E Infrastructure Test

```bash
python tests/test_e2e_infrastructure.py
```

Tests:
- Job creation
- Worker processing
- Database persistence
- Redis caching
- Job completion

### API Key Test

```bash
python tests/test_api_key.py
```

Tests:
- Authenticated requests
- Unauthorized rejection
- Invalid key rejection

### Production API Test

```bash
python tests/test_production_api.py
```

Tests:
- Health endpoint
- API docs accessibility
- Unauthenticated request handling

---

## Deployment

### Railway

**Services Required:**
1. **API Service** - FastAPI app
2. **Worker Service** - ARQ worker

**Plugins:**
- PostgreSQL
- Redis

**API Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Worker Start Command:**
```bash
arq app.worker.WorkerSettings
```

**Health Check:**
- Path: `/health`
- Timeout: 100s

---

## Environment Variables (Production)

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
GEMINI_API_KEY=<production-key>
CLERK_ISSUER_URL=https://your-production-clerk.accounts.dev
FRONTEND_URL=https://your-app.vercel.app
PROJECT_NAME=scraPy API
API_V1_STR=/api/v1
```

---

## Performance

### Benchmarks

- **Static scraping:** ~800ms/job
- **Dynamic scraping:** ~2.5s/job
- **AI extraction:** ~3s/job

### Optimization

1. Use `guided` mode for static content
2. Enable `renderJs` only when needed
3. Implement result caching
4. Scale workers horizontally
5. Use connection pooling

---

## Troubleshooting

### Worker not processing jobs

```bash
# Check worker is running
ps aux | grep arq

# Check Redis connection
redis-cli -u $REDIS_URL ping

# View worker logs
tail -f worker.log
```

### Database connection issues

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check async pool
# Look for "Database tables initialized" in logs
```

### Playwright errors

```bash
# Reinstall browsers
playwright install chromium

# Check browser path
playwright show
```

---

## Contributing

See main [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## License

MIT - See [LICENSE](../LICENSE)
