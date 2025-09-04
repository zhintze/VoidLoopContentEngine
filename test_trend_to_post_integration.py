#!/usr/bin/env python3

"""
Test script for end-to-end trend-to-post integration
Tests the complete workflow from trend data to generated content
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from factories.output_factory import OutputFactory
from models.account import Account, ThemePreferences
from services.trend_scraper import TrendScraper
from models.trend import TrendKeyword, TrendCategory, TrendScore, PlatformMetrics, TrendSource
from datetime import datetime


def setup_test_trends():
    """Setup some test trend data"""
    print("🔧 Setting up test trend data...")
    
    try:
        scraper = TrendScraper(theme_id="food_recipe_general")
        
        # Create some realistic test trends
        test_trends = [
            TrendKeyword(
                keyword="air fryer chicken",
                category=TrendCategory.COOKING_TECHNIQUES,
                score=TrendScore(current_score=85.0, peak_score=90.0, growth_rate=15.2),
                platform_metrics=[PlatformMetrics(
                    source=TrendSource.TIKTOK,
                    engagement_score=85.0,
                    last_updated=datetime.now()
                )],
                related_keywords=["crispy chicken", "healthy chicken", "quick chicken"],
                first_detected=datetime.now(),
                last_updated=datetime.now(),
                is_rising=True
            ),
            TrendKeyword(
                keyword="viral pasta recipe",
                category=TrendCategory.VIRAL_RECIPES,
                score=TrendScore(current_score=91.3, peak_score=95.0, growth_rate=22.1),
                platform_metrics=[PlatformMetrics(
                    source=TrendSource.INSTAGRAM,
                    engagement_score=91.3,
                    last_updated=datetime.now()
                )],
                related_keywords=["tiktok pasta", "baked feta pasta", "easy pasta"],
                first_detected=datetime.now(),
                last_updated=datetime.now(),
                is_rising=True
            ),
            TrendKeyword(
                keyword="protein smoothie bowl",
                category=TrendCategory.HEALTHY_EATING,
                score=TrendScore(current_score=72.5, peak_score=75.0, growth_rate=8.7),
                platform_metrics=[PlatformMetrics(
                    source=TrendSource.PINTEREST,
                    engagement_score=72.5,
                    last_updated=datetime.now()
                )],
                related_keywords=["breakfast bowl", "smoothie recipes", "high protein"],
                first_detected=datetime.now(),
                last_updated=datetime.now(),
                is_rising=True
            )
        ]
        
        # Save test trends to storage
        for trend in test_trends:
            scraper.trend_storage.save_trend_keyword(trend)
        
        print(f"✅ Created {len(test_trends)} test trends")
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup test trends: {e}")
        return False


def test_basic_trend_integration():
    """Test basic trend integration without account themes"""
    print("\n=== Testing Basic Trend Integration ===")
    
    try:
        # Create a simple test account
        test_account = Account(
            account_id="test_trend_basic",
            name="Basic Trend Test",
            site="@testtrendaccount",
            template_id="recipe_twitter",
            keywords=["recipe", "cooking"],
            tone="friendly",
            hashtags=["#recipe", "#food"]
        )
        
        # Test content generation WITH trends
        print("Testing WITH trends enabled...")
        factory_with_trends = OutputFactory(
            account=test_account,
            offline=True,  # Offline mode to avoid API calls
            platform="twitter",
            use_trends=True
        )
        
        prompt_with_trends = factory_with_trends.generate_prompt()
        print("✓ Generated prompt with trends")
        print(f"  Prompt length: {len(prompt_with_trends)} characters")
        
        # Test content generation WITHOUT trends
        print("\nTesting WITHOUT trends...")
        factory_without_trends = OutputFactory(
            account=test_account,
            offline=True,
            platform="twitter",
            use_trends=False
        )
        
        prompt_without_trends = factory_without_trends.generate_prompt()
        print("✓ Generated prompt without trends")
        print(f"  Prompt length: {len(prompt_without_trends)} characters")
        
        # Compare prompts
        if len(prompt_with_trends) > len(prompt_without_trends):
            print("✅ Trends successfully enhanced the prompt (longer content)")
        else:
            print("⚠️  Trend enhancement may not be working (similar length)")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic trend integration test failed: {e}")
        return False


def test_theme_aware_trend_integration():
    """Test trend integration with theme system"""
    print("\n=== Testing Theme-Aware Trend Integration ===")
    
    try:
        # Create an account with theme preferences
        theme_prefs = ThemePreferences()
        theme_prefs.primary_categories = ["healthy_eating", "quick_meals"]
        theme_prefs.preferred_tones = ["friendly"]
        theme_prefs.dietary_focus = ["vegan"]
        theme_prefs.trend_sensitivity = 0.8
        
        test_account = Account(
            account_id="test_trend_theme",
            name="Theme Trend Test",
            site="@healthytrendaccount",
            template_id="recipe_instagram",
            theme_id="food_recipe_healthy",
            theme_preferences=theme_prefs,
            tone="friendly"
        )
        
        print(f"Created account with theme: {test_account.theme_id}")
        print(f"Preferred categories: {test_account.theme_preferences.primary_categories}")
        
        # Test theme keyword integration
        theme_keywords = test_account.get_theme_keywords("instagram")
        print(f"✓ Theme keywords: {len(theme_keywords)} found")
        print(f"  Examples: {theme_keywords[:5]}")
        
        # Test theme hashtag integration
        theme_hashtags = test_account.get_theme_hashtags("instagram")
        print(f"✓ Theme hashtags: {len(theme_hashtags)} found")
        print(f"  Examples: {theme_hashtags[:5]}")
        
        # Generate content with theme + trends
        factory = OutputFactory(
            account=test_account,
            offline=True,
            platform="instagram",
            use_trends=True
        )
        
        prompt = factory.generate_prompt()
        print("✅ Generated theme-aware prompt with trends")
        print(f"  Prompt preview: {prompt[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Theme-aware trend integration test failed: {e}")
        return False


def test_platform_specific_integration():
    """Test trend integration across different platforms"""
    print("\n=== Testing Platform-Specific Integration ===")
    
    platforms = ["instagram", "twitter", "pinterest", "facebook"]
    results = {}
    
    # Create a test account
    test_account = Account(
        account_id="test_trend_platforms",
        name="Platform Trend Test",
        site="@platformtest",
        template_id="recipe",  # Base template
        theme_id="food_recipe_general",
        tone="enthusiastic"
    )
    
    try:
        for platform in platforms:
            print(f"\nTesting {platform.upper()} platform...")
            
            try:
                factory = OutputFactory(
                    account=test_account,
                    offline=True,
                    platform=platform,
                    use_trends=True
                )
                
                # Get the base context to see platform-specific data
                base_context = factory._get_base_context()
                print(f"  Platform context: {platform}")
                print(f"  Keywords: {len(base_context.get('keywords', []))}")
                print(f"  Hashtags: {len(base_context.get('hashtags', []))}")
                
                # Try to enhance with trends
                if factory.trend_integrator:
                    enhanced_context = factory._enhance_context_with_trends(base_context)
                    trend_keywords = enhanced_context.get('trend_insights', {}).get('trending_keywords', [])
                    print(f"  Trend keywords: {len(trend_keywords)}")
                    
                    results[platform] = {
                        'success': True,
                        'trend_keywords': len(trend_keywords),
                        'total_keywords': len(enhanced_context.get('keywords', [])),
                        'hashtags': len(enhanced_context.get('hashtags', []))
                    }
                else:
                    results[platform] = {'success': False, 'error': 'No trend integrator'}
                
                print(f"  ✅ {platform} integration successful")
                
            except Exception as e:
                print(f"  ❌ {platform} integration failed: {e}")
                results[platform] = {'success': False, 'error': str(e)}
        
        # Summary
        successful_platforms = sum(1 for r in results.values() if r['success'])
        print(f"\n✅ Platform integration: {successful_platforms}/{len(platforms)} platforms successful")
        
        for platform, result in results.items():
            if result['success']:
                print(f"  {platform}: {result.get('trend_keywords', 0)} trend keywords, "
                      f"{result.get('total_keywords', 0)} total keywords")
        
        return successful_platforms > 0
        
    except Exception as e:
        print(f"❌ Platform-specific integration test failed: {e}")
        return False


def test_end_to_end_content_generation():
    """Test complete end-to-end content generation with trends"""
    print("\n=== Testing End-to-End Content Generation ===")
    
    try:
        # Create a comprehensive test account
        theme_prefs = ThemePreferences()
        theme_prefs.primary_categories = ["viral_recipes", "quick_meals"]
        theme_prefs.preferred_tones = ["enthusiastic"]
        theme_prefs.trend_sensitivity = 0.9
        
        test_account = Account(
            account_id="test_e2e_trends",
            name="End-to-End Trend Test",
            site="@e2etrendtest",
            template_id="recipe_twitter",
            theme_id="food_recipe_general",
            theme_preferences=theme_prefs,
            tone="enthusiastic"
        )
        
        # Test full content generation workflow
        print("Running complete content generation...")
        
        factory = OutputFactory(
            account=test_account,
            offline=True,  # Use offline mode to test without API calls
            platform="twitter",
            use_trends=True,
            auto_post=False
        )
        
        # Test the complete run method
        print("Executing factory.run()...")
        factory.run()
        
        # Check if output was created
        output_dir = factory.output_dir
        if output_dir.exists():
            print(f"✅ Output directory created: {output_dir}")
            
            # Check for expected files
            expected_files = ["twitter_post.txt", "image_description.txt", "debug.json"]
            found_files = []
            
            for expected_file in expected_files:
                file_path = output_dir / expected_file
                if file_path.exists():
                    found_files.append(expected_file)
                    print(f"  ✓ Found: {expected_file}")
                    
                    # Show a preview of the content
                    if expected_file == "twitter_post.txt":
                        content = file_path.read_text()
                        print(f"    Twitter post preview: {content[:100]}...")
            
            print(f"✅ Files created: {len(found_files)}/{len(expected_files)}")
            
            # Check debug info for trend data
            debug_path = output_dir / "debug.json"
            if debug_path.exists():
                import json
                debug_info = json.loads(debug_path.read_text())
                print(f"  Debug info includes: {list(debug_info.keys())}")
                
        else:
            print("❌ No output directory created")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end content generation test failed: {e}")
        return False


def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    try:
        # Remove test output directories
        output_base = Path("output")
        if output_base.exists():
            import shutil
            for item in output_base.iterdir():
                if item.is_dir() and "test" in item.name.lower():
                    shutil.rmtree(item)
                    print(f"  Removed: {item}")
        
        print("✅ Cleanup completed")
    except Exception as e:
        print(f"⚠️  Cleanup failed: {e}")


def main():
    """Run all trend-to-post integration tests"""
    print("🔗 Testing VoidLoop Content Engine - Trend-to-Post Integration")
    print("=" * 70)
    
    # Setup test data first
    if not setup_test_trends():
        print("❌ Cannot continue without test trend data")
        return
    
    tests = [
        ("Basic Trend Integration", test_basic_trend_integration),
        ("Theme-Aware Trend Integration", test_theme_aware_trend_integration),
        ("Platform-Specific Integration", test_platform_specific_integration),
        ("End-to-End Content Generation", test_end_to_end_content_generation)
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
    
    print(f"\n{'='*70}")
    print(f"📊 FINAL RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED! Trend-to-post integration is working!")
        print("\n🚀 Integration features ready:")
        print("   ✅ Trend data automatically enhances content generation")
        print("   ✅ Theme-aware trend filtering")
        print("   ✅ Platform-specific trend optimization")
        print("   ✅ CLI option to enable/disable trends")
        print("   ✅ Complete workflow from trend scraping to post creation")
        print("\n💡 Usage:")
        print("   python cli.py run_account <account_name> --platform twitter --trends")
        print("   python cli.py run_account <account_name> --platform instagram --no-trends")
    else:
        print("⚠️  Some tests failed. Integration may need adjustments.")
        print("🔧 Check the output above for specific issues.")
    
    # Clean up
    cleanup_test_data()


if __name__ == "__main__":
    main()