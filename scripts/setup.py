#!/usr/bin/env python3
"""
Recipe Recommendation System One-Click Setup Script
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run command and display results"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False
    return True

def main():
    """Main function"""
    print("🚀 Recipe Recommendation System One-Click Setup")
    print("=" * 50)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    try:
        import streamlit
        import requests
        import psycopg2
        import sqlalchemy
        import pandas
        from dotenv import load_dotenv
        from PIL import Image
        print("✅ All dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check database connection
    print("\n🗄️ Checking database connection...")
    if not run_command("python -c \"from backend.core.models import db_manager; print('OK' if db_manager.test_connection() else 'FAIL')\"", "Database connection test"):
        print("❌ Database connection failed, please check configuration")
        sys.exit(1)
    
    # Initialize database
    print("\n🏗️ Initializing database...")
    if not run_command("python -c \"from backend.core.models import db_manager; db_manager.create_tables(); print('OK')\"", "Create database tables"):
        print("❌ Database initialization failed")
        sys.exit(1)
    
    # Check existing data
    print("\n📊 Checking existing data...")
    result = subprocess.run("python -c \"from backend.services.data_service import data_service; print(data_service.get_recipe_count())\"", 
                          shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        # Extract just the number from the output
        output_lines = result.stdout.strip().split('\n')
        for line in output_lines:
            if line.isdigit():
                current_count = int(line)
                break
        else:
            current_count = 0
        print(f"Current database has {current_count} recipes")
        
        if current_count == 0:
            print("\n🔄 Starting data sync...")
            print("⚠️  This may take a few minutes, please be patient...")
            
            # Run data sync
            if not run_command("python scripts/sync/quick_sync.py", "Sync data"):
                print("❌ Data sync failed")
                sys.exit(1)
        else:
            print("✅ Database already has data, skipping sync")
    else:
        print("❌ Unable to check data status")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("🌐 Start application: python run.py")
    print("📱 Access URL: http://localhost:8501")
    print("=" * 50)

if __name__ == "__main__":
    main()
