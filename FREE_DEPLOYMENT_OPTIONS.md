# 🆓 CallGuard AI - ZERO COST Deployment Options

> **Budget: ₹0 / $0 / €0** - All options are completely free with no credit card required!

---

## 📊 Comparison of Free Options

| Platform | Frontend | Backend | Database | Pros | Cons |
|----------|----------|---------|----------|------|------|
| **Vercel + Render** | ✅ Free | ✅ Free | ✅ SQLite | Best performance, easy setup | Render free tier sleeps after inactivity |
| **Netlify + Railway** | ✅ Free | ✅ Free | ✅ SQLite | Good performance | Railway has limited free hours |
| **Replit** | ✅ Free | ✅ Free | ✅ SQLite | All-in-one, simple | Limited RAM/CPU, slower |
| **GitHub Pages + Glitch** | ✅ Free | ✅ Free | ✅ SQLite | Easy CI/CD | Glitch slower for ML tasks |
| **Cloudflare Pages + PythonAnywhere** | ✅ Free | ✅ Free | ✅ MySQL | Very fast CDN | Complex setup |

---

## 🥇 BEST OPTION: Vercel + Render (Recommended)

### Why This Option?
- ✅ **Best Performance** - Vercel has fastest CDN, Render has good server
- ✅ **Easy Setup** - Both have GitHub integration
- ✅ **Scalable** - Easy to upgrade if needed
- ✅ **No Sleep** - Vercel frontend always active
- ⚠️ **Render backend** may sleep after 15 min inactivity (free tier)

### Step-by-Step Guide

#### 1️⃣ Prepare Your Repository

```bash
# Make sure you're on the main branch
git status
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2️⃣ Deploy Backend to Render (FREE)

1. Go to **https://render.com**
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub:
   - Click **"Connect account"** (if not connected)
   - Authorize Render
   - Select `CallGuardAI` repository
4. Configure Web Service:
   ```
   Name: callguard-api (or any name)
   Environment: Python 3
   Region: Singapore (closest to India)
   Branch: main
   Root Directory: backend
   Build Command: pip install -r requirements-render.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. Add Environment Variables:
   ```
   DATABASE_URL=sqlite:///./callguard.db
   JWT_SECRET=change-this-to-random-secret-key-32-chars
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   LOG_LEVEL=INFO
   ```
6. Click **"Deploy"**
7. Wait for deployment (takes 3-5 minutes)
8. **Copy your API URL** from the dashboard (e.g., `https://callguard-api.onrender.com`)

#### 3️⃣ Deploy Frontend to Vercel (FREE)

1. Go to **https://vercel.com**
2. Click **"Add New"** → **"Project"**
3. Import Git Repository:
   - Click **"Import"** next to your GitHub repo
   - Authorize if needed
   - Select `CallGuardAI`
4. Configure Project:
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```
5. Add Environment Variables:
   - Click **"Environment Variables"**
   - Add: `VITE_API_URL=https://your-render-backend-url` (from step 2)
6. Click **"Deploy"**
7. Wait for deployment (takes 2-3 minutes)
8. **Your app is live!** (e.g., `https://callguard-ai.vercel.app`)

#### 4️⃣ Update Render CORS

1. Go back to **Render.com** → your API service
2. Go to **"Environment"**
3. Update `CORS_ORIGINS` to your Vercel URL:
   ```
   https://your-vercel-frontend-url.vercel.app
   ```
4. **Redeploy** by clicking **"Redeploy latest commit"**

✅ **Done!** Your app is live and completely free!

---

## 🔄 Alternative Option: All-in-One Replit (SIMPLEST)

### Best For: Quick demo, testing

1. Go to **https://replit.com**
2. Click **"Create Repl"** → **"Import from GitHub"**
3. Paste: `https://github.com/YOUR-USERNAME/CallGuardAI`
4. Click **"Import"**
5. In the terminal, run:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
6. Replit creates a public URL automatically
7. In another terminal in Replit:
   ```bash
   cd frontend
   npm install
   VITE_API_URL=https://your-replit-url npm run dev
   ```

**Pros:** One-click setup, everything in one place  
**Cons:** Slower for ML models, limited resources (512MB RAM)

---

## 🚀 Alternative Option: Railway (Free Tier with Limits)

Railway offers **$5/month free credits** (no credit card required initially):

