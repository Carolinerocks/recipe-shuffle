#!/usr/bin/env python3
"""
Admin Tools - API Testing and System Status Check
"""

import sys
from data_service import data_service
from api_client import api_client
from database import db_manager

def test_api_connection():
    """Test API connection"""
    print("🧪 Testing TheMealDB API connection...")
    try:
        # Test random recipes
        random_meals = api_client.get_random_meals(1)
        if random_meals:
            meal_name = random_meals[0].get('strMeal', 'Unknown')
            print(f"✅ API connection successful! Got recipe: {meal_name}")
            return True
        else:
            print("⚠️ API returned empty data")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("🗄️ Testing database connection...")
    try:
        if db_manager.test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_system_status():
    """Check system status"""
    print("📊 Checking system status...")
    print("=" * 50)
    
    # Check database
    db_ok = test_database_connection()
    
    # Check API
    api_ok = test_api_connection()
    
    # Check data volume
    try:
        recipe_count = data_service.get_recipe_count()
        print(f"📚 Database has {recipe_count} recipes")
    except Exception as e:
        print(f"❌ Unable to get recipe count: {e}")
        recipe_count = 0
    
    print("=" * 50)
    
    if db_ok and recipe_count > 0:
        print("🎉 System status is good, ready to use!")
        return True
    elif db_ok and recipe_count == 0:
        print("⚠️ Database connection is normal, but no recipe data")
        print("💡 Suggestion: run python quick_sync.py")
        return False
    else:
        print("❌ System status is abnormal, please check configuration")
        return False

def show_api_info():
    """Show API information"""
    print("🔗 TheMealDB API Information")
    print("=" * 50)
    print("📡 API Base URL: https://www.themealdb.com/api/json/v1/1")
    print()
    print("🔍 Search Methods:")
    print("  - search.php?s=name     - Search by recipe name")
    print("  - search.php?f=letter   - Search by first letter")
    print("  - filter.php?i=ingredient - Filter by ingredient")
    print("  - filter.php?c=category   - Filter by category")
    print("  - filter.php?a=area       - Filter by area")
    print()
    print("📋 Query Methods:")
    print("  - lookup.php?i=id       - Get complete recipe by ID")
    print("  - random.php            - Get random recipe")
    print()
    print("📚 List Methods:")
    print("  - categories.php        - Get all categories")
    print("  - list.php?c=list       - Get all categories")
    print("  - list.php?i=list       - Get all ingredients")
    print("  - list.php?a=list       - Get all areas")
    print("=" * 50)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🔧 Admin Tools")
        print("=" * 30)
        print("Usage:")
        print("  python admin_tools.py status    - Check system status")
        print("  python admin_tools.py api       - Test API connection")
        print("  python admin_tools.py db        - Test database connection")
        print("  python admin_tools.py info      - Show API information")
        print("  python admin_tools.py all       - Run all tests")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        check_system_status()
    elif command == "api":
        test_api_connection()
    elif command == "db":
        test_database_connection()
    elif command == "info":
        show_api_info()
    elif command == "all":
        print("🔧 Running all system checks...")
        print()
        check_system_status()
        print()
        show_api_info()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python admin_tools.py' to see help")

if __name__ == "__main__":
    main()
