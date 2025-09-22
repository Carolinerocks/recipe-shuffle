#!/usr/bin/env python3
"""
Smart Scheduled Sync Script - Automatically adjust sync strategy based on database status
"""

import sys
import time
import logging
import random
from datetime import datetime, timedelta
from data_service import data_service
from api_client import api_client
from database import db_manager, Recipe

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_sync_strategy():
    """
    Determine sync strategy based on current database status
    """
    current_count = data_service.get_recipe_count()
    
    if current_count < 100:
        # Low data volume, use quick sync
        return "quick", 50
    elif current_count < 500:
        # Medium data volume, use random sync
        return "random", 30
    else:
        # Sufficient data volume, use category sync
        return "category", 20

def quick_sync(count):
    """Quick sync - get random recipes"""
    logger.info(f"🚀 Quick sync mode, target count: {count}")
    return data_service.sync_with_api(count)

def category_sync(count):
    """Category sync - get recipes by category"""
    logger.info(f"📂 Category sync mode, target count: {count}")
    
    # Get all categories
    categories = api_client.get_categories()
    logger.info(f"📋 Found {len(categories)} categories")
    
    # Randomly select categories
    selected_categories = random.sample(categories, min(3, len(categories)))
    
    total_added = 0
    total_skipped = 0
    
    for category in selected_categories:
        category_name = category.get('strCategory', '')
        if not category_name:
            continue
            
        logger.info(f"📂 Syncing category: {category_name}")
        
        try:
            # Get recipes for this category
            meals = api_client.search_by_category(category_name)
            logger.info(f"   📄 Found {len(meals)} recipes")
            
            # Randomly select recipes
            selected_meals = random.sample(meals, min(count // len(selected_categories), len(meals)))
            
            # Store to database
            session = db_manager.get_session()
            added_count = 0
            skipped_count = 0
            
            try:
                for meal in selected_meals:
                    parsed_meal = api_client.parse_meal_data(meal)
                    
                    # Check if already exists
                    existing_recipe = session.query(Recipe).filter(
                        Recipe.meal_id == parsed_meal['meal_id']
                    ).first()
                    
                    if not existing_recipe:
                        recipe = Recipe(
                            meal_id=parsed_meal['meal_id'],
                            name=parsed_meal['name'],
                            category=parsed_meal['category'],
                            area=parsed_meal['area'],
                            instructions=parsed_meal['instructions'],
                            image_url=parsed_meal['image_url'],
                            youtube_url=parsed_meal['youtube_url'],
                            ingredients=parsed_meal['ingredients'],
                            measures=parsed_meal['measures'],
                            tags=parsed_meal['tags']
                        )
                        session.add(recipe)
                        added_count += 1
                    else:
                        skipped_count += 1
                
                session.commit()
                logger.info(f"   ✅ Completed: added {added_count}, skipped {skipped_count}")
                total_added += added_count
                total_skipped += skipped_count
                
            except Exception as e:
                session.rollback()
                logger.error(f"   ❌ Error: {e}")
            finally:
                db_manager.close_session(session)
            
            # Avoid API limits
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"   ❌ Category {category_name} sync failed: {e}")
            continue
    
    return total_added, total_skipped

def area_sync(count):
    """Area sync - get recipes by area"""
    logger.info(f"🌍 Area sync mode, target count: {count}")
    
    # Get all areas
    areas = api_client.get_areas()
    logger.info(f"🌎 Found {len(areas)} areas")
    
    # Randomly select areas
    selected_areas = random.sample(areas, min(2, len(areas)))
    
    total_added = 0
    total_skipped = 0
    
    for area in selected_areas:
        area_name = area.get('strArea', '')
        if not area_name:
            continue
            
        logger.info(f"🌍 Syncing area: {area_name}")
        
        try:
            # Get recipes for this area
            meals = api_client.search_by_area(area_name)
            logger.info(f"   📄 Found {len(meals)} recipes")
            
            # Randomly select recipes
            selected_meals = random.sample(meals, min(count // len(selected_areas), len(meals)))
            
            # Store to database
            session = db_manager.get_session()
            added_count = 0
            skipped_count = 0
            
            try:
                for meal in selected_meals:
                    parsed_meal = api_client.parse_meal_data(meal)
                    
                    # Check if already exists
                    existing_recipe = session.query(Recipe).filter(
                        Recipe.meal_id == parsed_meal['meal_id']
                    ).first()
                    
                    if not existing_recipe:
                        recipe = Recipe(
                            meal_id=parsed_meal['meal_id'],
                            name=parsed_meal['name'],
                            category=parsed_meal['category'],
                            area=parsed_meal['area'],
                            instructions=parsed_meal['instructions'],
                            image_url=parsed_meal['image_url'],
                            youtube_url=parsed_meal['youtube_url'],
                            ingredients=parsed_meal['ingredients'],
                            measures=parsed_meal['measures'],
                            tags=parsed_meal['tags']
                        )
                        session.add(recipe)
                        added_count += 1
                    else:
                        skipped_count += 1
                
                session.commit()
                logger.info(f"   ✅ Completed: added {added_count}, skipped {skipped_count}")
                total_added += added_count
                total_skipped += skipped_count
                
            except Exception as e:
                session.rollback()
                logger.error(f"   ❌ Error: {e}")
            finally:
                db_manager.close_session(session)
            
            # Avoid API limits
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"   ❌ Area {area_name} sync failed: {e}")
            continue
    
    return total_added, total_skipped

def main():
    """Main function"""
    logger.info("🧠 Smart sync script started")
    logger.info("=" * 50)
    
    # Initialize database
    try:
        db_manager.create_tables()
        logger.info("✅ Database initialization completed")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Get current status
    current_count = data_service.get_recipe_count()
    logger.info(f"📊 Current database has {current_count} recipes")
    
    # Decide sync strategy
    if len(sys.argv) > 1:
        strategy = sys.argv[1].lower()
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    else:
        strategy, count = get_sync_strategy()
    
    logger.info(f"🎯 Sync strategy: {strategy}, target count: {count}")
    
    # Execute sync
    start_time = time.time()
    
    try:
        if strategy == "quick":
            added, skipped = quick_sync(count)
        elif strategy == "category":
            added, skipped = category_sync(count)
        elif strategy == "area":
            added, skipped = area_sync(count)
        else:
            logger.error(f"❌ Unknown sync strategy: {strategy}")
            sys.exit(1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Record sync results
        final_count = data_service.get_recipe_count()
        net_new = final_count - current_count
        
        logger.info("=" * 50)
        logger.info("📊 Sync result statistics:")
        logger.info(f"   ⏱️  Duration: {duration:.2f} seconds")
        logger.info(f"   ✅ Added recipes: {added}")
        logger.info(f"   ⏭️  Skipped duplicates: {skipped}")
        logger.info(f"   📈 Net growth: {net_new}")
        logger.info(f"   📊 Current total: {final_count}")
        logger.info("=" * 50)
        
        if added > 0:
            logger.info("🎉 Smart sync completed successfully!")
        else:
            logger.info("ℹ️  No new recipes to sync")
            
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
