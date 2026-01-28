# 🚀 News Recommendation System - Setup Guide

## Current Status
✅ Python 3.12.7 - Installed  
✅ Streamlit 1.31.1 - Installed  
❌ PostgreSQL - **Not Installed**  
❌ Docker - **Not Installed**

---

## 📋 Quick Start Options

### **Option A: Install PostgreSQL (Recommended)**

#### Step 1: Download & Install PostgreSQL
1. Visit: https://www.postgresql.org/download/windows/
2. Download PostgreSQL 16 (or latest)
3. Run the installer with these settings:
   - **Port**: 5432 (default)
   - **Password**: Choose a strong password (remember it!)
   - **Install pgAdmin 4**: Yes (for database management)

#### Step 2: Add PostgreSQL to PATH
After installation, add PostgreSQL to your system PATH:
```powershell
# Add to PATH (replace XX with your version number)
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
```

Or permanently add via System Environment Variables:
- Search "Environment Variables" in Windows
- Edit "Path" variable
- Add: `C:\Program Files\PostgreSQL\16\bin`

#### Step 3: Create Database
Open PowerShell and run:
```powershell
# Connect to PostgreSQL (will prompt for password)
psql -U postgres

# In psql prompt, run:
CREATE DATABASE newsrec;
CREATE USER newsrec WITH PASSWORD 'newsrec';
GRANT ALL PRIVILEGES ON DATABASE newsrec TO newsrec;
\q
```

#### Step 4: Update Database Connection
The `.env` file is already configured for local PostgreSQL:
```
DATABASE_URL=postgresql://newsrec:newsrec@localhost:5433/newsrec
```

**Change port from 5433 to 5432** (default PostgreSQL port):
```
DATABASE_URL=postgresql://newsrec:newsrec@localhost:5432/newsrec
```

#### Step 5: Run Database Migrations
```powershell
cd c:\Users\vamshikrishna\Desktop\AL-Task\news-recsys-platform-self-trained

# Run the migration script
psql -U newsrec -d newsrec -f migrations/001_init_schema.sql
```

#### Step 6: Install Backend Dependencies
```powershell
# Navigate to backend
cd backend

# Install dependencies (if requirements.txt exists)
pip install fastapi uvicorn psycopg[binary] psycopg-pool pydantic-settings python-dotenv numpy faiss-cpu
```

#### Step 7: Start Backend Server
```powershell
# From project root
cd c:\Users\vamshikrishna\Desktop\AL-Task\news-recsys-platform-self-trained

# Start FastAPI backend
uvicorn backend.app.main:app --reload --port 8000
```

#### Step 8: Start Frontend (New Terminal)
```powershell
# Open a NEW terminal window
cd c:\Users\vamshikrishna\Desktop\AL-Task\news-recsys-platform-self-trained\frontend

# Run Streamlit
streamlit run app.py
```

---

### **Option B: Use Docker Desktop**

#### Step 1: Install Docker Desktop
1. Download: https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Start Docker Desktop

#### Step 2: Start PostgreSQL with Docker
```powershell
cd c:\Users\vamshikrishna\Desktop\AL-Task\news-recsys-platform-self-trained

# Start PostgreSQL container
docker compose up -d

# Check if running
docker compose ps
```

#### Step 3: Run Database Migrations
```powershell
# Connect to the container and run migrations
docker compose exec postgres psql -U newsrec -d newsrec -f /migrations/001_init_schema.sql

# Or copy the file and run it
docker cp migrations/001_init_schema.sql news-recsys-platform-self-trained-postgres-1:/tmp/
docker compose exec postgres psql -U newsrec -d newsrec -f /tmp/001_init_schema.sql
```

#### Step 4: Install Backend Dependencies & Start
```powershell
# Install dependencies
pip install fastapi uvicorn psycopg[binary] psycopg-pool pydantic-settings python-dotenv numpy faiss-cpu

# Start backend (from project root)
uvicorn backend.app.main:app --reload --port 8000
```

#### Step 5: Start Frontend
```powershell
# New terminal
cd frontend
streamlit run app.py
```

---

### **Option C: Frontend Only (No Backend)**

If you just want to see the frontend UI without the recommendation engine:

```powershell
cd c:\Users\vamshikrishna\Desktop\AL-Task\news-recsys-platform-self-trained\frontend
streamlit run app.py
```

> **Note**: This will use SQLite for user authentication but won't have live recommendations from the backend.

---

## 🔍 Verification Steps

### Check PostgreSQL is Running
```powershell
# Test connection
psql -U newsrec -d newsrec -c "SELECT 1;"
```

### Check Backend is Running
Open browser: http://localhost:8000/health

Expected response:
```json
{
  "status": "ok",
  "db": 1
}
```

### Check Frontend is Running
Open browser: http://localhost:8501

You should see the login page.

---

## 📊 Project Architecture

```
┌─────────────────┐
│   Frontend      │  Streamlit (Port 8501)
│   (Streamlit)   │  - User Interface
└────────┬────────┘  - Authentication
         │           - News Feed Display
         │
         ▼
┌─────────────────┐
│   Backend       │  FastAPI (Port 8000)
│   (FastAPI)     │  - Recommendations API
└────────┬────────┘  - Click Tracking
         │           - Session Management
         │
         ▼
┌─────────────────┐
│   Database      │  PostgreSQL (Port 5432/5433)
│  (PostgreSQL)   │  - User Data
└─────────────────┘  - Impressions & Clicks
                     - Model Versions
```

---

## 🐛 Troubleshooting

### Issue: "psql: command not found"
**Solution**: PostgreSQL not in PATH. Add it manually or use full path:
```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
```

### Issue: "Connection refused" on backend
**Solution**: Ensure PostgreSQL is running:
```powershell
# Check service
Get-Service -Name "*postgres*"

# Start service if stopped
Start-Service postgresql-x64-16
```

### Issue: Port 5432 already in use
**Solution**: Either:
1. Stop the existing PostgreSQL service
2. Or use port 5433 (as configured in docker-compose.yml)

### Issue: "Module not found" errors
**Solution**: Install missing dependencies:
```powershell
pip install -r frontend/requirements.txt
pip install fastapi uvicorn psycopg[binary] psycopg-pool pydantic-settings
```

---

## 📝 Next Steps After Setup

1. **Create an account** in the frontend
2. **Browse the news feed** (will show recommendations once backend is connected)
3. **Check analytics** to see your reading patterns
4. **Explore the content catalog** with 160K+ articles

---

## 🎯 Quick Commands Reference

```powershell
# Start PostgreSQL (if installed as service)
Start-Service postgresql-x64-16

# Start Backend
uvicorn backend.app.main:app --reload --port 8000

# Start Frontend
cd frontend && streamlit run app.py

# Stop PostgreSQL
Stop-Service postgresql-x64-16

# View logs
docker compose logs -f  # (if using Docker)
```

---

**Need Help?** Check the conversation history or ask for specific guidance on any step!
