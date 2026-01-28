# MIND Recommendation System - Frontend

## 🚀 Industrial-Grade Multi-Page Streamlit UI

A professional, enterprise-level web application for the Microsoft News Recommendation (MIND) Dataset with advanced features for personalized news recommendations using high-dimensional similarity search.

### ✨ Features

#### 🔐 **Authentication System**
- User registration with email verification
- Secure login/logout functionality
- Password hashing and session management
- Account recovery capabilities

#### 📰 **News Feed**
- Personalized recommendations based on user preferences
- Advanced filtering (category, publication date, engagement score)
- Multiple sorting options
- Detailed article view with full content
- Like, save, and share functionality

#### 📜 **User History & Debugger**
- Complete reading timeline with temporal analysis
- Advanced analytics on reading patterns
- User engagement metrics
- Recommendation system debugging tools
- Data export functionality (CSV, JSON)

#### 📚 **Content Catalog**
- Browse all 160K+ articles from MIND dataset
- Advanced search and filtering
- Entity-based filtering
- Multi-view display (list/grid)
- Pagination and sorting

#### 📊 **Analytics & Metrics**
- Personal analytics dashboard
- System performance metrics
- Recommendation accuracy analysis
- Trend analysis
- A/B testing results
- User engagement insights

#### ⚙️ **Settings & Preferences**
- Profile management
- Content preferences customization
- Privacy & data management
- Notification preferences
- Session management

### 📋 Project Structure

```
frontend/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── .env.example                    # Environment variables template
│
├── database/
│   ├── __init__.py
│   └── db_init.py                 # Database initialization & queries
│
├── utils/
│   ├── __init__.py
│   ├── auth.py                     # Authentication utilities
│   ├── ui_helpers.py               # UI/UX helper functions
│   └── api_client.py               # Backend API client
│
├── pages/
│   ├── __init__.py
│   ├── auth.py                     # Login & Sign Up pages
│   ├── home.py                     # Home/Dashboard page
│   ├── news_feed.py                # News Feed page
│   ├── user_history.py             # User History & Debugger
│   ├── content_catalog.py          # Content Catalog page
│   ├── analytics.py                # Analytics page
│   └── settings.py                 # Settings page
│
└── assets/                         # Images and static files
```

### 🛠️ Installation & Setup

#### **Prerequisites**
- Python 3.8+
- pip or conda
- Git

#### **1. Clone the repository**
```bash
cd news-recsys-platform-self-trained/frontend
```

#### **2. Create virtual environment**
```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### **3. Install dependencies**
```bash
pip install -r requirements.txt
```

#### **4. Setup environment variables**
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your configuration
# Key variables:
# - BACKEND_URL: Your backend API URL (default: http://localhost:8000)
# - DATABASE_PATH: Path to SQLite database
# - DEBUG_MODE: Enable debug logging
```

#### **5. Initialize database**
```bash
python -c "from database.db_init import init_db; init_db(); print('Database initialized!')"
```

