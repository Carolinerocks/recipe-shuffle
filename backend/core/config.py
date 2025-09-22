import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'recipe_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# TheMealDB API configuration
MEALDB_API_BASE_URL = os.getenv('MEALDB_API_BASE_URL', 'https://www.themealdb.com/api/json/v1/1')

# Streamlit configuration
STREAMLIT_CONFIG = {
    'page_title': 'Recipe Recommendation System',
    'page_icon': '🍳',
    'layout': 'wide'
}
