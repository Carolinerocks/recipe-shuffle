import requests
import json
from typing import List, Dict, Optional
from ..core.config import MEALDB_API_BASE_URL

class TheMealDBClient:
    def __init__(self):
        self.base_url = MEALDB_API_BASE_URL
        self.session = requests.Session()
    
    def get_random_meals(self, count: int = 1) -> List[Dict]:
        """Get random meals using /random.php"""
        meals = []
        for _ in range(count):
            try:
                response = self.session.get(f"{self.base_url}/random.php")
                response.raise_for_status()
                data = response.json()
                if data.get('meals') and data['meals'][0]:
                    meals.append(data['meals'][0])
            except Exception as e:
                print(f"Get random meals failed: {e}")
                continue
        return meals
    
    def search_by_name(self, name: str) -> List[Dict]:
        """Search meals by name using /search.php?s=name"""
        try:
            response = self.session.get(f"{self.base_url}/search.php", params={'s': name})
            response.raise_for_status()
            data = response.json()
            return data.get('meals', [])
        except Exception as e:
            print(f"Search by name failed: {e}")
            return []
    
    def search_by_first_letter(self, letter: str) -> List[Dict]:
        """List all meals by first letter using /search.php?f=letter"""
        try:
            response = self.session.get(f"{self.base_url}/search.php", params={'f': letter})
            response.raise_for_status()
            data = response.json()
            return data.get('meals', [])
        except Exception as e:
            print(f"Search by first letter failed: {e}")
            return []
    
    def search_by_ingredient(self, ingredient: str) -> List[Dict]:
        """Search meals by ingredient using /filter.php?i=ingredient"""
        try:
            response = self.session.get(f"{self.base_url}/filter.php", params={'i': ingredient})
            response.raise_for_status()
            data = response.json()
            return data.get('meals', [])
        except Exception as e:
            print(f"Search by ingredient failed: {e}")
            return []
    
    def search_by_category(self, category: str) -> List[Dict]:
        """Search meals by category using /filter.php?c=category"""
        try:
            response = self.session.get(f"{self.base_url}/filter.php", params={'c': category})
            response.raise_for_status()
            data = response.json()
            return data.get('meals', [])
        except Exception as e:
            print(f"Search by category failed: {e}")
            return []
    
    def get_meal_by_id(self, meal_id: str) -> Optional[Dict]:
        """Lookup full meal details by id using /lookup.php?i=id"""
        try:
            response = self.session.get(f"{self.base_url}/lookup.php", params={'i': meal_id})
            response.raise_for_status()
            data = response.json()
            meals = data.get('meals', [])
            return meals[0] if meals else None
        except Exception as e:
            print(f"Get meal by ID failed: {e}")
            return None
    
    def get_categories(self) -> List[Dict]:
        """Get all categories using /categories.php"""
        try:
            response = self.session.get(f"{self.base_url}/categories.php")
            response.raise_for_status()
            data = response.json()
            return data.get('categories', [])
        except Exception as e:
            print(f"Get categories failed: {e}")
            return []
    
    def get_ingredients(self) -> List[Dict]:
        """Get all ingredients using /list.php?i=list"""
        try:
            response = self.session.get(f"{self.base_url}/list.php", params={'i': 'list'})
            response.raise_for_status()
            data = response.json()
            return data.get('meals', [])
        except Exception as e:
            print(f"Get ingredients failed: {e}")
            return []
    
    def get_areas(self) -> List[Dict]:
        """Get all areas/cuisines using /list.php?a=list"""
        try:
            response = self.session.get(f"{self.base_url}/list.php", params={'a': 'list'})
            response.raise_for_status()
            data = response.json()
            return data.get('meals', [])
        except Exception as e:
            print(f"Get areas failed: {e}")
            return []
    
    def get_categories_list(self) -> List[Dict]:
        """Get all categories using /list.php?c=list"""
        try:
            response = self.session.get(f"{self.base_url}/list.php", params={'c': 'list'})
            response.raise_for_status()
            data = response.json()
            return data.get('meals', [])
        except Exception as e:
            print(f"Get categories list failed: {e}")
            return []
    
    def search_by_area(self, area: str) -> List[Dict]:
        """Search meals by area/cuisine using /filter.php?a=area"""
        try:
            response = self.session.get(f"{self.base_url}/filter.php", params={'a': area})
            response.raise_for_status()
            data = response.json()
            return data.get('meals', [])
        except Exception as e:
            print(f"Search by area failed: {e}")
            return []
    
    def parse_meal_data(self, meal: Dict) -> Dict:
        """Parse meal data and extract ingredients and measures"""
        ingredients = []
        measures = []
        
        # Extract ingredients and measures (up to 20)
        for i in range(1, 21):
            ingredient_key = f'strIngredient{i}'
            measure_key = f'strMeasure{i}'
            
            ingredient = meal.get(ingredient_key, '') or ''
            measure = meal.get(measure_key, '') or ''
            
            ingredient = ingredient.strip() if ingredient else ''
            measure = measure.strip() if measure else ''
            
            if ingredient and ingredient.lower() != 'null':
                ingredients.append(ingredient)
                measures.append(measure if measure and measure.lower() != 'null' else '')
        
        # Process tags
        tags = []
        str_tags = meal.get('strTags')
        if str_tags:
            tags = [tag.strip() for tag in str_tags.split(',') if tag.strip()]
        
        return {
            'meal_id': meal.get('idMeal'),
            'name': meal.get('strMeal', ''),
            'category': meal.get('strCategory', ''),
            'area': meal.get('strArea', ''),
            'instructions': meal.get('strInstructions', ''),
            'image_url': meal.get('strMealThumb', ''),
            'youtube_url': meal.get('strYoutube', ''),
            'ingredients': ingredients,
            'measures': measures,
            'tags': tags
        }

# Global API client instance
api_client = TheMealDBClient()
