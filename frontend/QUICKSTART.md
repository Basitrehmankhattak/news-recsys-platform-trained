# MIND Recommendation System - Quick Start Guide

## 🚀 5-Minute Quick Start

### Step 1: Install Dependencies
```bash
cd frontend
pip install -r requirements.txt
```

### Step 2: Setup Environment
```bash
python setup.py
```

This will:
- ✅ Create `.env` file with default configuration
- ✅ Initialize SQLite database
- ✅ Create a test user account

### Step 3: Run Application
```bash
streamlit run app.py
```

### Step 4: Login
- **Username**: `testuser`
- **Password**: `TestPassword123`
- **Email**: `test@example.com`

## 📌 Key URLs

- **Main App**: http://localhost:8501
- **Backend API**: http://localhost:8000 (if running)

## 🎯 Features to Try

### 1. **News Feed** 📰
- Browse personalized recommendations
- Filter by category and engagement score
- Read full article details
- Like, save, and share articles

### 2. **Reading History** 📜
- View your complete reading timeline
- See engagement metrics
- Export data as CSV/JSON
- Access debugging information

### 3. **Content Catalog** 📚
- Browse all 160K articles
- Advanced search and filtering
- Filter by entities and engagement
- Grid or list view

### 4. **Analytics** 📊
- Personal reading statistics
- System performance metrics
- Recommendation analysis
- Trend insights

### 5. **Settings** ⚙️
- Update profile
- Customize preferences
- Privacy & security settings
- Notification management

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Backend
BACKEND_URL=http://localhost:8000

# Database
DATABASE_PATH=./database/recsys.db

# App
DEBUG_MODE=True
APP_NAME=MIND Recommendation System

# Security
SESSION_TIMEOUT=604800
PASSWORD_MIN_LENGTH=8
EMAIL_VERIFICATION_ENABLED=True
```

### Streamlit Config (`.streamlit/config.toml`)

Customize theme, port, and server settings:

```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"

[server]
port = 8501
```

## 📚 User Accounts

### Test Account
- Username: `testuser`
- Email: `test@example.com`
- Password: `TestPassword123`

### Create New Account
1. Click "Sign Up" in the sidebar
2. Enter credentials
3. Verify email (use verification code from console)
4. Login

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Database Errors
```bash
# Reinitialize database
rm database/recsys.db
python setup.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## 📁 Project Structure

```
frontend/
├── app.py                    # Main application
├── setup.py                  # Quick setup script
├── requirements.txt          # Dependencies
├── database/                 # Database module
│   └── db_init.py           # Database functions
├── utils/                   # Utilities
│   ├── auth.py              # Authentication
│   ├── ui_helpers.py        # UI functions
│   └── api_client.py        # API client
├── pages/                   # Page modules
│   ├── auth.py              # Auth pages
│   ├── home.py              # Home page
│   ├── news_feed.py         # News feed
│   ├── user_history.py      # History & debugger
│   ├── content_catalog.py   # Catalog
│   ├── analytics.py         # Analytics
│   └── settings.py          # Settings
└── .streamlit/              # Streamlit config
    └── config.toml
```

## 🔌 Backend Integration

To connect to your FastAPI backend:

1. **Start your backend server** (port 8000)
2. **Update `.env`**:
   ```
   BACKEND_URL=http://localhost:8000
   ```
3. **API endpoints used**:
   - `GET /recommendations/{user_id}`
   - `POST /clicks`
   - `GET /session/{user_id}/history`
   - `GET /content/{article_id}`
   - `GET /metrics`

## 📊 Demo Data

The application comes with sample data:
- **6 Sample articles** in News Feed
- **20 Sample articles** in Content Catalog
- **10 Sample history entries** in User History
- **Simulated analytics** and metrics

These can be replaced with real data from your backend API.

## 💾 Database

SQLite database automatically created at:
```
./database/recsys.db
```

### Tables:
- `users` - User accounts
- `email_verifications` - Email verification
- `sessions` - Active sessions
- `user_history` - Reading history
- `recommendations` - Recommendations
- `system_logs` - System audit logs

## 🎨 Customization

### Theme Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#0066cc"      # Change primary color
backgroundColor = "#ffffff"    # Change background
```

### Add New Page
1. Create `pages/new_page.py`
2. Add to navigation in `app.py`
3. Import in `pages/__init__.py`

## 🚢 Deployment

### Production Setup

1. **Install gunicorn for Streamlit**:
   ```bash
   pip install gunicorn streamlit
   ```

2. **Create `run.sh`**:
   ```bash
   #!/bin/bash
   streamlit run app.py \
       --server.port 80 \
       --server.address 0.0.0.0 \
       --logger.level=warning
   ```

3. **With Docker**:
   See `docker-compose.yml` in root directory

## 📞 Support

For issues or questions:
1. Check README.md for detailed documentation
2. Review `.env.example` for configuration
3. Check browser console for errors
4. Verify backend is running on correct port

## 📈 Next Steps

1. ✅ Run the application
2. ✅ Test with sample data
3. ✅ Connect to real backend
4. ✅ Customize for your needs
5. ✅ Deploy to production

---

**Happy exploring!** 🎉

For detailed documentation, see [README.md](README.md)
