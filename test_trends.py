#!/usr/bin/env python3

"""
Test script for the trend scraping functionality
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from services.trend_scraper import TrendScraper
from services.tiktok_trends import TikTokTrendsService
from services.pinterest_trends import PinterestTrendsService
from services.instagram_trends import InstagramTrendsService
from models.trend import TrendCategory


def test_new_platform_services():
    """Test new platform trend services"""
    print("=== Testing New Platform Services ===")
    
    success_count = 0
    total_tests = 3
    
    # Test TikTok service
    try:
        print("Testing TikTok Trends Service...")
        tiktok_service = TikTokTrendsService()
        print("✓ TikTokTrendsService initialized successfully")
        
        # Test viral content
        viral_trends = tiktok_service.get_viral_food_content(limit=5)
        print(f"✓ Found {len(viral_trends)} viral TikTok trends")
        for trend in viral_trends[:2]:
            print(f"  - {trend.keyword}: Score {trend.score.current_score:.1f} "
                  f"({'📈' if trend.is_rising else '📉'})")
        success_count += 1
        
    except Exception as e:
        print(f"❌ TikTok service test failed: {e}")
    
    # Test Pinterest service
    try:
        print("\nTesting Pinterest Trends Service...")
        pinterest_service = PinterestTrendsService()
        print("✓ PinterestTrendsService initialized successfully")
        
        # Test trending pins
        pin_trends = pinterest_service.get_trending_food_pins(limit=5)
        print(f"✓ Found {len(pin_trends)} trending Pinterest pins")
        for trend in pin_trends[:2]:
            print(f"  - {trend.keyword}: Score {trend.score.current_score:.1f} "
                  f"({'📈' if trend.is_rising else '📉'})")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Pinterest service test failed: {e}")
    
    # Test Instagram service
    try:
        print("\nTesting Instagram Trends Service...")
        instagram_service = InstagramTrendsService()
        print("✓ InstagramTrendsService initialized successfully")
        
        # Test visual trends
        visual_trends = instagram_service.get_visual_food_trends(limit=5)
        print(f"✓ Found {len(visual_trends)} visual Instagram trends")
        for trend in visual_trends[:2]:
            print(f"  - {trend.keyword}: Score {trend.score.current_score:.1f} "
                  f"({'📈' if trend.is_rising else '📉'})")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Instagram service test failed: {e}")
    
    print(f"\n✓ Platform services test: {success_count}/{total_tests} services working")
    return success_count == total_tests


def test_trend_storage():
    """Test trend storage functionality"""
    print("\n=== Testing Trend Storage ===")
    
    try:
        from models.trend_storage import TrendStorage
        from models.trend import TrendKeyword, TrendCategory, TrendScore
        from datetime import datetime
        
        storage = TrendStorage()
        print("✓ TrendStorage initialized successfully")
        
        # Create a test trend
        test_trend = TrendKeyword(
            keyword="test recipe",
            category=TrendCategory.QUICK_MEALS,
            score=TrendScore(current_score=75.0, peak_score=80.0, growth_rate=5.0),
            first_detected=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Save and retrieve
        storage.save_trend_keyword(test_trend)
        retrieved = storage.get_trend_keyword("test recipe")
        
        if retrieved and retrieved.keyword == "test recipe":
            print("✓ Trend storage/retrieval working")
            return True
        else:
            print("❌ Trend storage/retrieval failed")
            return False
            
    except Exception as e:
        print(f"❌ Trend storage test failed: {e}")
        return False


def test_trend_scraper():
    """Test the main trend scraper"""
    print("\n=== Testing Trend Scraper ===")
    
    try:
        scraper = TrendScraper()
        print("✓ TrendScraper initialized successfully")
        
        # Test quick trending topics scrape
        print("Fetching trending topics (this may take a moment)...")
        trends = scraper.scrape_trending_topics_only(limit=5)
        
        print(f"Found {len(trends)} trending topics:")
        for trend in trends:
            print(f"  - {trend.keyword}: {trend.score.current_score:.1f}")
        
        # Get summary
        summary = scraper.get_trend_summary()
        print(f"✓ Database stats: {summary['database_stats']['total_keywords']} keywords stored")
        
        return True
        
    except Exception as e:
        print(f"❌ Trend scraper test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🔍 Testing Void Loop Content Engine - Trend Scraping")
    print("=" * 50)
    
    tests = [
        test_new_platform_services,
        test_trend_storage, 
        test_trend_scraper
    ]
    
    passed = 0
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Trend scraping is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()