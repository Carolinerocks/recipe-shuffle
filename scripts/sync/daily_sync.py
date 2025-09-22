#!/usr/bin/env python3
"""
Daily Scheduled Sync Script - Automatically fetch new recipes from API and add to local database
"""

import sys
import time
import logging
from datetime import datetime
from data_service import data_service
from api_client import api_client
from database import db_manager, Recipe

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def sync_new_recipes(daily_count=20):
    """
    Sync new recipes to database
    Args:
        daily_count: Number of recipes to sync daily
    """
    logger.info(f"🔄 Starting daily sync, target count: {daily_count}")
    
    # Get current recipe count in database
    current_count = data_service.get_recipe_count()
    logger.info(f"📊 Current database has {current_count} recipes")
    
    # Sync new recipes
    try:
        added, skipped = data_service.sync_with_api(daily_count)
        logger.info(f"✅ Sync completed! Added {added} recipes, skipped {skipped} duplicate recipes")
        
        # Get count after sync
        final_count = data_service.get_recipe_count()
        logger.info(f"📈 Database now has {final_count} recipes (added {final_count - current_count})")
        
        return added, skipped, final_count - current_count
        
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        return 0, 0, 0

def sync_by_categories(daily_count=20):
    """
    Sync new recipes by category (more comprehensive sync strategy)
    """
    logger.info(f"🔄 Starting category sync, target count: {daily_count}")
    
    # Get all categories
    try:
        categories = api_client.get_categories()
        logger.info(f"📋 Found {len(categories)} categories")
    except Exception as e:
        logger.error(f"❌ Failed to get categories: {e}")
        return 0, 0, 0
    
    current_count = data_service.get_recipe_count()
    total_added = 0
    total_skipped = 0
    
    # Randomly select several categories for sync
    import random
    selected_categories = random.sample(categories, min(3, len(categories)))
    
    for category in selected_categories:
        category_name = category.get('strCategory', '')
        if not category_name:
            continue
            
        logger.info(f"📂 Syncing category: {category_name}")
        
        try:
            # Get recipes for this category
            meals = api_client.search_by_category(category_name)
            logger.info(f"   📄 Found {len(meals)} recipes")
            
            # Randomly select some recipes
            selected_meals = random.sample(meals, min(daily_count // len(selected_categories), len(meals)))
            
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
    
    final_count = data_service.get_recipe_count()
    logger.info(f"📈 Category sync completed! Added {total_added} recipes, skipped {total_skipped} duplicates")
    logger.info(f"📊 Database now has {final_count} recipes")
    
    return total_added, total_skipped, final_count - current_count

def main():
    """Main function"""
    logger.info("🚀 Daily sync script started")
    logger.info("=" * 50)
    
    # Check command line arguments
    daily_count = 20  # Default sync 20 daily
    sync_method = "random"  # Default random sync
    
    if len(sys.argv) > 1:
        try:
            daily_count = int(sys.argv[1])
        except ValueError:
            logger.error("❌ Invalid count parameter, using default value 20")
    
    if len(sys.argv) > 2:
        sync_method = sys.argv[2].lower()
    
    # Initialize database
    try:
        db_manager.create_tables()
        logger.info("✅ Database initialization completed")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Execute sync
    start_time = time.time()
    
    if sync_method == "category":
        added, skipped, net_new = sync_by_categories(daily_count)
    else:
        added, skipped, net_new = sync_new_recipes(daily_count)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Record sync results
    logger.info("=" * 50)
    logger.info("📊 Sync result statistics:")
    logger.info(f"   ⏱️  Duration: {duration:.2f} seconds")
    logger.info(f"   ✅ Added recipes: {added}")
    logger.info(f"   ⏭️  Skipped duplicates: {skipped}")
    logger.info(f"   📈 Net growth: {net_new}")
    logger.info(f"   📊 Current total: {data_service.get_recipe_count()}")
    logger.info("=" * 50)
    
    if added > 0:
        logger.info("🎉 Daily sync completed successfully!")
    else:
        logger.info("ℹ️  No new recipes to sync")

if __name__ == "__main__":
    main()
