# scraPy - Intelligent Web Scraping Platform

<div align="center">

![scraPy Logo](https://img.shields.io/badge/scraPy-Intelligent%20Scraping-blue?style=for-the-badge)

**Production-grade web scraping platform powered by AI**

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/next.js-16.0-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [API Docs](#api-documentation) • [Deployment](#deployment)

</div>

---

## Overview

**scraPy** is a modern, production-ready web scraping platform that combines the power of AI with traditional CSS selectors to extract data from any website. Built with a microservices architecture, it offers both a beautiful web interface and a comprehensive REST API for programmatic access.

### Key Highlights

- 🤖 **AI-Powered Extraction** - Natural language instructions powered by Google Gemini
- 🎯 **Traditional Selectors** - CSS selector support for precise data extraction
- 🚀 **Async Processing** - Background job queue with ARQ for non-blocking operations
- 🔒 **Enterprise Security** - SSRF protection, rate limiting, JWT authentication
- 📊 **Real-time Monitoring** - Health checks, structured logging, job tracking
- 🌐 **Dynamic Content** - Playwright integration for JavaScript-heavy sites
- 🔑 **API Key Management** - Secure programmatic access with HMAC webhooks
- 📱 **Modern UI** - Responsive Next.js interface with real-time updates

---

## Features

### 🎯 Core Scraping Capabilities

#### Guided Mode (CSS Selectors)
```json
{
  "url": "https://example.com",
  "mode": "guided",
  "selectors": {
    "title": "h1",
    "description": "p.description",
    "price": ".price-tag"
  }
}
```

#### Smart Mode (AI-Powered)
```json
{
  "url": "https://example.com",
  "mode": "smart",
  "instruction": "Extract product name, price, and availability status"
}
```

### 🔐 Security Features

- **SSRF Prevention** - Blocks private IPs, localhost, link-local addresses
- **Rate Limiting** - Per-API-key limits stored in Redis
- **Input Validation** - Pydantic validators for all inputs
- **Request Size Limits** - 10MB max payload protection
- **Error Sanitization** - No internal details exposed in production
- **JWT Authentication** - Clerk-based user authentication

### 📊 Monitoring & Observability

- **Health Checks** - `/health` endpoint with DB/Redis verification
- **Structured Logging** - Consistent log format with levels
- **Job Tracking** - Complete lifecycle logging with duration metrics
- **API Documentation** - Auto-generated Swagger UI at `/docs`

### 🔧 Advanced Features

- **Dynamic Content Support** - Playwright for JavaScript-rendered pages
- **Webhook Notifications** - HMAC-signed webhooks for job completion
- **Job History** - Persistent storage in PostgreSQL
- **Result Caching** - Redis-based caching with 1-hour TTL
- **Async Workers** - ARQ-based background processing

---

## Architecture

### System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Next.js Frontend]
        API_CLIENT[API Clients]
    end

    subgraph "API Gateway"
        FASTAPI[FastAPI Server]
        AUTH[Clerk Auth]
    end

    subgraph "Processing Layer"
        WORKER[ARQ Worker]
        SCRAPER[Scraper Service]
        LLM[Gemini LLM]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        REDIS[(Redis)]
    end

    subgraph "External"
        WEBSITES[Target Websites]
    end

    UI --> FASTAPI
    API_CLIENT --> FASTAPI
    FASTAPI --> AUTH
    FASTAPI --> REDIS
    FASTAPI --> POSTGRES
    WORKER --> REDIS
    WORKER --> POSTGRES
    WORKER --> SCRAPER
    SCRAPER --> WEBSITES
    SCRAPER --> LLM
    WORKER -.Webhook.-> API_CLIENT
```

### Data Flow - Scraping Job

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Redis
    participant Worker
    participant Scraper
    participant LLM
    participant DB

    Client->>API: POST /scrape
    API->>Redis: Enqueue job
    API->>Redis: Set initial status
    API-->>Client: job_id

    Worker->>Redis: Dequeue job
    Worker->>DB: Update status: processing
    Worker->>Scraper: Fetch content
    Scraper->>LLM: Analyze (if smart mode)
    LLM-->>Scraper: Extracted data
    Scraper-->>Worker: Results
    Worker->>DB: Save results
    Worker->>Redis: Cache results
    
    Client->>API: GET /scrape/{id}
    API->>Redis: Get cached job
    API-->>Client: Job status + data
```

### Tech Stack

#### Backend
- **API Framework:** FastAPI 0.115+
- **Authentication:** Clerk JWT
- **Task Queue:** ARQ (Async Redis Queue)
- **Database:** PostgreSQL with AsyncPG
- **Cache:** Redis 7.0+
- **Web Scraping:** 
  - httpx (static content)
  - Playwright (dynamic content)
  - BeautifulSoup4 (HTML parsing)
- **AI:** Google Gemini 2.0 Flash
- **Validation:** Pydantic 2.0+

#### Frontend
- **Framework:** Next.js 16 (App Router)
- **UI Library:** React 19
- **Authentication:** Clerk
- **State Management:** 
  - TanStack Query (React Query)
  - Zustand
- **HTTP Client:** Axios
- **UI Components:** Radix UI + TailwindCSS
- **Forms:** React Hook Form + Zod

#### Infrastructure
- **Deployment:** Railway (Backend) + Vercel (Frontend)
- **Databases:** Railway PostgreSQL + Redis
- **Monitoring:** Built-in health checks + structured logs

---

## Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **PostgreSQL 14+**
- **Redis 7.0+**
- **Gemini API Key** ([Get one here](https://ai.google.dev/))
- **Clerk Account** ([Sign up](https://clerk.com/))

### Backend Setup

```bash
# Clone repository
git clone https://github.com/Vrohs/scraPy_final_release.git
cd scraPy_final_release/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start API server
uvicorn app.main:app --reload

# Start worker (in separate terminal)
arq app.worker.WorkerSettings
```

### Frontend Setup

```bash
cd scraPy_final_release/frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your credentials

# Start development server
npm run dev
```

### Access

- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## API Documentation

### Authentication

All API endpoints require authentication via:
- **API Key:** `X-API-Key` header
- **JWT Token:** `Authorization: Bearer <token>` header

### Core Endpoints

#### Create Scraping Job

```http
POST /api/v1/scrape
Content-Type: application/json
X-API-Key: sk_live_xxx

{
  "url": "https://example.com",
  "mode": "guided",
  "selectors": {
    "title": "h1",
    "description": ".description"
  },
  "options": {
    "renderJs": false
  }
}
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "pending"
}
```

#### Get Job Status

```http
GET /api/v1/scrape/{job_id}
X-API-Key: sk_live_xxx
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "completed",
  "url": "https://example.com",
  "mode": "guided",
  "data": {
    "title": "Example Domain",
    "description": "This domain is for use in illustrative examples..."
  }
}
```

### Complete API Reference

Interactive API documentation available at:
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

---

## Configuration

### Environment Variables

#### Backend (`backend/.env`)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/scrapy
# Or use individual components:
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
POSTGRES_DB=scrapy

# Redis
REDIS_URL=redis://localhost:6379
# Or use individual components:
REDIS_HOST=localhost
REDIS_PORT=6379

# API Keys
GEMINI_API_KEY=your_gemini_api_key

# Authentication
CLERK_ISSUER_URL=https://your-clerk-app.clerk.accounts.dev

# CORS
FRONTEND_URL=http://localhost:3000

# Application
PROJECT_NAME=scraPy API
API_V1_STR=/api/v1
```

#### Frontend (`frontend/.env.local`)

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
```

---

## Deployment

### Production Architecture

```mermaid
graph LR
    subgraph "Vercel"
        FE[Next.js App]
    end
    
    subgraph "Railway"
        API[FastAPI API]
        WORKER[ARQ Worker]
        PG[(PostgreSQL)]
        RD[(Redis)]
    end
    
    FE --> API
    API --> PG
    API --> RD
    WORKER --> PG
    WORKER --> RD
```

### Railway Deployment

1. **Create Railway Project**
```bash
railway login
railway init
```

2. **Add Database Plugins**
```bash
railway add --plugin postgresql
railway add --plugin redis
```

3. **Deploy API Service**
```bash
cd backend
railway up
```

4. **Deploy Worker Service**
- Create second service in Railway dashboard
- Use same repo, different start command: `arq app.worker.WorkerSettings`

### Vercel Deployment

```bash
cd frontend
vercel login
vercel --prod
```

**Detailed deployment guide:** See [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## Security

### Implemented Protections

✅ **SSRF Prevention**
- Blocks private IP ranges (10.x.x.x, 192.168.x.x, 172.16.x.x)
- Blocks localhost and loopback addresses
- Blocks link-local addresses

✅ **Input Validation**
- URL format validation
- Maximum length constraints
- Mode validation (guided/smart only)

✅ **Rate Limiting**
- Per-API-key limits
- Redis-backed distributed rate limiting
- Configurable limits per key

✅ **Request Size Limits**
- 10MB maximum payload
- Prevents memory exhaustion

✅ **Error Sanitization**
- Generic errors in production
- Detailed errors only in development

✅ **Authentication**
- Clerk JWT verification
- API key SHA-256 hashing
- HMAC webhook signatures

### Security Headers

```python
# CORS configured with specific origins
# Content-Type validation
# Request size middleware
# Rate limiting per API key
```

---

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-01T16:30:00.123456",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### Structured Logging

All events are logged with consistent format:

```
2025-12-01 21:45:30 - scrapy - INFO - Starting scrape job abc-123 for https://example.com in guided mode
2025-12-01 21:45:32 - scrapy - INFO - Job completed: abc-123 | Duration: 1.85s
```

**Log Events:**
- Job creation, processing, completion
- API key creation/revocation
- Webhook dispatch
- Rate limit violations
- SSRF attempts
- System startup/shutdown

---

## Development

### Project Structure

```
scraPy/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   │           ├── scrape.py       # Scraping endpoints
│   │   │           ├── api_keys.py     # API key management
│   │   │           └── webhooks.py     # Webhook management
│   │   ├── core/
│   │   │   ├── config.py              # Settings
│   │   │   ├── database.py            # DB connection
│   │   │   ├── redis.py               # Redis connection
│   │   │   ├── logging.py             # Structured logging
│   │   │   └── ratelimit.py           # Rate limiter
│   │   ├── models/
│   │   │   ├── job.py                 # Job model
│   │   │   ├── api_key.py             # API key model
│   │   │   └── webhook.py             # Webhook model
│   │   ├── services/
│   │   │   ├── scraper.py             # Scraping logic
│   │   │   └── llm.py                 # LLM integration
│   │   ├── main.py                    # FastAPI app
│   │   └── worker.py                  # ARQ worker
│   ├── tests/
│   │   ├── test_e2e_infrastructure.py
│   │   ├── test_api_key.py
│   │   └── test_production_api.py
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── app/                       # Next.js App Router
    │   │   ├── page.tsx               # Dashboard
    │   │   ├── scrape/                # Scrape pages
    │   │   ├── history/               # Job history
    │   │   └── api-keys/              # API key management
    │   ├── components/
    │   │   ├── ui/                    # Radix UI components
    │   │   ├── scrape-form.tsx        # Scrape job form
    │   │   └── results/               # Results display
    │   ├── services/
    │   │   ├── scrape.ts              # Scrape API client
    │   │   ├── api-keys.ts            # API key client
    │   │   └── webhook.ts             # Webhook client
    │   └── lib/
    │       └── api.ts                 # Axios instance
    └── package.json
```

### Running Tests

```bash
# Backend tests
cd backend
source venv/bin/activate

# E2E infrastructure test
python tests/test_e2e_infrastructure.py

# API key tests
python tests/test_api_key.py

# Production API test
python tests/test_production_api.py

# Frontend E2E tests
cd frontend
npx playwright test
```

### Making Changes

1. **Backend Changes:**
   - API server auto-reloads with `--reload` flag
   - Worker needs manual restart
   - Run linting: `ruff check .`

2. **Frontend Changes:**
   - Next.js hot-reloads automatically
   - Check console for errors
   - Run linting: `npm run lint`

3. **Database Changes:**
   - Currently using `Base.metadata.create_all`
   - For production: implement Alembic migrations

---

## Performance

### Benchmarks

**Static Page Scraping:**
- Average: ~800ms per job
- Includes: HTTP fetch + parsing + DB save

**Dynamic Page Scraping (Playwright):**
- Average: ~2.5s per job
- Includes: Browser launch + render + parsing + DB save

**Smart Mode (AI):**
- Average: ~3s per job
- Includes: Scraping + LLM analysis (Gemini 2.0 Flash)

### Optimization Tips

1. **Use Guided Mode** for static content
2. **Enable `renderJs`** only when necessary
3. **Implement result caching** for frequently scraped URLs
4. **Use API keys** with appropriate rate limits
5. **Deploy worker separately** for better scaling

---

## Roadmap

### Completed ✅
- [x] Core scraping (guided + smart modes)
- [x] API key authentication
- [x] Webhook notifications
- [x] Security hardening (SSRF, rate limiting)
- [x] Structured logging
- [x] Health monitoring
- [x] API documentation
- [x] Production deployment

### In Progress 🚧
- [ ] Unit test coverage expansion
- [ ] Alembic database migrations
- [ ] Sentry error tracking integration

### Planned 📋
- [ ] Browser pooling for Playwright
- [ ] WebSocket support for real-time job updates
- [ ] Data export formats (CSV, JSON, Excel)
- [ ] Scheduled scraping (cron jobs)
- [ ] Custom JavaScript injection
- [ ] Proxy rotation support
- [ ] Rate limit usage dashboard

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest` (backend) / `npm test` (frontend)
5. Commit with conventional commits: `feat: add amazing feature`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Commit Convention

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build process or auxiliary tool changes

---

## Troubleshooting

### Common Issues

**Jobs not processing:**
```bash
# Check worker is running
ps aux | grep "arq app.worker"

# Check Redis connection
redis-cli ping

# View worker logs
tail -f worker.log
```

**401 Unauthorized:**
```bash
# Verify Clerk issuer URL
echo $CLERK_ISSUER_URL

# Check API key format
# Should start with sk_live_ or sk_test_
```

**Health check fails:**
```bash
# Test individually
curl http://localhost:8000/health

# Check database
psql $DATABASE_URL -c "SELECT 1"

# Check Redis
redis-cli -u $REDIS_URL ping
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

**Built with:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [Clerk](https://clerk.com/) - Authentication platform
- [Playwright](https://playwright.dev/) - Browser automation
- [Google Gemini](https://ai.google.dev/) - AI model
- [Radix UI](https://www.radix-ui.com/) - Unstyled UI components
- [Railway](https://railway.app/) - Deployment platform
- [Vercel](https://vercel.com/) - Frontend hosting

---

## Support

- **Documentation:** [Full docs](./docs/)
- **Issues:** [GitHub Issues](https://github.com/Vrohs/scraPy_final_release/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Vrohs/scraPy_final_release/discussions)

---

<div align="center">

**Made with ❤️ by [Advait](https://github.com/Vrohs)**

⭐ Star this repo if you find it useful!

</div>
