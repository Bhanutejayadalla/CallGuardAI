# ☁️ AWS Free Tier Options for CallGuard AI

> **AWS Free Tier: 12 months free** (with limitations)
> 
> After 12 months or exceeding limits → **PAID (can get expensive!)**

---

## 🚨 AWS Free Tier Limitations for This Project

| Component | AWS Free Tier | Your Project Needs | Risk |
|-----------|---------------|-------------------|------|
| **EC2** | 750 hrs/mo t2.micro (1GB RAM) | FastAPI + ML models need 2GB+ | ⚠️ HIGH |
| **RDS Database** | 750 hrs/mo t2.micro MySQL (20GB) | SQLite built-in (no need) | ✅ OK |
| **S3** | 5GB storage | Static files (~2MB) | ✅ OK |
| **Data Transfer OUT** | 1GB/month free | ML inference data | ⚠️ RISKY |
| **Lambda** | 1M requests/month | FastAPI not Lambda-friendly | ❌ NOT IDEAL |
| **Cost After 12 Months** | → Paid | Can be $50-200/month | 💰 EXPENSIVE |

---

## ⚠️ Why AWS is NOT the Best for This Project

### Problem 1: Insufficient RAM on Free Tier
```
AWS t2.micro = 512MB - 1GB RAM
Your App Needs:
  - FastAPI: ~200MB
  - Transformers model: ~1GB
  - Librosa: ~300MB
  - TOTAL: ~1.5GB minimum
  
Result: App will crash or run very slowly ❌
```

### Problem 2: Cost After 12 Months
```
t2.micro costs: $0.0116/hour in India region
Per month: 730 hours × $0.0116 = ~$8.47 USD
Plus: Data transfer OUT ($0.12/GB), RDS, S3 storage
Annual Cost: $100-200+ (NOT FREE!)
```

### Problem 3: ML Models are Heavy
```
Whisper model: 140MB
Transformers: 400MB+
This is challenging on t2.micro
```

### Problem 4: 12-Month Limit
```
After 12 months, everything becomes PAID
- Unlike Vercel + Render: FREE FOREVER
- Unlike Railway: Only $5/month thereafter
- AWS: Can jump to $100+/month suddenly
```

---

## ✅ AWS Option IF You Must Use It

If you still want to use AWS, here's the setup:

### Architecture

```
AWS Free Tier Setup:
┌─────────────────────────────────────────┐
│  AWS EC2 t2.micro (1GB RAM)             │
│  - Ubuntu 22.04                         │
│  - FastAPI backend (port 8000)          │
│  - SQLite database                      │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│  AWS S3 + CloudFront                    │
│  - Static React frontend (dist/ files)  │
│  - CDN delivery (free 1GB/month)        │
└─────────────────────────────────────────┘
```

### Step-by-Step AWS Deployment

#### 1️⃣ Create AWS Account (Free Tier Eligible)

1. Go to **https://aws.amazon.com/free**
2. Click **"Create a Free Account"**
3. Sign up with email/card (verification only, not charged initially)
4. Choose **"Free Tier"** plan during signup
5. Wait for account activation

#### 2️⃣ Deploy Backend on EC2

1. **Go to EC2 Dashboard**
   - Search: "EC2" in AWS Console
   - Click **"Launch Instances"**

2. **Configure Instance**
   ```
   Name: callguard-api
   AMI: Ubuntu 22.04 LTS (Free tier eligible)
   Instance Type: t2.micro (Free tier eligible)
   Key Pair: Create new → "callguard-key" → Download .pem file
   ```

3. **Security Group Settings**
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) from 0.0.0.0
   - Allow HTTPS (port 443) from 0.0.0.0
   - Allow custom TCP (port 8000) from 0.0.0.0

4. **Launch** and wait 2-3 minutes

5. **Connect to EC2**
   ```bash
   # Get public IP from AWS Console
   # Rename downloaded .pem file to callguard-key.pem
   
   chmod 400 callguard-key.pem
   ssh -i callguard-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
   ```

6. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv
   
   # Clone your repository
   git clone https://github.com/YOUR-USERNAME/CallGuardAI.git
   cd CallGuardAI/backend
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install requirements (skip Whisper for low RAM)
   pip install -r requirements.txt
   # Or minimal:
   pip install fastapi uvicorn sqlalchemy
   ```

7. **Run Application**
   ```bash
   # In background with nohup
   nohup python main.py > app.log 2>&1 &
   
   # Or use PM2
   npm install -g pm2
   pm2 start "python main.py" --name callguard
   ```

8. **Get Your Backend URL**
   ```
   http://YOUR_EC2_PUBLIC_IP:8000
   ```

#### 3️⃣ Deploy Frontend to S3 + CloudFront

1. **Build Frontend Locally**
   ```bash
   cd frontend
   npm install
   VITE_API_URL=http://YOUR_EC2_IP:8000 npm run build
   ```

2. **Create S3 Bucket**
   - Go to S3 → **Create bucket**
   - Name: `callguard-frontend-YOUR-ID`
   - Region: Asia Pacific (Mumbai) or closest
   - Keep default settings
   - Create

3. **Upload Build Files**
   - Open bucket
   - Click **Upload**
   - Drag `frontend/dist` folder contents
   - Click **Upload**

4. **Enable Static Website Hosting**
   - Go to bucket properties
   - **Static website hosting** → Edit
   - Enable: `Use this bucket to host a website`
   - Index document: `index.html`
   - Error document: `index.html`
   - Save

5. **Get S3 Website URL**
   ```
   http://your-bucket.s3-website.ap-south-1.amazonaws.com
   ```

#### 4️⃣ Optional: Use CloudFront for CDN (Free 1GB/month data)

1. Go to **CloudFront** → **Create Distribution**
2. Origin: Your S3 bucket
3. Create → Wait 15-20 minutes
4. Use CloudFront domain for fastest access

---

## 💰 AWS Free Tier Pricing After 12 Months

| Service | Free Tier | After Free | Monthly Cost |
|---------|-----------|-----------|--------------|
| EC2 t2.micro | 750 hrs/mo | Hourly | $8.47 |
| Data Transfer OUT | 1GB/mo | Per GB | $0.12/GB |
| S3 Storage | 5GB | Per GB | $0.023/GB |
| Route53 (optional) | - | Fixed | $0.50/hosted zone |
| **TOTAL** | **FREE** | **$100+** | **$100-150+** |

---

## 🎯 AWS vs Other FREE Options

| Platform | Frontend | Backend | Cost First 12mo | Cost After 12mo | Suitable |
|----------|----------|---------|-----------------|-----------------|----------|
| **Vercel + Render** | ✅ Free ∞ | ✅ Free ∞ | **₹0** | **₹0** | ✅ YES |
| **Railway** | ✅ Free | ✅ $5/mo | **₹0** | **~₹415** | ✅ YES |
| **Replit** | ✅ Free | ✅ Free | **₹0** | **Paid plans** | ✅ YES |
| **AWS** | ✅ Free 12mo | ⚠️ Limited | **₹0** | **₹8,000+** | ❌ NO |
| **GCP** | ⚠️ Limited | ⚠️ Limited | **₹0** | **Paid** | ⚠️ MAYBE |

---

## 🚀 BETTER AWS-Like Option: AWS Lightsail (Still More Expensive)

If you want managed AWS, try **AWS Lightsail**:
- Monthly: $3.50-5 (but NOT free tier eligible on free account)
- Better for this project than EC2 t2.micro
- Easier management

---

## ✅ RECOMMENDATION: Skip AWS Free Tier

### Why?
1. **RAM too limited** - App will struggle
2. **Time-limited** - Only 12 months free
3. **Gets expensive** - $100+/month after free tier
4. **Not designed for this** - EC2 t2.micro is for light web apps

### Best Choice for ₹0 FOREVER:

```
✅ **Vercel + Render** (RECOMMENDED)
   - Forever free
   - Better performance
   - Simple deployment
   - No surprises

OR

✅ **Railway + Netlify**
   - $5/month after trial
   - Excellent performance
   - Easy management
```

---

## 🔥 If You MUST Use AWS (Advanced)

Use **AWS Lambda + API Gateway** instead of EC2:

```
Pros:
- $1 = 1 million requests/month
- True serverless
- No management

Cons:
- Need to convert FastAPI → Lambda handlers (complex)
- Cold start delays (3-10 seconds first time)
- ML models too heavy for Lambda
- Not suitable for real-time analysis
```

---

## 📋 Final Recommendation

| Use Case | Best Option | Cost |
|----------|------------|------|
| **Want 100% FREE forever** | Vercel + Render | ₹0 |
| **Want better performance after 1 year** | Railway | ~₹415/mo |
| **Need AWS specifically** | Lightsail ($3.50/mo) or EC2 (after free tier) | $100+/mo |
| **Educational/Testing** | Replit | ₹0 (free tier) |
| **Production with ₹0 budget** | Render + Vercel | ₹0 ∞ |

---

## 🎯 My Honest Take

**AWS Free Tier is a trap for this project because:**

1. ❌ t2.micro too small for ML models
2. ❌ Only 12 months free (not perpetual like others)
3. ❌ Becomes expensive quickly ($100+/month)
4. ✅ Better options exist (Render, Railway, Vercel)

**Stick with Vercel + Render. It's free forever and performs better!**

---

**Questions?** The Vercel + Render setup is truly ₹0 forever with no surprises.
