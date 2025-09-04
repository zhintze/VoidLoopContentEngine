from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime

from models.theme import ThemeData, ThemePreferences, CategoryKeywords, SeasonalKeywords
from models.trend import TrendCategory


class ThemeLoader:
    """Service for loading and managing content themes"""
    
    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.themes_cache: Dict[str, ThemeData] = {}
        self._load_all_themes()
    
    def _load_all_themes(self):
        """Load all theme files from the themes directory"""
        if not self.themes_dir.exists():
            print(f"Warning: Themes directory {self.themes_dir} does not exist")
            return
        
        for theme_file in self.themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                    theme = ThemeData(**theme_data)
                    self.themes_cache[theme.theme_id] = theme
                    print(f"✓ Loaded theme: {theme.name}")
            except Exception as e:
                print(f"Error loading theme {theme_file}: {e}")
    
    def get_theme(self, theme_id: str) -> Optional[ThemeData]:
        """Get a specific theme by ID"""
        return self.themes_cache.get(theme_id)
    
    def list_available_themes(self) -> List[Dict[str, str]]:
        """List all available themes with basic info"""
        return [
            {
                "theme_id": theme.theme_id,
                "name": theme.name,
                "description": theme.description,
                "type": theme.theme_type.value,
                "version": theme.version
            }
            for theme in self.themes_cache.values()
        ]
    
    def get_keywords_for_category(self, theme_id: str, category_name: str, 
                                platform: str = None) -> List[str]:
        """Get keywords for a specific category from a theme"""
        theme = self.get_theme(theme_id)
        if not theme:
            return []
        
        # Find the category
        category = None
        for cat in theme.categories:
            if cat.category_name == category_name:
                category = cat
                break
        
        if not category:
            return []
        
        # Combine primary and secondary keywords
        keywords = category.primary_keywords + category.secondary_keywords
        
        # Add platform-specific keywords if requested
        if platform and platform in category.platform_specific:
            platform_data = category.platform_specific[platform]
            keywords.extend(platform_data.keywords)
        
        return keywords
    
    def get_seasonal_keywords(self, theme_id: str, month: Optional[int] = None) -> List[str]:
        """Get seasonal keywords for current month or specified month"""
        theme = self.get_theme(theme_id)
        if not theme:
            return []
        
        if month is None:
            month = datetime.now().month
        
        seasonal_keywords = []
        for seasonal in theme.seasonal_keywords:
            if month in seasonal.months:
                seasonal_keywords.extend(seasonal.keywords)
        
        return seasonal_keywords
    
    def get_platform_hashtags(self, theme_id: str, platform: str, 
                            categories: List[str] = None) -> List[str]:
        """Get platform-specific hashtags"""
        theme = self.get_theme(theme_id)
        if not theme:
            return []
        
        hashtags = []
        
        # Get hashtags from categories
        if categories:
            for cat in theme.categories:
                if cat.category_name in categories and platform in cat.platform_specific:
                    hashtags.extend(cat.platform_specific[platform].hashtags)
        else:
            # Get hashtags from all categories
            for cat in theme.categories:
                if platform in cat.platform_specific:
                    hashtags.extend(cat.platform_specific[platform].hashtags)
        
        # Get seasonal hashtags
        month = datetime.now().month
        for seasonal in theme.seasonal_keywords:
            if month in seasonal.months:
                hashtags.extend(seasonal.hashtags)
        
        # Remove duplicates while preserving order
        unique_hashtags = []
        seen = set()
        for tag in hashtags:
            if tag not in seen:
                unique_hashtags.append(tag)
                seen.add(tag)
        
        return unique_hashtags
    
    def get_content_tone_keywords(self, theme_id: str, tone_name: str) -> Dict[str, List[str]]:
        """Get keywords for a specific content tone"""
        theme = self.get_theme(theme_id)
        if not theme:
            return {}
        
        for tone in theme.content_tones:
            if tone.name == tone_name:
                return {
                    "keywords": tone.keywords,
                    "avoid_terms": tone.avoid_terms,
                    "example_phrases": tone.example_phrases
                }
        
        return {}
    
    def get_ingredient_info(self, theme_id: str, ingredient: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an ingredient"""
        theme = self.get_theme(theme_id)
        if not theme:
            return None
        
        ingredient_lower = ingredient.lower()
        for ing in theme.ingredients:
            if (ing.ingredient.lower() == ingredient_lower or 
                ingredient_lower in [s.lower() for s in ing.synonyms]):
                return {
                    "ingredient": ing.ingredient,
                    "synonyms": ing.synonyms,
                    "related_ingredients": ing.related_ingredients,
                    "cooking_methods": ing.cooking_methods,
                    "cuisine_types": ing.cuisine_types,
                    "dietary_tags": ing.dietary_tags
                }
        
        return None
    
    def get_dietary_restriction_keywords(self, theme_id: str, 
                                       restriction: str) -> Dict[str, List[str]]:
        """Get keywords for a specific dietary restriction"""
        theme = self.get_theme(theme_id)
        if not theme:
            return {}
        
        restriction_lower = restriction.lower().replace(' ', '_')
        for dietary in theme.dietary_restrictions:
            if dietary.restriction_type.lower() == restriction_lower:
                return {
                    "primary_keywords": dietary.primary_keywords,
                    "substitute_terms": dietary.substitute_terms,
                    "forbidden_terms": dietary.forbidden_terms,
                    "alternative_ingredients": dietary.alternative_ingredients
                }
        
        return {}
    
    def get_platform_optimization(self, theme_id: str, platform: str) -> Dict[str, Any]:
        """Get platform-specific optimization data"""
        theme = self.get_theme(theme_id)
        if not theme or platform not in theme.platform_optimization:
            return {}
        
        return theme.platform_optimization[platform]
    
    def get_trend_keywords(self, theme_id: str) -> List[str]:
        """Get keywords for trend detection"""
        theme = self.get_theme(theme_id)
        if not theme:
            return []
        
        return theme.trend_keywords
    
    def get_viral_indicators(self, theme_id: str) -> List[str]:
        """Get viral indicator terms"""
        theme = self.get_theme(theme_id)
        if not theme:
            return []
        
        return theme.viral_indicators
    
    def get_content_templates(self, theme_id: str) -> Dict[str, str]:
        """Get content templates"""
        theme = self.get_theme(theme_id)
        if not theme:
            return {}
        
        return theme.content_templates
    
    def get_engagement_elements(self, theme_id: str) -> Dict[str, List[str]]:
        """Get call-to-actions and engagement phrases"""
        theme = self.get_theme(theme_id)
        if not theme:
            return {}
        
        return {
            "call_to_actions": theme.call_to_actions,
            "engagement_phrases": theme.engagement_phrases
        }
    
    def apply_theme_preferences(self, theme_id: str, preferences: ThemePreferences) -> Dict[str, Any]:
        """Apply user preferences to theme data and return filtered/customized content"""
        theme = self.get_theme(theme_id)
        if not theme:
            return {}
        
        result = {
            "keywords": [],
            "hashtags": [],
            "categories": [],
            "tones": [],
            "content_elements": {}
        }
        
        # Filter categories based on preferences
        if preferences.primary_categories:
            selected_categories = [
                cat for cat in theme.categories 
                if cat.category_name in preferences.primary_categories
            ]
        else:
            selected_categories = [
                cat for cat in theme.categories 
                if cat.category_name not in preferences.excluded_categories
            ]
        
        # Collect keywords from selected categories
        for category in selected_categories:
            result["keywords"].extend(category.primary_keywords)
            result["keywords"].extend(category.secondary_keywords)
            result["categories"].append(category.category_name)
        
        # Add seasonal keywords if enabled
        if preferences.seasonal_adjustment:
            seasonal_keywords = self.get_seasonal_keywords(theme_id)
            result["keywords"].extend(seasonal_keywords)
        
        # Filter content tones
        if preferences.preferred_tones:
            result["tones"] = [
                tone.name for tone in theme.content_tones 
                if tone.name in preferences.preferred_tones
            ]
        else:
            result["tones"] = [tone.name for tone in theme.content_tones]
        
        # Add dietary focus keywords
        if preferences.dietary_focus:
            for dietary_type in preferences.dietary_focus:
                dietary_keywords = self.get_dietary_restriction_keywords(theme_id, dietary_type)
                result["keywords"].extend(dietary_keywords.get("primary_keywords", []))
        
        # Get content elements
        result["content_elements"] = self.get_engagement_elements(theme_id)
        
        # Remove duplicates
        result["keywords"] = list(set(result["keywords"]))
        result["hashtags"] = list(set(result["hashtags"]))
        
        return result
    
    def search_themes_by_keyword(self, keyword: str) -> List[str]:
        """Find themes that contain a specific keyword"""
        matching_themes = []
        keyword_lower = keyword.lower()
        
        for theme_id, theme in self.themes_cache.items():
            # Search in categories
            for category in theme.categories:
                all_keywords = (category.primary_keywords + 
                              category.secondary_keywords + 
                              category.related_terms)
                if any(keyword_lower in kw.lower() for kw in all_keywords):
                    matching_themes.append(theme_id)
                    break
        
        return matching_themes
    
    def reload_themes(self):
        """Reload all themes from disk"""
        self.themes_cache.clear()
        self._load_all_themes()


# Global theme loader instance
theme_loader = ThemeLoader()