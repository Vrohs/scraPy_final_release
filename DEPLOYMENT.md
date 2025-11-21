# scraPy Deployment Guide

Complete guide to deploying scraPy platform: Next.js frontend to Vercel and Python FastAPI backend to Railway.

## Prerequisites

Before starting deployment, ensure you have:

1. ✅ **Vercel Account**: Sign up at [vercel.com](https://vercel.com) (free tier works)
2. ✅ **Railway Account**: Sign up at [railway.app](https://railway.app) (free tier available)
3. ✅ **GitHub Account**: Your code repository at `https://github.com/Vrohs/scraPy_final_release`
4. ✅ **Clerk Account**: Your authentication credentials ready
5. ✅ **Gemini API Key**: For AI-powered scraping features

---

## Part 1: Deploy Backend to Railway

### Step 1: Create New Railway Project

1. Go to [railway.app](https://railway.app) and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `Vrohs/scraPy_final_release`
5. Railway will auto-detect it's a Python project

### Step 2: Add PostgreSQL Database

1. In your Railway project dashboard, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will automatically create a PostgreSQL instance
3. Important: Railway automatically sets the `DATABASE_URL` environment variable
4. Your backend code will automatically use this (thanks to our smart config!)

### Step 3: Add Redis Database

1. In your Railway project dashboard, click **"New"** → **"Database"** → **"Add Redis"**
2. Railway will automatically create a Redis instance
3. Important: Railway automatically sets the `REDIS_URL` environment variable
4. Your backend code will automatically use this (thanks to our smart config!)

### Step 4: Configure Backend Environment Variables

1. Click on your **backend service** (the Python app, not the databases)
2. Go to **"Variables"** tab
3. Add the following environment variables:

```bash
# Gemini AI API Key (REQUIRED)
GEMINI_API_KEY=AIzaSyAqZ7m0_thfL9bH-MsnrCNN4gkLaKoRrok

# Frontend URL (will update this after Vercel deployment)
FRONTEND_URL=http://localhost:3000

# Project settings (optional, defaults are good)
PROJECT_NAME=scraPy API
API_V1_STR=/api/v1
```

> [!NOTE]
> `DATABASE_URL` and `REDIS_URL` are **automatically set** by Railway when you add those services. You don't need to manually add them!

### Step 5: Configure Root Directory

Since your backend code is in the `backend/` folder:

1. In Railway, click your backend service
2. Go to **"Settings"** tab
3. Scroll to **"Service"** section
4. Set **"Root Directory"** to: `backend`
5. Click **"Update"**

### Step 6: Deploy Backend

1. Railway will automatically deploy when you push to GitHub
2. Or manually click **"Deploy"** in Railway dashboard
3. Wait for deployment to complete (2-3 minutes)
4. Once deployed, copy your **Railway public URL** (e.g., `https://scrapy-production-xxxx.railway.app`)

### Step 7: Install Playwright in Railway

Railway needs to install Playwright browsers after deployment:

1. In Railway, go to your backend service
2. Click **"Settings"** → **"Deploy"** section
3. Under **"Build Command"**, add:
   ```bash
   pip install -r requirements.txt && playwright install --with-deps chromium
   ```
4. Click **"Update"**
5. Redeploy the service

### Step 8: Verify Backend Deployment

Visit your Railway URL in a browser:
- Root endpoint: `https://your-app.railway.app/`
  - Should show: `{"message": "Welcome to scraPy API"}`
- API docs: `https://your-app.railway.app/api/v1/docs`
  - Should show FastAPI Swagger UI

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create New Vercel Project

1. Go to [vercel.com](https://vercel.com) and log in
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository: `Vrohs/scraPy_final_release`
4. Vercel will auto-detect it's a Next.js project

### Step 2: Configure Build Settings

1. **Framework Preset**: Next.js (auto-detected)
2. **Root Directory**: Set to `frontend`
3. **Build Command**: `npm run build` (default)
4. **Output Directory**: `.next` (default)

### Step 3: Configure Environment Variables

Before clicking "Deploy", add these environment variables:

Click **"Environment Variables"** and add:

```bash
# Clerk Authentication (REQUIRED)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_c3F1YXJlLW1vbGx5LTcyLmNsZXJrLmFjY291bnRzLmRldiQ
CLERK_SECRET_KEY=sk_test_E707AcKflh7XO9n3FPQVbhDhue9Umbp9lLEEjrnG2P

# Backend API URL (use your Railway URL from Part 1, Step 6)
NEXT_PUBLIC_API_URL=https://your-app.railway.app/api/v1
```

> [!IMPORTANT]
> Replace `https://your-app.railway.app` with your actual Railway backend URL!

### Step 4: Deploy Frontend

1. Click **"Deploy"**
2. Vercel will build and deploy your frontend (3-5 minutes)
3. Once complete, you'll get a Vercel URL (e.g., `https://scrapy-frontend.vercel.app`)

### Step 5: Update Backend CORS

Now that you have your Vercel URL, update the backend to allow it:

1. Go back to **Railway**
2. Click your backend service → **"Variables"** tab
3. Update the `FRONTEND_URL` variable:
   ```bash
   FRONTEND_URL=https://your-vercel-app.vercel.app
   ```
4. Railway will automatically redeploy with new CORS settings

---

## Part 3: Verification

### Test the Deployment

1. **Visit your Vercel frontend URL**
   - App should load without errors
   - UI should render correctly

2. **Test Authentication**
   - Click "Sign In" or "Sign Up"
   - Clerk authentication should work

3. **Test Scraping Functionality**
   - Sign in to your account
   - Create a new scraping job
   - Verify it communicates with Railway backend
   - Check that results are displayed

4. **Check Railway Logs**
   - Go to Railway → Your backend service → **"Deployments"** tab
   - Check logs for any errors
   - Verify database and Redis connections are successful

---

## Troubleshooting

### Common Issues

#### ❌ CORS Errors

**Problem**: Frontend can't connect to backend, browser console shows CORS errors

**Solution**:
- Verify `FRONTEND_URL` in Railway matches your Vercel URL exactly
- Make sure `NEXT_PUBLIC_API_URL` in Vercel points to Railway
- No trailing slashes in URLs!

#### ❌ Database Connection Failed

**Problem**: Railway logs show database connection errors

**Solution**:
- Verify PostgreSQL service is running in Railway
- Check that `DATABASE_URL` is automatically set (Railway → Backend service → Variables)
- Redeploy the backend service

#### ❌ Redis Connection Failed

**Problem**: Background jobs not processing

**Solution**:
- Verify Redis service is running in Railway
- Check that `REDIS_URL` is automatically set
- Make sure the worker process is running (check Procfile)

#### ❌ Playwright/Browser Errors

**Problem**: Scraping fails with browser-related errors

**Solution**:
- Ensure Playwright install command is in Railway build settings (Step 1.7)
- Check Railway logs for browser installation errors
- May need to increase Railway memory allocation (Settings → Resources)

#### ❌ Authentication Not Working

**Problem**: Clerk sign in/sign up fails

**Solution**:
- Verify both `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY` are set in Vercel
- Check Clerk dashboard → your application → settings for correct keys
- Ensure your Vercel domain is added to Clerk's allowed domains

---

## Environment Variables Reference

### Frontend (Vercel)

| Variable | Value | Required |
|----------|-------|----------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_test_c3F1YXJlLW1vbGx5LTcyLmNsZXJrLmFjY291bnRzLmRldiQ` | ✅ Yes |
| `CLERK_SECRET_KEY` | `sk_test_E707AcKflh7XO9n3FPQVbhDhue9Umbp9lLEEjrnG2P` | ✅ Yes |
| `NEXT_PUBLIC_API_URL` | `https://your-railway-app.railway.app/api/v1` | ✅ Yes |

### Backend (Railway)

| Variable | Value | Auto-Set by Railway? |
|----------|-------|---------------------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ Yes (when you add PostgreSQL) |
| `REDIS_URL` | Redis connection string | ✅ Yes (when you add Redis) |
| `GEMINI_API_KEY` | `AIzaSyAqZ7m0_thfL9bH-MsnrCNN4gkLaKoRrok` | ❌ No (you must add) |
| `FRONTEND_URL` | `https://your-vercel-app.vercel.app` | ❌ No (you must add) |
| `PROJECT_NAME` | `scraPy API` | ⚪ Optional (has default) |
| `API_V1_STR` | `/api/v1` | ⚪ Optional (has default) |

---

## Post-Deployment

### Monitor Your Services

**Vercel**:
- Dashboard → Your project → Analytics
- View traffic, performance, and errors

**Railway**:
- Dashboard → Your project → Deployments tab
- Monitor logs, resource usage, and uptime

### Update Your Application

1. **Push to GitHub**: All changes pushed to your repository will auto-deploy
2. **Vercel**: Auto-deploys on push to main branch
3. **Railway**: Auto-deploys on push to main branch

### Rollback if Needed

**Vercel**:
- Dashboard → Your project → Deployments
- Click on a previous deployment → "Promote to Production"

**Railway**:
- Dashboard → Your project → Deployments tab
- Click on a previous deployment → "Redeploy"

---

## Cost Estimate

**Free Tier Limits**:
- **Vercel**: 100GB bandwidth/month, unlimited deployments
- **Railway**: $5 free credit/month (usually enough for small projects)
- **Clerk**: 10,000 MAU (Monthly Active Users) free

> [!TIP]
> Both platforms have generous free tiers perfect for development and small-scale production use!

---

## Next Steps

🎉 **Congratulations!** Your scraPy platform is now live!

- Share your Vercel URL with users
- Monitor usage and performance
- Consider setting up custom domains for both services
- Set up monitoring/alerting for production issues

Need help? Check the Railway and Vercel documentation or reach out to their support teams.
