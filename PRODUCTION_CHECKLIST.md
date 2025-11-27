# ScraPy Production Deployment Checklist

## Critical Pre-Launch Items

### Backend (Railway)
- [ ] Verify ARQ worker is running (check Railway logs or add worker dyno)
- [ ] Run database migration to add `error` column:
  ```sql
  ALTER TABLE jobs ADD COLUMN IF NOT EXISTS error VARCHAR;
  ```
- [ ] Verify environment variables in Railway:
  - [ ] `GEMINI_API_KEY` is set
  - [ ] `FRONTEND_URL` points to Vercel URL
  - [ ] `DATABASE_URL` is auto-set by Railway
  - [ ] `REDIS_URL` is auto-set by Railway

### Frontend (Vercel)
- [ ] Verify environment variables:
  - [ ] `NEXT_PUBLIC_API_URL` points to Railway URL
  - [ ] `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is set
  - [ ] `CLERK_SECRET_KEY` is set

### Verification Steps
1. [ ] Submit a test scrape job via production UI
2. [ ] Verify job completes and results appear
3. [ ] Check Railway logs for worker activity
4. [ ] Generate an API key from production UI
5. [ ] Test API key with curl:
   ```bash
   curl -X POST https://scrapyfinalrelease-production.up.railway.app/api/v1/scrape \
     -H "X-API-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"url":"https://example.com","mode":"guided","selectors":{"title":"h1"}}'
   ```

## Post-Launch Monitoring
- [ ] Monitor Railway logs for errors
- [ ] Check database for job completion rates
- [ ] Verify Redis queue is being processed
- [ ] Monitor API response times

## Known Issues
- OpenAPI docs endpoint returns 404 in production (non-critical)
- Some endpoints return 405 instead of 401 (needs investigation)