1. Go to **https://railway.app**
2. Click **"Start Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Select root: `backend`
5. Deploy
6. Add environment variables same as Render
7. Frontend can still go to Vercel

**Pros:** Clean interface, fast deployment  
**Cons:** Free credits run out, then paid

---

## 💡 FREE Tier Limitations & Solutions

### Render (FREE)
- ✅ Unlimited requests
- ❌ Spins down after 15 min of inactivity
- ❌ 50 hours/month (but free tier doesn't count towards this)
- **Solution:** Add a cronjob to ping your API every 10 minutes (use cron-job.org - FREE)

### Vercel (FREE)
- ✅ Unlimited requests
- ✅ 100 GB bandwidth/month
- ✅ Fast CDN, no sleep time
- ❌ Pro features locked

### Railway (FREE)
- ✅ $5/month credits (free)
- ❌ After $5, need to pay
- **Solution:** Budget-friendly, good for learning

---

## 🔧 Keep Backend Awake (Optional but Recommended)

If using Render, add a free uptime monitor to keep your backend awake:

### Option 1: Cron-job.org (FREE)
1. Go to **https://cron-job.org**
2. Click **"Sign up"** (free account)
3. **"Create cronjob"**:
   ```
   URL: https://your-render-api.onrender.com/health
   Execution: Every 10 minutes
   ```
4. Save - now your API stays awake!

### Option 2: UptimeRobot (FREE)
1. Go to **https://uptimerobot.com**
2. Create new monitor:
   ```
   Monitor Type: HTTP(s)
   URL: https://your-render-api.onrender.com/health
   Interval: 5 minutes
   ```

---

## 📱 Testing Your Deployment

1. **Frontend URL**: https://your-app.vercel.app
2. **API Docs**: https://your-api.onrender.com/docs
3. **ReDoc**: https://your-api.onrender.com/redoc

### Test endpoints:
```bash
# Check if API is alive
curl https://your-api.onrender.com/health

# Try a sample analysis
curl -X POST https://your-api.onrender.com/api/v1/analyze/text \
  -d "text=test call" \
  -H "Content-Type: application/json"
```

---

## 🔐 Important Security Notes

1. **Change JWT_SECRET**: Generate a random 32-character string
   ```bash
   # Linux/Mac
   openssl rand -hex 16
   
   # Windows PowerShell
   [System.Guid]::NewGuid().ToString().Replace('-', '').Substring(0, 32)
   ```

2. **Update CORS_ORIGINS**: Always set to your actual Vercel URL (not *)

3. **Hide Secrets**: Use environment variables, never commit `.env`

---

## 📊 Cost Breakdown: ₹0 / $0

| Service | Free Tier | Cost |
|---------|-----------|------|
| Vercel Frontend | 100GB bandwidth/month | **₹0** |
| Render Backend | ✅ Always free | **₹0** |
| SQLite Database | Included in backend | **₹0** |
| Domain (optional) | Use `vercel.app` & `onrender.com` | **₹0** |
| **TOTAL** | | **₹0** |

---

## 🆘 Troubleshooting

### "Backend not responding"
- Check Render logs: Dashboard → Your service → Logs
- Wait 30 seconds for free tier to start up
- Check CORS_ORIGINS is correct

### "Frontend can't reach backend"
- Verify `VITE_API_URL` is set in Vercel
- Open DevTools (F12) → Network tab → check request URLs
- Make sure no typos in backend URL

### "API returning 504"
- Render free tier is starting up (wait 30 sec)
- Check backend logs for errors
- Restart the service from Render dashboard

---

## 📝 Summary: Quickest Path to Free Deployment

```
1. Push code to GitHub ✅
2. Go to Render.com, deploy backend (5 min) ✅
3. Go to Vercel.com, deploy frontend (3 min) ✅
4. Add environment variables (2 min) ✅
5. Test on https://your-app.vercel.app ✅

TOTAL TIME: ~15 minutes
TOTAL COST: ₹0
```

---

## 🎯 Next Steps

1. **[Deploy Now](https://render.com)** - Start with backend
2. **[Then Frontend](https://vercel.com)** - Deploy frontend
3. **Test** - Open your Vercel URL and test features
4. **Share** - Your app is public and free!

---

**Questions?** Check logs in respective dashboards or open an issue on GitHub.

**Budget Friendly Confirmed:** ✅ ₹0 | ✅ $0 | ✅ €0
