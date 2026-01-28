#!/usr/bin/env python
"""
Quick start script for MIND News Recommendation System
"""
import os
import sys
from pathlib import Path

def setup_environment():
    """Setup project environment"""
    print("🚀 MIND Recommendation System - Quick Setup")
    print("=" * 50)
    
    # Create .env file if not exists
    if not Path(".env").exists():
        print("\n📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("""# Backend Configuration
BACKEND_URL=http://localhost:8000

# Database Configuration
DATABASE_PATH=./database/recsys.db

# App Configuration
DEBUG_MODE=True
APP_NAME=MIND Recommendation System

# Security
SESSION_TIMEOUT=604800
PASSWORD_MIN_LENGTH=8
EMAIL_VERIFICATION_ENABLED=True
""")
        print("✅ .env file created")
    
    # Initialize database
    print("\n🗄️  Initializing database...")
    try:
        from database.db_init import init_db
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    # Create test account
    print("\n👤 Creating test account...")
    try:
        from database.db_init import register_user, verify_email
        
        # Register test user
        result = register_user("testuser", "test@example.com", "TestPassword123", "Test User")
        
        if result['success']:
            user_id = result['user_id']
            verification_code = result.get('verification_code', '')
            
            # Verify email
            verify_result = verify_email(user_id, verification_code)
            
            if verify_result['success']:
                print(f"✅ Test account created:")
                print(f"   Username: testuser")
                print(f"   Password: TestPassword123")
                print(f"   Email: test@example.com")
            else:
                print(f"⚠️  Account created but email verification failed")
        else:
            print(f"⚠️  Could not create test account (may already exist)")
    
    except Exception as e:
        print(f"❌ Error creating test account: {e}")
    
    return True

def print_next_steps():
    """Print next steps"""
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("=" * 50)
    print("""
1. INSTALL DEPENDENCIES
   pip install -r requirements.txt

2. RUN THE APPLICATION
   streamlit run app.py

3. OPEN IN BROWSER
   http://localhost:8501

4. LOGIN WITH TEST ACCOUNT
   Username: testuser
   Password: TestPassword123

5. EXPLORE THE PLATFORM
   - Check out News Feed for recommendations
   - View your reading history
   - Browse content catalog
   - Check analytics and metrics
   - Configure your preferences in Settings

📚 For more information, see README.md
""")

if __name__ == "__main__":
    try:
        if setup_environment():
            print_next_steps()
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
