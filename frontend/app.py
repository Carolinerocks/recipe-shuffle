#!/usr/bin/env python3
"""
Recipe Recommendation System - Modern Frontend
"""

import streamlit as st
import requests
from PIL import Image
import io
from typing import List
import logging
import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core.config import STREAMLIT_CONFIG
from backend.core.models import db_manager, Recipe
from backend.services.data_service import data_service
from backend.services.recommendation_service import recommendation_engine

# Set page configuration
st.set_page_config(
    page_title="🍳 Recipe Finder",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Set page background to purple gradient */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Override Streamlit's default background */
    .stApp {
        background-color: white;
    }
    
    .main-header {
        background: transparent;
        padding: 2rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .recipe-card {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
        overflow: hidden;
    }
    
    .recipe-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    .recipe-image {
        width: 100%;
        height: 200px;
        overflow: hidden;
    }
    
    .recipe-content {
        padding: 1.5rem;
    }
    
    .recipe-title {
        color: #2c3e50;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .recipe-meta {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .ingredient-tag {
        background: #ecf0f1;
        color: #2c3e50;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .search-container {
        background: transparent;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        background: #000000;
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Make the card container relative for absolute positioning */
    .recipe-card {
        position: relative;
    }
    
    .welcome-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid #dee2e6;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .stat-label {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def load_image_from_url(url: str) -> Image.Image:
    """Load image from URL with better error handling"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except Exception as e:
        logger.error(f"Failed to load image: {e}")
        return None

def display_modern_recipe_card(recipe: Recipe, col):
    """Display simplified recipe card for homepage"""
    with col:
        # Create a clickable area using st.columns
        click_col = st.columns(1)[0]
        
        with click_col:
            # Complete card with image using HTML
            image_url = recipe.image_url if recipe.image_url and recipe.image_url.strip() else "https://via.placeholder.com/300x200?text=🍽️"
            
            st.markdown(f"""
            <div class="recipe-card" style="cursor: pointer;">
                <div class="recipe-image">
                    <img src="{image_url}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 10px 10px 0 0;" onerror="this.src='https://via.placeholder.com/300x200?text=🍽️'">
                </div>
                <div class="recipe-content">
                    <div class="recipe-title">{recipe.name}</div>
                    <div class="recipe-meta">
                        {f"🍽️ {recipe.category}" if recipe.category else ""} 
                        {f"🌍 {recipe.area}" if recipe.area else ""}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a clickable button
            if st.button("View Details", key=f"card_{recipe.id}"):
                st.session_state.selected_recipe_id = recipe.id
                st.rerun()

def display_recipe_detail(recipe: Recipe):
    """Display detailed recipe information on a separate page"""
    # Add anchor point and force scroll to top
    st.markdown('<div id="recipe-detail-top"></div>', unsafe_allow_html=True)
    
    # Add JavaScript to scroll to the anchor point
    st.markdown("""
    <script>
    setTimeout(function() {
        const element = document.getElementById('recipe-detail-top');
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        window.scrollTo(0, 0);
    }, 50);
    </script>
    """, unsafe_allow_html=True)
    
    # Add a clear page title
    st.markdown("# Recipe Details")
    st.markdown("---")
    
    # Back button using Streamlit
    if st.button("← Back to Search", key="back_to_search"):
        st.session_state.selected_recipe_id = None
        # Keep search state to return to search results
        st.rerun()
    
    # Recipe header
    col1, col2 = st.columns([1, 2])
    
    with col1:
        image_url = recipe.image_url if recipe.image_url and recipe.image_url.strip() else "https://via.placeholder.com/400x300?text=🍽️"
        st.image(image_url, width=400)
    
    with col2:
        st.markdown(f"# {recipe.name}")
        st.markdown(f"**🍽️ Category:** {recipe.category if recipe.category else 'N/A'}")
        st.markdown(f"**🌍 Cuisine:** {recipe.area if recipe.area else 'N/A'}")
        
        if recipe.youtube_url and recipe.youtube_url.strip():
            st.markdown(f"**🎥 Video Tutorial:** [Watch on YouTube]({recipe.youtube_url})")
    
    st.markdown("---")
    
    # Ingredients and Instructions in two columns (1:2 ratio)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Ingredients section
        st.markdown("## 🥘 Ingredients")
        if recipe.ingredients:
            ingredients_text = []
            for i, (ingredient, measure) in enumerate(zip(recipe.ingredients, recipe.measures)):
                if ingredient:
                    if measure:
                        ingredients_text.append(f"• {ingredient}: {measure}")
                    else:
                        ingredients_text.append(f"• {ingredient}")
            
            for text in ingredients_text:
                st.markdown(text)
        else:
            st.markdown("No ingredients information available")
    
    with col2:
        # Instructions section
        st.markdown("## 📝 Instructions")
        if recipe.instructions:
            steps = recipe.instructions.split('\r\n')
            for i, step in enumerate(steps, 1):
                if step.strip():
                    st.markdown(f"**Step {i}:** {step.strip()}")
        else:
            st.markdown("No detailed instructions available")

def render_recipe_count():
    """Render recipe count below main header"""
    try:
        recipe_count = data_service.get_recipe_count()
        st.markdown(f"<p style='text-align: center; color: #7f8c8d; margin-top: -1rem;'>{recipe_count} recipes available</p>", unsafe_allow_html=True)
    except:
        pass


def render_search_section():
    """Render modern search section"""
    st.markdown("""
    <div class="search-container">
        <h3>🔍 Find Your Perfect Recipe</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Get saved search state
    saved_query = st.session_state.get('saved_search_query', '')
    saved_type = st.session_state.get('saved_search_type', 'All')
    saved_num_results = st.session_state.get('saved_num_results', 6)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search for recipes...", 
            value=saved_query,
            placeholder="e.g., chicken pasta, dessert, Italian...",
            key="search_input"
        )
    
    with col2:
        search_type = st.selectbox(
            "Search by",
            ["All", "Name", "Ingredient", "Category", "Area"],
            index=["All", "Name", "Ingredient", "Category", "Area"].index(saved_type) if saved_type in ["All", "Name", "Ingredient", "Category", "Area"] else 0,
            key="search_type"
        )
    
    with col3:
        num_results = st.slider("Results", 3, 12, saved_num_results, key="num_results")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        search_clicked = st.button("🔍 Search", type="primary", key="search_btn")
    with col2:
        st.empty()  # Empty space for better layout
    
    return search_query, search_type, num_results, search_clicked

def main():
    """Main application function"""
    # Initialize app
    try:
        db_manager.create_tables()
        logger.info("Database initialization completed")
        
        recipe_count = data_service.get_recipe_count()
        if recipe_count == 0:
            st.error("⚠️ No recipe data found in database!")
            st.info("Please run the data sync script first: `python scripts/sync/quick_sync.py`")
            st.stop()
        else:
            logger.info(f"Database contains {recipe_count} recipes")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        st.error("Database initialization failed, please check database connection configuration")
        st.stop()
    
    # Check if we're viewing a specific recipe detail
    selected_recipe_id = st.session_state.get('selected_recipe_id')
    if selected_recipe_id:
        try:
            recipe = data_service.get_recipe_by_id(selected_recipe_id)
            if recipe:
                display_recipe_detail(recipe)
                return
            else:
                st.error("Recipe not found")
                st.session_state.selected_recipe_id = None
                st.rerun()
        except Exception as e:
            st.error(f"Error loading recipe: {e}")
            st.session_state.selected_recipe_id = None
            st.rerun()
    
    # Store search state to maintain it after returning from detail view
    search_query = st.session_state.get('saved_search_query', '')
    search_type = st.session_state.get('saved_search_type', 'all')
    num_results = st.session_state.get('saved_num_results', 6)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🍳 Recipe Finder</h1>
        <p>Discover amazing recipes from around the world</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recipe count below header
    render_recipe_count()
    
    # Search section
    search_query, search_type, num_results, search_clicked = render_search_section()
    
    # Main content area
    if search_clicked and search_query.strip():
        # Save search state to session with different variable names
        st.session_state.saved_search_query = search_query
        st.session_state.saved_search_type = search_type
        st.session_state.saved_num_results = num_results
        
        # Search
        st.markdown(f"### 🔍 Search Results for '{search_query}'")
        
        # Map search types
        search_type_map = {
            "All": "all",
            "Name": "name", 
            "Ingredient": "ingredient",
            "Category": "category",
            "Area": "area"
        }
        
        with st.spinner("Searching recipes..."):
            try:
                recipes = recommendation_engine.search_and_recommend(
                    search_query, 
                    search_type_map[search_type], 
                    num_results
                )
                
                if recipes:
                    cols = st.columns(3)
                    for i, recipe in enumerate(recipes):
                        display_modern_recipe_card(recipe, cols[i % 3])
                else:
                    st.warning("No related recipes found, please try other keywords")
                    
            except Exception as e:
                st.error(f"Search failed: {e}")
    
    elif st.session_state.get('saved_search_query'):
        # Show previous search results
        search_query = st.session_state.saved_search_query
        search_type = st.session_state.saved_search_type
        num_results = st.session_state.saved_num_results
        
        st.markdown(f"### 🔍 Search Results for '{search_query}'")
        
        # Map search types
        search_type_map = {
            "All": "all",
            "Name": "name", 
            "Ingredient": "ingredient",
            "Category": "category",
            "Area": "area"
        }
        
        with st.spinner("Loading search results..."):
            try:
                recipes = recommendation_engine.search_and_recommend(
                    search_query, 
                    search_type_map[search_type], 
                    num_results
                )
                
                if recipes:
                    cols = st.columns(3)
                    for i, recipe in enumerate(recipes):
                        display_modern_recipe_card(recipe, cols[i % 3])
                else:
                    st.warning("No related recipes found, please try other keywords")
                    
            except Exception as e:
                st.error(f"Search failed: {e}")
    
    else:
        # Default view - show featured recipes
        st.markdown("### 🌟 Featured Recipes")
        try:
            with st.spinner("Loading featured recipes..."):
                sample_recipes = data_service.get_random_recipes(6)
                if sample_recipes:
                    cols = st.columns(3)
                    for i, recipe in enumerate(sample_recipes):
                        display_modern_recipe_card(recipe, cols[i % 3])
                else:
                    st.info("No recipe data available, please run the data sync script first")
        except Exception as e:
            st.error(f"Failed to load sample recipes: {e}")

if __name__ == "__main__":
    main()