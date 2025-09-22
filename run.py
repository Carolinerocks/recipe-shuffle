#!/usr/bin/env python3
"""
Recipe Recommendation System Startup Script
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import streamlit
        import requests
        import psycopg2
        import sqlalchemy
        import pandas
        from dotenv import load_dotenv
        from PIL import Image
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_database_connection():
    """Check database connection"""
    try:
        from backend.core.models import db_manager
        if db_manager.test_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting Recipe Recommendation System...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        print("⚠️  Database connection failed, but can continue running (some features may be unavailable)")
    
    # Start Streamlit application
    try:
        print("🌐 Starting web interface...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Startup failed: {e}")

if __name__ == "__main__":
    main()
