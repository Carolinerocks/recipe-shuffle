from ..core.models import db_manager, Recipe
from ..api.client import api_client
from typing import List, Dict, Optional
import logging
from sqlalchemy import func

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeDataService:
    def __init__(self):
        self.db = db_manager
        self.api = api_client
    
    def fetch_and_store_random_recipes(self, count: int = 10) -> List[Recipe]:
        """Fetch and store random recipes"""
        logger.info(f"Starting to fetch {count} random recipes...")
        
        # Get random recipes from API
        meals = self.api.get_random_meals(count)
        stored_recipes = []
        
        session = self.db.get_session()
        try:
            for meal in meals:
                # Parse recipe data
                parsed_meal = self.api.parse_meal_data(meal)
                
                # Check if already exists
                existing_recipe = session.query(Recipe).filter(
                    Recipe.meal_id == parsed_meal['meal_id']
                ).first()
                
                if existing_recipe:
                    logger.info(f"Recipe {parsed_meal['name']} already exists, skipping")
                    stored_recipes.append(existing_recipe)
                    continue
                
                # Create new recipe record
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
                stored_recipes.append(recipe)
                logger.info(f"Successfully stored recipe: {parsed_meal['name']}")
            
            session.commit()
            logger.info(f"Successfully stored {len(stored_recipes)} recipes")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to store recipes: {e}")
            raise e
        finally:
            self.db.close_session(session)
        
        return stored_recipes
    
    def search_recipes(self, query: str, search_type: str = 'all') -> List[Recipe]:
        """Search recipes"""
        session = self.db.get_session()
        try:
            if search_type == 'name':
                # Search by name
                recipes = session.query(Recipe).filter(
                    Recipe.name.ilike(f'%{query}%')
                ).all()
            elif search_type == 'ingredient':
                # Search by ingredient using array_to_string
                recipes = session.query(Recipe).filter(
                    func.array_to_string(Recipe.ingredients, ',').ilike(f'%{query.lower()}%')
                ).all()
            elif search_type == 'category':
                # Search by category
                recipes = session.query(Recipe).filter(
                    Recipe.category.ilike(f'%{query}%')
                ).all()
            elif search_type == 'area':
                # Search by area/cuisine
                recipes = session.query(Recipe).filter(
                    Recipe.area.ilike(f'%{query}%')
                ).all()
            elif search_type == 'first_letter':
                # Search by first letter
                recipes = session.query(Recipe).filter(
                    Recipe.name.ilike(f'{query}%')
                ).all()
            else:
                # Comprehensive search
                recipes = session.query(Recipe).filter(
                    (Recipe.name.ilike(f'%{query}%')) |
                    (Recipe.category.ilike(f'%{query}%')) |
                    (Recipe.area.ilike(f'%{query}%')) |
                    (func.array_to_string(Recipe.ingredients, ',').ilike(f'%{query.lower()}%'))
                ).all()
            
            return recipes
        finally:
            self.db.close_session(session)
    
    def get_random_recipes(self, count: int = 5) -> List[Recipe]:
        """Get random recipes"""
        session = self.db.get_session()
        try:
            recipes = session.query(Recipe).order_by(Recipe.id.desc()).limit(count).all()
            return recipes
        finally:
            self.db.close_session(session)
    
    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Get recipe by ID"""
        session = self.db.get_session()
        try:
            recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()
            return recipe
        finally:
            self.db.close_session(session)
    
    def get_all_categories(self) -> List[str]:
        """Get all categories"""
        session = self.db.get_session()
        try:
            categories = session.query(Recipe.category).distinct().all()
            return [cat[0] for cat in categories if cat[0]]
        finally:
            self.db.close_session(session)
    
    def get_all_ingredients(self) -> List[str]:
        """Get all ingredients"""
        session = self.db.get_session()
        try:
            recipes = session.query(Recipe.ingredients).all()
            all_ingredients = set()
            for recipe_ingredients in recipes:
                if recipe_ingredients[0]:
                    all_ingredients.update(recipe_ingredients[0])
            return sorted(list(all_ingredients))
        finally:
            self.db.close_session(session)
    
    def get_recipe_count(self) -> int:
        """Get total recipe count"""
        session = self.db.get_session()
        try:
            count = session.query(Recipe).count()
            return count
        finally:
            self.db.close_session(session)
    
    def sync_with_api(self, count: int = 50):
        """Sync data with API"""
        logger.info(f"Starting to sync {count} recipes with TheMealDB API...")
        
        # Get random recipes
        meals = self.api.get_random_meals(count)
        stored_count = 0
        skipped_count = 0
        
        session = self.db.get_session()
        try:
            for meal in meals:
                parsed_meal = self.api.parse_meal_data(meal)
                
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
                    stored_count += 1
                else:
                    skipped_count += 1
            
            session.commit()
            logger.info(f"Sync completed: {stored_count} new recipes added, {skipped_count} already existed")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Sync failed: {e}")
            raise e
        finally:
            self.db.close_session(session)
        
        return stored_count, skipped_count

# Global data service instance
data_service = RecipeDataService()
