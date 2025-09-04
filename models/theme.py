from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class ThemeType(str, Enum):
    """Types of content themes"""
    FOOD_RECIPE = "food_recipe"
    LIFESTYLE = "lifestyle" 
    TECH = "tech"
    FITNESS = "fitness"
    TRAVEL = "travel"
    FASHION = "fashion"


class PlatformKeywords(BaseModel):
    """Platform-specific keywords and hashtags"""
    keywords: List[str] = Field(default_factory=list, description="General keywords for the platform")
    hashtags: List[str] = Field(default_factory=list, description="Platform-specific hashtags")
    trending_terms: List[str] = Field(default_factory=list, description="Currently trending terms")
    evergreen_terms: List[str] = Field(default_factory=list, description="Always relevant terms")


class CategoryKeywords(BaseModel):
    """Keywords organized by content category"""
    category_name: str
    primary_keywords: List[str] = Field(default_factory=list)
    secondary_keywords: List[str] = Field(default_factory=list)
    related_terms: List[str] = Field(default_factory=list)
    platform_specific: Dict[str, PlatformKeywords] = Field(default_factory=dict)


class SeasonalKeywords(BaseModel):
    """Seasonal keyword sets"""
    season: str  # spring, summer, fall, winter
    months: List[int] = Field(description="Months this applies to (1-12)")
    keywords: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    trending_boost: float = Field(default=1.0, description="Multiplier for seasonal relevance")


class ContentTone(BaseModel):
    """Content tone and voice guidelines"""
    name: str
    description: str
    keywords: List[str] = Field(default_factory=list, description="Words that convey this tone")
    avoid_terms: List[str] = Field(default_factory=list, description="Terms to avoid for this tone")
    example_phrases: List[str] = Field(default_factory=list)


class IngredientKeywords(BaseModel):
    """Ingredient-specific keywords (for food themes)"""
    ingredient: str
    synonyms: List[str] = Field(default_factory=list)
    related_ingredients: List[str] = Field(default_factory=list)
    cooking_methods: List[str] = Field(default_factory=list)
    cuisine_types: List[str] = Field(default_factory=list)
    dietary_tags: List[str] = Field(default_factory=list)  # vegan, keto, etc.


class CookingTechniqueKeywords(BaseModel):
    """Cooking technique-specific keywords"""
    technique: str
    related_terms: List[str] = Field(default_factory=list)
    equipment_needed: List[str] = Field(default_factory=list)
    suitable_ingredients: List[str] = Field(default_factory=list)
    difficulty_level: str = Field(default="medium")  # easy, medium, hard
    time_indicators: List[str] = Field(default_factory=list)  # "quick", "slow", "overnight"


class DietaryRestrictionKeywords(BaseModel):
    """Keywords for specific dietary needs"""
    restriction_type: str  # vegan, keto, gluten-free, etc.
    primary_keywords: List[str] = Field(default_factory=list)
    substitute_terms: List[str] = Field(default_factory=list)
    forbidden_terms: List[str] = Field(default_factory=list)
    alternative_ingredients: List[str] = Field(default_factory=list)


class ThemeData(BaseModel):
    """Complete theme data structure"""
    theme_id: str
    theme_type: ThemeType
    name: str
    description: str
    version: str = Field(default="1.0")
    
    # Core keyword categories
    categories: List[CategoryKeywords] = Field(default_factory=list)
    seasonal_keywords: List[SeasonalKeywords] = Field(default_factory=list)
    content_tones: List[ContentTone] = Field(default_factory=list)
    
    # Food/recipe specific (optional)
    ingredients: List[IngredientKeywords] = Field(default_factory=list)
    cooking_techniques: List[CookingTechniqueKeywords] = Field(default_factory=list)
    dietary_restrictions: List[DietaryRestrictionKeywords] = Field(default_factory=list)
    
    # Platform optimization
    platform_optimization: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Trend integration
    trend_keywords: List[str] = Field(default_factory=list, description="Keywords for trend detection")
    viral_indicators: List[str] = Field(default_factory=list, description="Terms that indicate viral potential")
    
    # Content generation hints
    content_templates: Dict[str, str] = Field(default_factory=dict)
    call_to_actions: List[str] = Field(default_factory=list)
    engagement_phrases: List[str] = Field(default_factory=list)


class ThemePreferences(BaseModel):
    """User preferences for theme application"""
    primary_categories: List[str] = Field(default_factory=list)
    excluded_categories: List[str] = Field(default_factory=list)
    preferred_tones: List[str] = Field(default_factory=list)
    dietary_focus: List[str] = Field(default_factory=list)  # For food themes
    platform_priorities: Dict[str, float] = Field(default_factory=dict)  # platform -> weight
    seasonal_adjustment: bool = Field(default=True)
    trend_sensitivity: float = Field(default=0.7, ge=0.0, le=1.0)