import random
from typing import List, Dict, Tuple
from .data_service import data_service
from ..core.models import Recipe
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        self.data_service = data_service
    
    def search_and_recommend(self, query: str, search_type: str = 'all', 
                           num_results: int = 6, include_random: bool = True) -> List[Recipe]:
        """
        Search and recommend recipes
        Args:
            query: Search keywords
            search_type: Search type ('all', 'name', 'ingredient', 'category', 'area', 'first_letter')
            num_results: Number of results to return
            include_random: Whether to include random recommendations
        """
        logger.info(f"Searching recipes: '{query}', type: {search_type}, count: {num_results}")
        
        # Execute search
        search_results = self.data_service.search_recipes(query, search_type)
        
        # If search results are insufficient, add random recommendations
        if len(search_results) < num_results and include_random:
            random_count = num_results - len(search_results)
            random_recipes = self.data_service.get_random_recipes(random_count)
            
            # Avoid duplicates
            existing_ids = {r.id for r in search_results}
            additional_recipes = [r for r in random_recipes if r.id not in existing_ids]
            
            search_results.extend(additional_recipes[:random_count])
        
        # Limit result count
        return search_results[:num_results]
    
    def get_ingredient_based_recommendations(self, ingredients: List[str], 
                                           num_results: int = 6) -> List[Recipe]:
        """Get recommendations based on ingredients"""
        logger.info(f"Getting ingredient-based recommendations: {ingredients}")
        
        recommendations = []
        session = self.data_service.db.get_session()
        
        try:
            # Search for recipes related to each ingredient
            for ingredient in ingredients:
                recipes = session.query(Recipe).filter(
                    Recipe.ingredients.any(lambda x: ingredient.lower() in x.lower())
                ).all()
                recommendations.extend(recipes)
            
            # Remove duplicates and sort by match score
            unique_recipes = {}
            for recipe in recommendations:
                if recipe.id not in unique_recipes:
                    # Calculate match score (number of matching ingredients)
                    match_count = sum(1 for ing in ingredients 
                                    if any(ing.lower() in r_ing.lower() 
                                          for r_ing in recipe.ingredients))
                    unique_recipes[recipe.id] = (recipe, match_count)
            
            # Sort by match score
            sorted_recipes = sorted(unique_recipes.values(), 
                                  key=lambda x: x[1], reverse=True)
            
            return [recipe for recipe, _ in sorted_recipes[:num_results]]
            
        finally:
            self.data_service.db.close_session(session)
    
    def get_category_recommendations(self, category: str, num_results: int = 6) -> List[Recipe]:
        """Get recommendations based on category"""
        logger.info(f"Getting category-based recommendations: {category}")
        return self.data_service.search_recipes(category, 'category')[:num_results]
    
    def get_random_recommendations(self, num_results: int = 6) -> List[Recipe]:
        """Get random recommendations"""
        logger.info(f"Getting random recommendations for {num_results} recipes")
        return self.data_service.get_random_recipes(num_results)
    
    def get_trending_recipes(self, num_results: int = 6) -> List[Recipe]:
        """Get trending recipes (based on recently added)"""
        logger.info(f"Getting trending recipes for {num_results} recipes")
        session = self.data_service.db.get_session()
        
        try:
            recipes = session.query(Recipe).order_by(
                Recipe.created_at.desc()
            ).limit(num_results).all()
            return recipes
        finally:
            self.data_service.db.close_session(session)
    
    def get_similar_recipes(self, recipe: Recipe, num_results: int = 6) -> List[Recipe]:
        """Get similar recipes"""
        logger.info(f"Getting similar recipes to '{recipe.name}'")
        
        session = self.data_service.db.get_session()
        
        try:
            # Similarity based on category and ingredients
            similar_recipes = session.query(Recipe).filter(
                (Recipe.category == recipe.category) |
                (Recipe.area == recipe.area)
            ).filter(Recipe.id != recipe.id).all()
            
            # Calculate similarity score
            scored_recipes = []
            for similar_recipe in similar_recipes:
                score = 0
                
                # Category match
                if similar_recipe.category == recipe.category:
                    score += 2
                
                # Area match
                if similar_recipe.area == recipe.area:
                    score += 1
                
                # Ingredient match
                common_ingredients = set(recipe.ingredients) & set(similar_recipe.ingredients)
                score += len(common_ingredients) * 0.5
                
                scored_recipes.append((similar_recipe, score))
            
            # Sort by score
            scored_recipes.sort(key=lambda x: x[1], reverse=True)
            
            return [recipe for recipe, _ in scored_recipes[:num_results]]
            
        finally:
            self.data_service.db.close_session(session)
    
    def get_personalized_recommendations(self, user_preferences: Dict, 
                                       num_results: int = 6) -> List[Recipe]:
        """Get personalized recommendations"""
        logger.info("Generating personalized recommendations")
        
        recommendations = []
        
        # Based on preferred categories
        if 'categories' in user_preferences:
            for category in user_preferences['categories']:
                cat_recipes = self.get_category_recommendations(category, 2)
                recommendations.extend(cat_recipes)
        
        # Based on preferred ingredients
        if 'ingredients' in user_preferences:
            ing_recipes = self.get_ingredient_based_recommendations(
                user_preferences['ingredients'], 3
            )
            recommendations.extend(ing_recipes)
        
        # If insufficient recommendations, add random ones
        if len(recommendations) < num_results:
            random_count = num_results - len(recommendations)
            random_recipes = self.get_random_recommendations(random_count)
            recommendations.extend(random_recipes)
        
        # Remove duplicates and limit count
        unique_recipes = []
        seen_ids = set()
        for recipe in recommendations:
            if recipe.id not in seen_ids:
                unique_recipes.append(recipe)
                seen_ids.add(recipe.id)
                if len(unique_recipes) >= num_results:
                    break
        
        return unique_recipes

# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