#### **6. Run the application**
```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

### 🎯 Usage Guide

#### **First Time Setup**

1. **Create Account**
   - Click "Sign Up" button in sidebar
   - Enter username, email, password, and full name
   - Verify email with the code sent
   - Login with your credentials

2. **Set Preferences**
   - Go to Settings → Preferences
   - Select your interests (Technology, Business, Sports, etc.)
   - Configure reading preferences
   - Choose notification settings

3. **Explore News**
   - Navigate to News Feed
   - Browse personalized recommendations
   - Click articles to read full content
   - Like or save articles for later

#### **Key Pages**

| Page | Purpose |
|------|---------|
| **Home** | Dashboard with quick stats and overview |
| **News Feed** | Personalized recommendations with filtering |
| **My History** | Reading timeline, analytics, and debugging |
| **Content Catalog** | Browse all articles with advanced search |
| **Analytics** | System metrics and user insights |
| **Settings** | Account and preference management |

### 🔗 Backend Integration

The frontend communicates with the backend API using the `APIClient` class in `utils/api_client.py`.

#### **Expected Backend Endpoints**

```python
GET  /recommendations/{user_id}           # Get recommendations
POST /clicks                              # Record user click
GET  /session/{user_id}/history          # Get user history
GET  /content/{article_id}               # Get article info
GET  /metrics                            # Get system metrics
```

#### **Configuration**

Update `BACKEND_URL` in `.env` file:
```
BACKEND_URL=http://localhost:8000
```

### 🎨 UI/UX Features

#### **Professional Design**
- Modern gradient color scheme (Blue: #0066cc, Cyan: #00a8e8)
- Responsive layout with Streamlit columns
- Custom CSS for enhanced styling
- Smooth animations and transitions

#### **Accessibility**
- Clear navigation structure
- Descriptive labels and help text
- Keyboard-friendly inputs
- High contrast colors

#### **Performance**
- Cached components with `@st.cache_resource`
- Optimized database queries
- Efficient API calls
- Session-based state management

### 📊 Database Schema

#### **Tables**

1. **users** - User account information
   - user_id (PK), username, email, password_hash, full_name, is_verified, created_at, last_login

2. **email_verifications** - Email verification tracking
   - verification_id (PK), user_id (FK), verification_code, expires_at, is_used

3. **sessions** - Active user sessions
   - session_id (PK), user_id (FK), session_token, expires_at, is_active

4. **user_history** - User interaction history
   - history_id (PK), user_id (FK), article_id, action_type, category, timestamp, dwell_time

5. **recommendations** - Recommendation records
   - recommendation_id (PK), user_id (FK), article_id, score, rank, method, created_at

6. **system_logs** - System audit logs
   - log_id (PK), user_id (FK), action, details, timestamp

### 🔐 Security Features

- **Password Security**: SHA-256 hashing for all passwords
- **Session Management**: Secure tokens with expiration
- **Email Verification**: Required for account activation
- **SQL Injection Protection**: Parameterized queries
- **CORS**: Configurable cross-origin requests
- **Rate Limiting**: Configurable request limits

### 📈 Scalability Considerations

#### **For Production Deployment**

1. **Database**: Replace SQLite with PostgreSQL
   ```python
   import psycopg2
   # Update connection in db_init.py
   ```

2. **Caching**: Add Redis for session/data caching
   ```python
   import redis
   cache = redis.Redis(host='localhost', port=6379)
   ```

3. **Authentication**: Implement JWT tokens
   ```python
   import jwt
   # Replace session-based auth
   ```

4. **Deployment**: Use Docker and Kubernetes
   - See `docker-compose.yml` in root directory

### 🧪 Testing

#### **Unit Tests** (Create `tests/` directory)
```python
# tests/test_auth.py
import pytest
from database.db_init import register_user, authenticate_user

def test_register_user():
    result = register_user("testuser", "test@example.com", "password123", "Test User")
    assert result['success'] == True
```

Run tests:
```bash
pytest tests/ -v
```

### 📝 Configuration

#### **Streamlit Config** (`.streamlit/config.toml`)
```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"

[server]
port = 8501
headless = true
```

#### **Environment Variables** (`.env`)
```
BACKEND_URL=http://localhost:8000
DEBUG_MODE=True
DATABASE_PATH=./database/recsys.db
```

### 🐛 Troubleshooting

#### **Issue: "ModuleNotFoundError"**
```bash
# Solution: Ensure all imports are correct
python -c "import streamlit; print(streamlit.__version__)"
```

#### **Issue: Database lock**
```bash
# Solution: Remove database file and reinitialize
rm database/recsys.db
python -c "from database.db_init import init_db; init_db()"
```

#### **Issue: Connection refused (backend)**
```bash
# Solution: Ensure backend is running
# Start backend on port 8000, then start frontend:
streamlit run app.py
```

### 📚 API Documentation

#### **Authentication Endpoints**

```python
# Register user
POST /auth/register
{
    "username": "user123",
    "email": "user@example.com",
    "password": "secure_password",
    "full_name": "Full Name"
}

# Login
POST /auth/login
{
    "username": "user123",
    "password": "secure_password"
}

# Verify email
POST /auth/verify
{
    "user_id": 1,
    "verification_code": "123456"
}
```

### 🎯 Development Roadmap

- [ ] Multi-language support (i18n)
- [ ] Advanced recommendation algorithms
- [ ] Social features (follow, share recommendations)
- [ ] Mobile app (React Native)
- [ ] Real-time notifications (WebSocket)
- [ ] Advanced user segmentation
- [ ] A/B testing framework
- [ ] Custom recommendation models

### 📞 Support & Contribution

For issues, feature requests, or contributions:
1. Create an issue on GitHub
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

### 📄 License

This project is part of the MIND Dataset research. See LICENSE file for details.

### 🙏 Acknowledgments

- Microsoft News Dataset (MIND) team
- Streamlit framework
- FastAPI backend
- Contributors and testers

---

**Version**: 1.0.0  
**Last Updated**: January 27, 2025  
**Status**: Production Ready
