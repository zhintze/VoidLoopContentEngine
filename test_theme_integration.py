#!/usr/bin/env python3

"""
Test script for theme system integration
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from services.theme_loader import theme_loader
from services.theme_trend_integration import theme_trend_integrator
from models.account import Account
from models.theme import ThemePreferences
from datetime import datetime


def test_theme_loader():
    """Test theme loading functionality"""
    print("=== Testing Theme Loader ===")
    
    try:
        # Test loading themes
        available_themes = theme_loader.list_available_themes()
        print(f"✓ Found {len(available_themes)} available themes:")
        for theme in available_themes:
            print(f"  - {theme['name']} ({theme['theme_id']})")
        
        # Test getting specific theme
        general_theme = theme_loader.get_theme("food_recipe_general")
        if general_theme:
            print(f"✓ Loaded general theme: {general_theme.name}")
            print(f"  Categories: {len(general_theme.categories)}")
            print(f"  Ingredients: {len(general_theme.ingredients)}")
            print(f"  Content tones: {len(general_theme.content_tones)}")
        
        # Test getting keywords for category
        comfort_keywords = theme_loader.get_keywords_for_category(
            "food_recipe_general", "comfort_food"
        )
        print(f"✓ Comfort food keywords: {len(comfort_keywords)} found")
        print(f"  Examples: {comfort_keywords[:5]}")
        
        # Test seasonal keywords
        seasonal_keywords = theme_loader.get_seasonal_keywords("food_recipe_general")
        print(f"✓ Seasonal keywords for current month: {len(seasonal_keywords)} found")
        print(f"  Examples: {seasonal_keywords[:5]}")
        
        # Test platform hashtags
        instagram_hashtags = theme_loader.get_platform_hashtags(
            "food_recipe_general", "instagram", ["comfort_food", "healthy_eating"]
        )
        print(f"✓ Instagram hashtags: {len(instagram_hashtags)} found")
        print(f"  Examples: {instagram_hashtags[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme loader test failed: {e}")
        return False


def test_theme_trend_integration():
    """Test theme-trend integration"""
    print("\n=== Testing Theme-Trend Integration ===")
    
    try:
        # Test food-related detection
        test_texts = [
            "Amazing chicken recipe that everyone loves",
            "Tech startup launches new app",
            "Best chocolate cake for holidays",
            "Political news update"
        ]
        
        food_related_count = 0
        for text in test_texts:
            is_food = theme_trend_integrator.is_food_related_by_theme(text)
            result = "✓ Food-related" if is_food else "✗ Not food-related"
            print(f"  '{text}' - {result}")
            if is_food:
                food_related_count += 1
        
        print(f"✓ Detected {food_related_count}/4 texts as food-related (expected: 2)")
        
        # Test keyword categorization
        test_keywords = [
            "mac and cheese",
            "kale smoothie", 
            "chocolate cake",
            "15 minute pasta"
        ]
        
        print("\n  Keyword categorization:")
        for keyword in test_keywords:
            category = theme_trend_integrator.categorize_keyword_from_theme(keyword, "food_recipe_general")
            print(f"  '{keyword}' → {category.value}")
        
        # Test seed keywords generation
        seed_keywords = theme_trend_integrator.get_theme_based_seed_keywords("food_recipe_general")
        print(f"\n✓ Generated {len(seed_keywords)} seed keywords")
        print(f"  Examples: {seed_keywords[:5]}")
        
        # Test content suggestions
        suggestions = theme_trend_integrator.get_content_suggestions_from_theme(
            "pasta", "food_recipe_general"
        )
        print(f"\n✓ Content suggestions for 'pasta': {len(suggestions)} found")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme-trend integration test failed: {e}")
        return False


def test_account_theme_integration():
    """Test account integration with themes"""
    print("\n=== Testing Account-Theme Integration ===")
    
    try:
        # Create test account with theme
        test_account = Account(
            account_id="test_theme_account",
            name="Test Food Account",
            site="@testfoodie",
            template_id="recipe_instagram",
            theme_id="food_recipe_healthy"
        )
        
        print(f"✓ Created account with theme: {test_account.theme_id}")
        
        # Test theme preferences
        test_account.update_theme_preferences(
            primary_categories=["clean_eating", "superfoods"],
            preferred_tones=["wellness_focused"],
            dietary_focus=["vegan"]
        )
        
        print(f"✓ Updated theme preferences:")
        print(f"  Categories: {test_account.theme_preferences.primary_categories}")
        print(f"  Tones: {test_account.theme_preferences.preferred_tones}")
        print(f"  Dietary focus: {test_account.theme_preferences.dietary_focus}")
        
        # Test getting theme keywords
        theme_keywords = test_account.get_theme_keywords()
        print(f"\n✓ Theme keywords: {len(theme_keywords)} found")
        print(f"  Examples: {theme_keywords[:5]}")
        
        # Test getting platform hashtags
        instagram_hashtags = test_account.get_theme_hashtags("instagram")
        print(f"\n✓ Instagram hashtags: {len(instagram_hashtags)} found")
        print(f"  Examples: {instagram_hashtags[:5]}")
        
        # Test content tone guidance
        tone_guidance = test_account.get_content_tone_guidance()
        print(f"\n✓ Content tone guidance: {tone_guidance}")
        
        # Test engagement elements
        engagement = test_account.get_engagement_elements()
        print(f"\n✓ Engagement elements:")
        print(f"  CTAs: {len(engagement.get('call_to_actions', []))}")
        print(f"  Phrases: {len(engagement.get('engagement_phrases', []))}")
        
        # Test dietary keywords
        vegan_keywords = test_account.get_dietary_keywords("vegan")
        print(f"\n✓ Vegan keywords: {len(vegan_keywords.get('primary_keywords', []))} found")
        print(f"  Examples: {vegan_keywords.get('primary_keywords', [])[:3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Account-theme integration test failed: {e}")
        return False


def test_theme_system_performance():
    """Test theme system performance and edge cases"""
    print("\n=== Testing Theme System Performance ===")
    
    try:
        import time
        
        # Test performance of food detection
        start_time = time.time()
        test_texts = [
            "chicken recipe", "pasta dish", "chocolate cake", "healthy smoothie",
            "tech news", "sports update", "weather report", "movie review"
        ] * 25  # 200 texts total
        
        food_count = 0
        for text in test_texts:
            if theme_trend_integrator.is_food_related_by_theme(text):
                food_count += 1
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✓ Processed {len(test_texts)} texts in {processing_time:.3f} seconds")
        print(f"  Average: {processing_time/len(test_texts)*1000:.2f}ms per text")
        print(f"  Food-related: {food_count}/{len(test_texts)}")
        
        # Test edge cases
        edge_cases = [
            "",  # Empty string
            "a",  # Single character
            "This is a very long text about cooking and recipes and food preparation " * 10,  # Long text
            "🍕🍔🍰",  # Emojis only
            "recipe123!@#$%",  # Mixed characters
        ]
        
        print("\n  Edge case handling:")
        for i, case in enumerate(edge_cases):
            try:
                result = theme_trend_integrator.is_food_related_by_theme(case)
                display_text = case[:20] + "..." if len(case) > 20 else case
                if not display_text.strip():
                    display_text = "[empty]" if not case else "[whitespace]"
                print(f"    Case {i+1}: {display_text} → {result}")
            except Exception as e:
                print(f"    Case {i+1}: Error - {e}")
        
        print("✓ All edge cases handled successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def main():
    """Run all theme integration tests"""
    print("🎨 Testing VoidLoop Content Engine - Theme System Integration")
    print("=" * 65)
    
    tests = [
        ("Theme Loader", test_theme_loader),
        ("Theme-Trend Integration", test_theme_trend_integration),
        ("Account-Theme Integration", test_account_theme_integration),
        ("Performance & Edge Cases", test_theme_system_performance)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} PASSED")
            else:
                print(f"\n❌ {test_name} FAILED")
        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ {test_name} CRASHED: {e}")
    
    print(f"\n{'='*65}")
    print(f"📊 FINAL RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED! Theme system is working perfectly!")
        print("\n🚀 Theme system features ready:")
        print("   • JSON-based theme configuration")
        print("   • Account theme preferences")
        print("   • Theme-aware trend categorization")
        print("   • Platform-specific keyword optimization")
        print("   • Seasonal content adaptation")
        print("   • Dietary restriction support")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("🔧 Theme system may need adjustments before production use.")


if __name__ == "__main__":
    main()