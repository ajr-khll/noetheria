# 🚀 Deployment Guide

## Quick Deploy Setup

### 1. **Frontend (Vercel) - FREE**

1. **Connect GitHub to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with GitHub
   - Click "New Project" → Import your GitHub repo
   - Select `vector-app` as root directory

2. **Environment Variables:**
   ```
   NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.railway.app
   ```

3. **Deploy:**
   - Vercel auto-deploys on git push
   - Your site: `https://your-project.vercel.app`

### 2. **Backend (Railway) - FREE**

1. **Setup Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Create new project → "Deploy from GitHub repo"
   - Select your repo, set root directory to `vector-backend`

2. **Environment Variables in Railway:**
   ```
   OPENAI_API_KEY=your_key_here
   CUSTOM_SEARCH_API=your_google_api_key
   ENGINE_ID=your_search_engine_id
   REDIS_URL=redis://your-redis-url
   FRONTEND_URL=https://your-project.vercel.app
   PORT=5000
   ```

3. **Deploy Settings:**
   - Build command: `pip install -r requirements.txt`
   - Start command: `python wsgi.py`

### 3. **Redis (Upstash) - FREE**

1. **Setup Upstash Redis:**
   - Go to [upstash.com](https://upstash.com)
   - Create account → New Database
   - Choose "Global" for best performance
   - Copy the Redis URL

2. **Update Environment:**
   - Add Redis URL to Railway environment variables
   - Format: `redis://default:password@host:port`

## Alternative Hosting Options

### **Backend Alternatives:**

| Platform | Free Tier | Pros | Cons |
|----------|-----------|------|------|
| **Railway** | ✅ 500 hours/month | Easy setup, good performance | Limited free tier |
| **Render** | ✅ 750 hours/month | Reliable, automatic SSL | Slower cold starts |
| **Fly.io** | ✅ 3 apps free | Fast, global | More complex setup |
| **Heroku** | ❌ Paid only | Mature platform | No free tier |
| **DigitalOcean** | ❌ $5/month | Full control | Requires server management |

### **Redis Alternatives:**

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Upstash** | ✅ 10k requests/day | 256MB storage |
| **Redis Cloud** | ✅ 30MB | Limited connections |
| **Railway Redis** | ✅ Included | With backend hosting |

## Step-by-Step Railway Deployment

### 1. **Prepare Backend:**
```bash
# Add Gunicorn for production (optional but recommended)
echo "gunicorn" >> vector-backend/requirements.txt
```

### 2. **Deploy to Railway:**
1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set **Root Directory**: `vector-backend`
5. Railway will auto-detect Python and deploy

### 3. **Configure Environment:**
In Railway dashboard → Variables tab:
```
OPENAI_API_KEY=sk-...
CUSTOM_SEARCH_API=AIza...
ENGINE_ID=your-engine-id
REDIS_URL=redis://default:password@host:port
FRONTEND_URL=https://your-project.vercel.app
PORT=5000
```

### 4. **Update CORS in Backend:**
Replace `https://your-app.vercel.app` in `app.py` with your actual Vercel URL.

### 5. **Deploy Frontend:**
1. Go to [vercel.com](https://vercel.com)
2. Import GitHub repo
3. Set **Root Directory**: `vector-app`
4. Add environment variable:
   ```
   NEXT_PUBLIC_BACKEND_URL=https://your-project.up.railway.app
   ```

## Production Checklist

### ✅ **Before Going Live:**

1. **Security:**
   - [ ] Set Redis password in production
   - [ ] Use environment variables for all secrets
   - [ ] Enable HTTPS (automatic on Vercel/Railway)
   - [ ] Update CORS origins to your actual domains

2. **Performance:**
   - [ ] Redis caching enabled and configured
   - [ ] Database indexes in place
   - [ ] Frontend build optimized

3. **Monitoring:**
   - [ ] Check Railway logs for errors
   - [ ] Monitor Redis usage in Upstash dashboard
   - [ ] Test all features in production

## Cost Estimates

### **Free Tier Limits:**
- **Vercel:** Unlimited for personal projects
- **Railway:** 500 hours/month (≈20 days of 24/7 uptime)
- **Upstash Redis:** 10k requests/day
- **Total Monthly Cost:** $0 for moderate usage

### **Paid Upgrade Triggers:**
- Railway: $5/month for unlimited hours
- Upstash: $0.2 per 100k requests beyond free tier
- Vercel: Free for personal use

## Troubleshooting

### **Common Issues:**

1. **CORS Errors:**
   - Update allowed origins in `app.py`
   - Ensure FRONTEND_URL environment variable is set

2. **Redis Connection Fails:**
   - Verify REDIS_URL format
   - Check Upstash dashboard for connection limits

3. **Build Failures:**
   - Check requirements.txt is complete
   - Verify all dependencies are compatible

4. **API Limits:**
   - Monitor Google Search API usage
   - Check OpenAI API usage limits

### **Logs & Debugging:**
```bash
# Railway logs
railway logs

# Local testing with production env
cd vector-backend
cp .env.example .env
# Edit .env with production values
python wsgi.py
```

## Domain Setup (Optional)

### **Custom Domain:**
1. **Frontend (Vercel):**
   - Project Settings → Domains → Add domain
   - Update DNS records as instructed

2. **Backend (Railway):**
   - Project Settings → Networking → Custom Domain
   - Point your domain to Railway

Your app will be live at:
- **Frontend:** `https://your-domain.com`
- **Backend:** `https://api.your-domain.com`