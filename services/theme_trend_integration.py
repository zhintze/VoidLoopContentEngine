from typing import List, Dict, Optional, Set
from datetime import datetime

from services.theme_loader import theme_loader
from models.theme import ThemeData
from models.trend import TrendKeyword, TrendCategory


class ThemeTrendIntegrator:
    """Service for integrating theme system with trend scraping"""
    
    def __init__(self):
        self.theme_cache = {}
    
    def get_food_related_keywords(self, theme_id: str) -> List[str]:
        """Get comprehensive list of food-related keywords from theme"""
        theme = theme_loader.get_theme(theme_id)
        if not theme:
            return []
        
        keywords = []
        
        # Get keywords from all categories
        for category in theme.categories:
            keywords.extend(category.primary_keywords)
            keywords.extend(category.secondary_keywords)
            keywords.extend(category.related_terms)
        
        # Add ingredient names
        for ingredient in theme.ingredients:
            keywords.append(ingredient.ingredient)
            keywords.extend(ingredient.synonyms)
            keywords.extend(ingredient.related_ingredients)
        
        # Add cooking techniques
        for technique in theme.cooking_techniques:
            keywords.append(technique.technique)
            keywords.extend(technique.related_terms)
        
        # Add dietary restriction terms
        for dietary in theme.dietary_restrictions:
            keywords.extend(dietary.primary_keywords)
            keywords.extend(dietary.substitute_terms)
            keywords.extend(dietary.alternative_ingredients)
        
        # Add trend keywords
        keywords.extend(theme.trend_keywords)
        
        # Remove duplicates and normalize
        unique_keywords = list(set(keyword.lower() for keyword in keywords if keyword))
        
        return unique_keywords
    
    def get_platform_specific_hashtags(self, theme_id: str, platform: str) -> List[str]:
        """Get platform-specific hashtags from theme"""
        return theme_loader.get_platform_hashtags(theme_id, platform)
    
    def get_viral_indicators(self, theme_id: str) -> List[str]:
        """Get viral indicator terms from theme"""
        return theme_loader.get_viral_indicators(theme_id)
    
    def categorize_keyword_from_theme(self, keyword: str, theme_id: str) -> TrendCategory:
        """Categorize a keyword using theme data"""
        theme = theme_loader.get_theme(theme_id)
        if not theme:
            return TrendCategory.VIRAL_RECIPES
        
        keyword_lower = keyword.lower()
        
        # Map theme categories to TrendCategory
        category_mapping = {
            "comfort_food": TrendCategory.COMFORT_FOOD,
            "classic_comfort": TrendCategory.COMFORT_FOOD,
            "cozy_baking": TrendCategory.DESSERTS,
            "slow_cooked": TrendCategory.COMFORT_FOOD,
            "childhood_favorites": TrendCategory.COMFORT_FOOD,
            
            "clean_eating": TrendCategory.HEALTHY_EATING,
            "superfoods": TrendCategory.HEALTHY_EATING,
            "meal_prep": TrendCategory.QUICK_MEALS,
            "plant_based": TrendCategory.HEALTHY_EATING,
            
            "healthy_eating": TrendCategory.HEALTHY_EATING,
            "quick_meals": TrendCategory.QUICK_MEALS,
            "desserts": TrendCategory.DESSERTS
        }
        
        # Check each category in theme
        for category in theme.categories:
            category_name = category.category_name
            
            # Check if keyword matches any terms in this category
            all_terms = (category.primary_keywords + 
                        category.secondary_keywords + 
                        category.related_terms)
            
            if any(term.lower() in keyword_lower or keyword_lower in term.lower() 
                   for term in all_terms):
                return category_mapping.get(category_name, TrendCategory.VIRAL_RECIPES)
        
        # Check ingredients
        for ingredient in theme.ingredients:
            if (ingredient.ingredient.lower() in keyword_lower or
                any(syn.lower() in keyword_lower for syn in ingredient.synonyms)):
                return TrendCategory.INGREDIENTS
        
        # Check cooking techniques
        for technique in theme.cooking_techniques:
            if technique.technique.lower() in keyword_lower:
                return TrendCategory.COOKING_TECHNIQUES
        
        # Check dietary restrictions
        for dietary in theme.dietary_restrictions:
            if any(term.lower() in keyword_lower for term in dietary.primary_keywords):
                return TrendCategory.DIETARY_RESTRICTIONS
        
        # Default category
        return TrendCategory.VIRAL_RECIPES
    
    def is_food_related_by_theme(self, text: str, theme_id: str = "food_recipe_general") -> bool:
        """Check if text is food-related using theme keywords"""
        if not text:
            return False
        
        text_lower = text.lower()
        food_keywords = self.get_food_related_keywords(theme_id)
        
        # Check if any food-related keywords appear in the text
        return any(keyword in text_lower for keyword in food_keywords[:100])  # Use top 100 for performance
    
    def extract_food_keywords_from_text(self, text: str, theme_id: str = "food_recipe_general") -> List[str]:
        """Extract food-related keywords from text using theme"""
        if not text:
            return []
        
        text_lower = text.lower()
        food_keywords = self.get_food_related_keywords(theme_id)
        
        found_keywords = []
        for keyword in food_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def get_seasonal_keywords(self, theme_id: str, month: Optional[int] = None) -> List[str]:
        """Get seasonal keywords from theme"""
        return theme_loader.get_seasonal_keywords(theme_id, month)
    
    def get_category_keywords_for_platform(self, theme_id: str, category_name: str, 
                                         platform: str) -> List[str]:
        """Get category keywords optimized for specific platform"""
        return theme_loader.get_keywords_for_category(theme_id, category_name, platform)
    
    def enhance_trend_keywords_with_theme(self, base_keywords: List[str], 
                                        theme_id: str, platform: str = None) -> List[str]:
        """Enhance a list of keywords with theme-specific terms"""
        enhanced = base_keywords.copy()
        
        # Add seasonal keywords
        seasonal = self.get_seasonal_keywords(theme_id)
        enhanced.extend(seasonal)
        
        # Add platform-specific viral indicators
        if platform:
            platform_data = theme_loader.get_platform_optimization(theme_id, platform)
            viral_terms = platform_data.get('viral_indicators', [])
            enhanced.extend(viral_terms)
        
        # Add general viral indicators
        viral_indicators = self.get_viral_indicators(theme_id)
        enhanced.extend(viral_indicators)
        
        # Remove duplicates
        return list(set(enhanced))
    
    def get_content_suggestions_from_theme(self, keyword: str, theme_id: str) -> List[str]:
        """Get content suggestions based on keyword and theme"""
        theme = theme_loader.get_theme(theme_id)
        if not theme:
            return []
        
        suggestions = []
        
        # Get templates and apply to keyword
        templates = theme.content_templates
        for template_name, template in templates.items():
            try:
                # Simple template substitution
                if '{dish}' in template:
                    suggestion = template.replace('{dish}', keyword)
                    suggestions.append(suggestion)
                elif '{ingredient}' in template:
                    suggestion = template.replace('{ingredient}', keyword)
                    suggestions.append(suggestion)
            except:
                continue
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def get_trending_combinations(self, theme_id: str, platform: str) -> List[str]:
        """Get trending keyword combinations for a platform"""
        theme = theme_loader.get_theme(theme_id)
        if not theme:
            return []
        
        combinations = []
        
        # Get platform optimization data
        platform_data = theme.platform_optimization.get(platform, {})
        
        # Combine viral indicators with food categories
        viral_terms = platform_data.get('viral_indicators', [])
        
        for category in theme.categories[:3]:  # Top 3 categories
            for viral_term in viral_terms[:2]:  # Top 2 viral terms
                for keyword in category.primary_keywords[:2]:  # Top 2 keywords
                    combination = f"{viral_term} {keyword}"
                    combinations.append(combination)
        
        return combinations
    
    def get_theme_based_seed_keywords(self, theme_id: str) -> List[str]:
        """Get seed keywords for trend scraping based on theme"""
        theme = theme_loader.get_theme(theme_id)
        if not theme:
            return []
        
        seed_keywords = []
        
        # Get primary keywords from each category
        for category in theme.categories:
            seed_keywords.extend(category.primary_keywords[:3])  # Top 3 from each category
        
        # Add seasonal keywords for current month
        seasonal = self.get_seasonal_keywords(theme_id)
        seed_keywords.extend(seasonal[:5])  # Top 5 seasonal
        
        # Add ingredient-focused keywords
        for ingredient in theme.ingredients[:5]:  # Top 5 ingredients
            seed_keywords.append(f"{ingredient.ingredient} recipe")
            seed_keywords.append(f"how to cook {ingredient.ingredient}")
        
        # Add technique-focused keywords
        for technique in theme.cooking_techniques[:3]:  # Top 3 techniques
            seed_keywords.append(f"{technique.technique} recipe")
        
        return seed_keywords[:30]  # Limit to 30 seed keywords


# Global integrator instance
theme_trend_integrator = ThemeTrendIntegrator()