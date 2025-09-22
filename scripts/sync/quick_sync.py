#!/usr/bin/env python3
"""
Quick sync of small amount of data for testing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.services.data_service import data_service
from backend.core.models import db_manager

def main():
    """Quick sync 100 random recipes"""
    print("🚀 Quick syncing 100 random recipes...")
    
    # Initialize database
    try:
        db_manager.create_tables()
        print("✅ Database initialization completed")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return
    
    # Check current data volume
    current_count = data_service.get_recipe_count()
    print(f"📊 Current database has {current_count} recipes")
    
    # Sync data
    try:
        added, skipped = data_service.sync_with_api(100)
        print(f"✅ Sync completed! Added {added} recipes, skipped {skipped} duplicate recipes")
        
        final_count = data_service.get_recipe_count()
        print(f"📊 Final database has {final_count} recipes")
        
        if final_count > 0:
            print("🎯 Now you can start the application!")
            print("   Run: python run.py")
        else:
            print("❌ Sync failed, database is empty")
            
    except Exception as e:
        print(f"❌ Sync failed: {e}")

if __name__ == "__main__":
    main()
