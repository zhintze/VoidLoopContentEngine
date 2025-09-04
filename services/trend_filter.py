from typing import List, Dict, Set, Optional
import re
from datetime import datetime
from models.trend import TrendKeyword, TrendCategory, TrendSource


class RecipeTrendFilter:
    """Advanced filtering system for recipe and food-related trends"""
    
    def __init__(self):
        # Food/recipe related keywords for enhanced filtering
        self.food_keywords = {
            'cooking_terms': {
                'recipe', 'recipes', 'cooking', 'baking', 'grilling', 'roasting', 'frying',
                'sautéing', 'steaming', 'braising', 'simmering', 'boiling', 'poaching',
                'marinating', 'seasoning', 'preparation', 'prep', 'meal prep'
            },
            'meal_types': {
                'breakfast', 'brunch', 'lunch', 'dinner', 'snack', 'snacks', 'appetizer',
                'appetizers', 'main course', 'side dish', 'dessert', 'desserts'
            },
            'diet_types': {
                'keto', 'paleo', 'vegan', 'vegetarian', 'gluten free', 'dairy free',
                'sugar free', 'low carb', 'low fat', 'mediterranean', 'whole30',
                'plant based', 'organic', 'raw', 'detox', 'healthy'
            },
            'cooking_methods': {
                'air fryer', 'instant pot', 'slow cooker', 'pressure cooker', 'microwave',
                'oven baked', 'grilled', 'pan fried', 'deep fried', 'steamed', 'roasted',
                'broiled', 'braised', 'stewed', 'one pot', 'sheet pan', 'no bake'
            },
            'ingredients': {
                'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp', 'pasta',
                'rice', 'quinoa', 'vegetables', 'broccoli', 'spinach', 'tomatoes',
                'avocado', 'cheese', 'chocolate', 'vanilla', 'garlic', 'onion', 'herbs',
                'spices', 'flour', 'sugar', 'eggs', 'milk', 'butter', 'oil', 'beans'
            },
            'cuisines': {
                'italian', 'chinese', 'mexican', 'indian', 'thai', 'japanese', 'french',
                'mediterranean', 'american', 'southern', 'tex mex', 'korean', 'greek',
                'middle eastern', 'latin', 'caribbean', 'asian', 'european'
            },
            'food_types': {
                'soup', 'salad', 'sandwich', 'pizza', 'burger', 'tacos', 'pasta',
                'noodles', 'stir fry', 'curry', 'casserole', 'smoothie', 'juice',
                'cocktail', 'bread', 'cake', 'cookies', 'pie', 'muffins', 'pancakes'
            }
        }
        
        # Non-food keywords to exclude
        self.exclude_keywords = {
            'non_food': {
                'exercise', 'workout', 'fitness', 'gym', 'sports', 'politics', 'news',
                'celebrity', 'fashion', 'beauty', 'technology', 'software', 'app',
                'game', 'movie', 'music', 'book', 'travel', 'hotel', 'car', 'phone'
            },
            'inappropriate': {
                'alcohol', 'alcoholic', 'wine', 'beer', 'vodka', 'whiskey', 'cocktails',
                'drugs', 'smoking', 'tobacco', 'gambling', 'adult', 'explicit'
            }
        }
        
        # Quality indicators for trend scoring
        self.quality_indicators = {
            'high_quality': {
                'homemade', 'fresh', 'natural', 'authentic', 'traditional', 'artisan',
                'gourmet', 'premium', 'organic', 'farm to table', 'seasonal', 'local'
            },
            'trending_formats': {
                'viral', 'trending', 'popular', 'famous', 'tiktok', 'instagram',
                'easy', 'quick', 'simple', '15 minute', '30 minute', 'one pot'
            }
        }
    
    def filter_food_trends(self, trends: List[TrendKeyword], 
                          min_relevance_score: float = 0.3) -> List[TrendKeyword]:
        """Filter trends to only include food/recipe related content
        
        Args:
            trends: List of trend keywords to filter
            min_relevance_score: Minimum relevance score (0-1) to include
            
        Returns:
            Filtered list of food-related trends
        """
        filtered_trends = []
        
        for trend in trends:
            relevance = self._calculate_food_relevance(trend.keyword)
            
            if relevance >= min_relevance_score:
                # Update the trend with relevance-adjusted score
                trend.score.current_score *= (0.5 + relevance * 0.5)  # Boost by relevance
                trend.score.peak_score *= (0.5 + relevance * 0.5)
                
                # Add quality metadata (store as custom attributes)
                quality_score = self._calculate_quality_score(trend.keyword)
                # Store as custom attributes instead of metadata dict
                trend.food_relevance = relevance
                trend.quality_score = quality_score
                trend.enhanced_score = trend.score.current_score
                
                filtered_trends.append(trend)
        
        return filtered_trends
    
    def categorize_food_trends(self, trends: List[TrendKeyword]) -> Dict[TrendCategory, List[TrendKeyword]]:
        """Categorize food trends into specific categories"""
        categorized = {category: [] for category in TrendCategory}
        
        for trend in trends:
            # Get the best category for this trend
            category = self._determine_best_category(trend.keyword)
            trend.category = category  # Update the trend's category
            categorized[category].append(trend)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def filter_by_dietary_restrictions(self, trends: List[TrendKeyword],
                                     dietary_preferences: List[str]) -> List[TrendKeyword]:
        """Filter trends based on dietary restrictions/preferences
        
        Args:
            trends: List of trends to filter
            dietary_preferences: List of dietary preferences ('vegan', 'keto', etc.)
        """
        if not dietary_preferences:
            return trends
        
        filtered = []
        dietary_prefs_lower = [pref.lower() for pref in dietary_preferences]
        
        for trend in trends:
            keyword_lower = trend.keyword.lower()
            
            # Check if trend matches any dietary preference
            if any(pref in keyword_lower for pref in dietary_prefs_lower):
                filtered.append(trend)
            # Or check if it's diet-neutral (doesn't conflict)
            elif not self._conflicts_with_diet(keyword_lower, dietary_prefs_lower):
                filtered.append(trend)
        
        return filtered
    
    def filter_by_cooking_skill(self, trends: List[TrendKeyword],
                              skill_level: str = 'all') -> List[TrendKeyword]:
        """Filter trends based on cooking skill level
        
        Args:
            skill_level: 'beginner', 'intermediate', 'advanced', or 'all'
        """
        if skill_level == 'all':
            return trends
        
        skill_keywords = {
            'beginner': {
                'easy', 'simple', 'quick', 'no bake', 'microwave', 'instant',
                '15 minute', '30 minute', 'one pot', 'sheet pan', 'basic'
            },
            'intermediate': {
                'homemade', 'from scratch', 'traditional', 'classic', 'baked',
                'roasted', 'braised', 'marinated', 'seasoned'
            },
            'advanced': {
                'gourmet', 'artisan', 'professional', 'complex', 'technique',
                'advanced', 'chef', 'restaurant style', 'molecular', 'fusion'
            }
        }
        
        target_keywords = skill_keywords.get(skill_level, set())
        if not target_keywords:
            return trends
        
        filtered = []
        for trend in trends:
            keyword_lower = trend.keyword.lower()
            
            if skill_level == 'beginner':
                # For beginners, include if it has beginner keywords OR no skill indicators
                if (any(kw in keyword_lower for kw in target_keywords) or
                    not any(kw in keyword_lower for kws in skill_keywords.values() for kw in kws)):
                    filtered.append(trend)
            else:
                # For intermediate/advanced, must have those keywords
                if any(kw in keyword_lower for kw in target_keywords):
                    filtered.append(trend)
        
        return filtered
    
    def enhance_trend_keywords(self, trends: List[TrendKeyword]) -> List[TrendKeyword]:
        """Enhance trends with related keywords and suggestions"""
        enhanced = []
        
        for trend in trends:
            # Generate related keywords based on the main keyword
            related = self._generate_related_keywords(trend.keyword)
            
            # Add to existing related keywords
            existing_related = set(trend.related_keywords)
            new_related = existing_related.union(set(related))
            trend.related_keywords = list(new_related)
            
            # Add content suggestions as custom attribute
            suggestions = self._generate_content_suggestions(trend.keyword, trend.category)
            trend.content_suggestions = getattr(trend, 'content_suggestions', []) + suggestions
            
            enhanced.append(trend)
        
        return enhanced
    
    def _calculate_food_relevance(self, keyword: str) -> float:
        """Calculate how food-related a keyword is (0-1 score)"""
        keyword_lower = keyword.lower()
        relevance_score = 0.0
        
        # Check against food keyword categories
        for category, keywords in self.food_keywords.items():
            matches = sum(1 for kw in keywords if kw in keyword_lower)
            if matches > 0:
                # Weight different categories differently
                weights = {
                    'cooking_terms': 0.3,
                    'meal_types': 0.25,
                    'diet_types': 0.2,
                    'cooking_methods': 0.25,
                    'ingredients': 0.3,
                    'cuisines': 0.2,
                    'food_types': 0.3
                }
                relevance_score += matches * weights.get(category, 0.2)
        
        # Penalize if contains excluded keywords
        for category, keywords in self.exclude_keywords.items():
            if any(kw in keyword_lower for kw in keywords):
                relevance_score *= 0.3  # Significant penalty
        
        # Cap at 1.0
        return min(relevance_score, 1.0)
    
    def _calculate_quality_score(self, keyword: str) -> float:
        """Calculate quality score based on indicators"""
        keyword_lower = keyword.lower()
        quality_score = 0.5  # Base score
        
        # Check quality indicators
        for category, keywords in self.quality_indicators.items():
            matches = sum(1 for kw in keywords if kw in keyword_lower)
            if matches > 0:
                if category == 'high_quality':
                    quality_score += matches * 0.2
                elif category == 'trending_formats':
                    quality_score += matches * 0.15
        
        return min(quality_score, 1.0)
    
    def _determine_best_category(self, keyword: str) -> TrendCategory:
        """Determine the best category for a keyword"""
        keyword_lower = keyword.lower()
        
        # Category mapping with keywords
        category_keywords = {
            TrendCategory.COMFORT_FOOD: {
                'comfort', 'mac and cheese', 'fried chicken', 'pizza', 'burger',
                'grilled cheese', 'meatloaf', 'pot pie', 'casserole', 'hearty'
            },
            TrendCategory.HEALTHY_EATING: {
                'healthy', 'nutritious', 'superfood', 'clean eating', 'detox',
                'low calorie', 'protein', 'vitamins', 'antioxidants', 'green'
            },
            TrendCategory.QUICK_MEALS: {
                'quick', 'fast', 'easy', '15 minute', '30 minute', 'instant',
                'microwave', 'one pot', 'sheet pan', 'no prep'
            },
            TrendCategory.DESSERTS: {
                'dessert', 'sweet', 'cake', 'cookie', 'pie', 'chocolate', 'vanilla',
                'sugar', 'frosting', 'ice cream', 'candy', 'treat'
            },
            TrendCategory.INTERNATIONAL: {
                'italian', 'chinese', 'mexican', 'indian', 'thai', 'japanese',
                'french', 'korean', 'greek', 'mediterranean', 'asian'
            },
            TrendCategory.DIETARY_RESTRICTIONS: {
                'gluten free', 'dairy free', 'vegan', 'vegetarian', 'keto',
                'paleo', 'sugar free', 'low carb', 'whole30'
            },
            TrendCategory.SEASONAL: {
                'christmas', 'thanksgiving', 'halloween', 'easter', 'summer',
                'winter', 'spring', 'fall', 'holiday', 'seasonal'
            },
            TrendCategory.VIRAL_RECIPES: {
                'viral', 'trending', 'tiktok', 'instagram', 'famous', 'popular',
                'social media', 'challenge', 'trend'
            },
            TrendCategory.COOKING_TECHNIQUES: {
                'technique', 'method', 'grilling', 'roasting', 'braising',
                'sautéing', 'steaming', 'pressure cooking', 'sous vide'
            },
            TrendCategory.INGREDIENTS: {
                'ingredient', 'spice', 'herb', 'seasoning', 'sauce', 'condiment',
                'protein', 'vegetable', 'fruit', 'grain', 'dairy'
            },
            TrendCategory.BEVERAGES: {
                'drink', 'beverage', 'smoothie', 'juice', 'cocktail', 'mocktail',
                'tea', 'coffee', 'shake', 'lemonade', 'water'
            }
        }
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for kw in keywords if kw in keyword_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return the category with the highest score, or default
        if category_scores:
            return max(category_scores.keys(), key=lambda x: category_scores[x])
        else:
            return TrendCategory.VIRAL_RECIPES  # Default category
    
    def _conflicts_with_diet(self, keyword: str, dietary_prefs: List[str]) -> bool:
        """Check if keyword conflicts with dietary preferences"""
        conflicts = {
            'vegan': {'meat', 'chicken', 'beef', 'pork', 'fish', 'dairy', 'cheese', 'milk', 'butter', 'eggs'},
            'vegetarian': {'meat', 'chicken', 'beef', 'pork', 'fish', 'bacon', 'ham'},
            'gluten free': {'wheat', 'flour', 'bread', 'pasta', 'barley', 'rye'},
            'dairy free': {'cheese', 'milk', 'butter', 'cream', 'yogurt', 'dairy'},
            'keto': {'sugar', 'bread', 'pasta', 'rice', 'potatoes', 'fruit', 'sweet'},
            'sugar free': {'sugar', 'sweet', 'candy', 'dessert', 'syrup', 'honey'}
        }
        
        for pref in dietary_prefs:
            if pref in conflicts:
                conflict_keywords = conflicts[pref]
                if any(conflict in keyword for conflict in conflict_keywords):
                    return True
        
        return False
    
    def _generate_related_keywords(self, keyword: str) -> List[str]:
        """Generate related keywords for content creation"""
        keyword_lower = keyword.lower()
        related = []
        
        # Add variations with common modifiers
        modifiers = ['easy', 'quick', 'healthy', 'homemade', 'best', 'simple']
        for modifier in modifiers:
            if modifier not in keyword_lower:
                related.append(f"{modifier} {keyword}")
        
        # Add recipe variations
        if 'recipe' not in keyword_lower:
            related.append(f"{keyword} recipe")
        
        # Add how-to variations
        related.append(f"how to make {keyword}")
        
        return related[:5]  # Limit to top 5
    
    def _generate_content_suggestions(self, keyword: str, category: TrendCategory) -> List[str]:
        """Generate content creation suggestions"""
        suggestions = []
        
        # Base suggestions for all recipes
        suggestions.append(f"Share a step-by-step {keyword} tutorial")
        suggestions.append(f"Create {keyword} ingredient prep tips")
        
        # Category-specific suggestions
        if category == TrendCategory.QUICK_MEALS:
            suggestions.append(f"Show time-saving hacks for {keyword}")
        elif category == TrendCategory.HEALTHY_EATING:
            suggestions.append(f"Highlight nutritional benefits of {keyword}")
        elif category == TrendCategory.DESSERTS:
            suggestions.append(f"Create beautiful {keyword} styling content")
        elif category == TrendCategory.VIRAL_RECIPES:
            suggestions.append(f"Film trending {keyword} reaction video")
        
        return suggestions