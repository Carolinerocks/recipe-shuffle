#!/usr/bin/env python3
"""
Recipe Recommendation System Test Script
"""

import sys
import os

def test_imports():
    """Test all module imports"""
    print("🔍 Testing module imports...")
    
    try:
        from config import DB_CONFIG, MEALDB_API_BASE_URL
        print("✅ config module import successful")
    except Exception as e:
        print(f"❌ config module import failed: {e}")
        return False
    
    try:
        from database import db_manager, Recipe
        print("✅ database module import successful")
    except Exception as e:
        print(f"❌ database module import failed: {e}")
        return False
    
    try:
        from api_client import api_client
        print("✅ api_client module import successful")
    except Exception as e:
        print(f"❌ api_client module import failed: {e}")
        return False
    
    try:
        from data_service import data_service
        print("✅ data_service module import successful")
    except Exception as e:
        print(f"❌ data_service module import failed: {e}")
        return False
    
    try:
        from recommendation_engine import recommendation_engine
        print("✅ recommendation_engine module import successful")
    except Exception as e:
        print(f"❌ recommendation_engine module import failed: {e}")
        return False
    
    return True

def test_api_connection():
    """Test API connection"""
    print("\n🌐 Testing TheMealDB API connection...")
    
    try:
        from api_client import api_client
        meals = api_client.get_random_meals(1)
        if meals:
            print("✅ API connection successful")
            print(f"   Got recipe: {meals[0].get('strMeal', 'Unknown')}")
            return True
        else:
            print("❌ API returned empty data")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from database import db_manager
        if db_manager.test_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Please check database configuration and connection")
        return False

def test_data_operations():
    """Test data operations"""
    print("\n📊 Testing data operations...")
    
    try:
        from data_service import data_service
        
        # Test getting recipe count
        count = data_service.get_recipe_count()
        print(f"✅ Current database has {count} recipes")
        
        # Test search functionality
        recipes = data_service.search_recipes("chicken", "all")
        print(f"✅ Search 'chicken' found {len(recipes)} recipes")
        
        return True
    except Exception as e:
        print(f"❌ Data operations failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Recipe Recommendation System Test Started\n")
    
    # Test module imports
    if not test_imports():
        print("\n❌ Module import test failed, please check dependency installation")
        sys.exit(1)
    
    # Test API connection
    api_ok = test_api_connection()
    
    # Test database connection
    db_ok = test_database_connection()
    
    # Test data operations
    if db_ok:
        data_ok = test_data_operations()
    else:
        data_ok = False
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"   Module Import: {'✅' if True else '❌'}")
    print(f"   API Connection: {'✅' if api_ok else '❌'}")
    print(f"   Database Connection: {'✅' if db_ok else '❌'}")
    print(f"   Data Operations: {'✅' if data_ok else '❌'}")
    
    if api_ok and db_ok and data_ok:
        print("\n🎉 All tests passed! System can run normally")
        print("   Run 'python run.py' to start the application")
    else:
        print("\n⚠️  Some tests failed, please check configuration")
        if not db_ok:
            print("   Please ensure PostgreSQL is installed and running")
            print("   Please check database configuration in .env file")
        if not api_ok:
            print("   Please check network connection")

if __name__ == "__main__":
    main()
