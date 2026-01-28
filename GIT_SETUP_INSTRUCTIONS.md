# Git Setup and Push to GitHub

## Prerequisites

### 1. Install Git (if not already installed)
Download and install Git from: https://git-scm.com/download/win

**After installation, restart VS Code.**

---

## Push to GitHub Repository

### Step 1: Configure Git (First time only)
```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 2: Initialize Git Repository
```powershell
cd D:\hackathon
git init
```

### Step 3: Add All Files
```powershell
git add .
```

### Step 4: Create Initial Commit
```powershell
git commit -m "Initial commit: CallGuard AI with AI Voice Detection

Features:
- AI-generated voice detection (multi-language)
- Supports Tamil, English, Hindi, Malayalam, Telugu
- Base64-encoded MP3 audio input
- Spam/Fraud/Phishing/Robocall detection
- Real-time audio analysis
- FastAPI backend with React frontend
- SQLite database with analytics
- Admin dashboard and user authentication"
```

### Step 5: Set Main Branch
```powershell
git branch -M main
```

### Step 6: Add GitHub Remote
```powershell
git remote add origin https://github.com/Bhanutejayadalla/CallGuardAI.git
```

### Step 7: Push to GitHub
```powershell
git push -u origin main
```

**If the repository already exists on GitHub with content:**
```powershell
# Force push (overwrites remote)
git push -u origin main --force

# OR pull first and merge
git pull origin main --allow-unrelated-histories
git push -u origin main
```

---

## Complete Command Sequence (Copy-Paste)

```powershell
# Navigate to project
cd D:\hackathon

# Initialize and commit
git init
git add .
git commit -m "Initial commit: CallGuard AI with AI Voice Detection"
git branch -M main

# Add remote and push
git remote add origin https://github.com/Bhanutejayadalla/CallGuardAI.git
git push -u origin main
```

---

## Troubleshooting

### Error: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/Bhanutejayadalla/CallGuardAI.git
```

### Error: "failed to push some refs"
```powershell
# Option 1: Force push (if you're sure)
git push -u origin main --force

# Option 2: Pull and merge first
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Error: "Git is not recognized"
1. Install Git from https://git-scm.com/download/win
2. Restart VS Code
3. Try again

### Authentication Required
GitHub may ask for authentication:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (not your password)
  - Generate token at: https://github.com/settings/tokens
  - Select scopes: `repo` (full control)

---

## Future Updates

After the initial push, use these commands to update:

```powershell
cd D:\hackathon

# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to GitHub
git push
```

---

## What's Being Committed

Files included (based on .gitignore):
- ✅ All source code (backend & frontend)
- ✅ Configuration files
- ✅ README and documentation
- ✅ Test files
- ❌ node_modules/ (excluded)
- ❌ .venv/ (excluded)
- ❌ __pycache__/ (excluded)
- ❌ uploads/ (excluded)
- ❌ *.db files (excluded)
- ❌ .env files (excluded)

Total project size (excluding ignored files): ~5-10 MB
