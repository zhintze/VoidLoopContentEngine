#!/usr/bin/env python3

"""
Comprehensive test of trend-driven content generation
Tests the complete pipeline from trend scraping to content creation
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from services.trend_template_integrator import TrendTemplateIntegrator
from services.trend_scraper import TrendScraper
from services.trend_analyzer import TrendAnalyzer
from services.trend_filter import RecipeTrendFilter
from models.trend import TrendKeyword, TrendCategory, TrendScore, TrendSource, PlatformMetrics
from factories.output_factory import OutputFactory
from models.account import Account
from template_loader import load_template_config
from datetime import datetime
import json


def create_mock_trends():
    """Create realistic mock trends for testing"""
    trends = []
    
    # Trending recipe keywords
    trend_data = [
        {
            'keyword': 'air fryer chicken',
            'category': TrendCategory.COOKING_TECHNIQUES,
            'score': 85.0,
            'growth_rate': 15.2,
            'is_rising': True,
            'related': ['crispy chicken', 'healthy chicken', 'quick chicken']
        },
        {
            'keyword': 'protein smoothie bowl',
            'category': TrendCategory.HEALTHY_EATING,
            'score': 72.5,
            'growth_rate': 8.7,
            'is_rising': True,
            'related': ['breakfast bowl', 'smoothie recipes', 'high protein']
        },
        {
            'keyword': 'viral pasta recipe',
            'category': TrendCategory.VIRAL_RECIPES,
            'score': 91.3,
            'growth_rate': 22.1,
            'is_rising': True,
            'related': ['tiktok pasta', 'baked feta pasta', 'easy pasta']
        },
        {
            'keyword': 'keto dessert',
            'category': TrendCategory.DIETARY_RESTRICTIONS,
            'score': 68.2,
            'growth_rate': 5.4,
            'is_rising': True,
            'related': ['low carb dessert', 'sugar free dessert', 'keto recipes']
        },
        {
            'keyword': 'meal prep containers',
            'category': TrendCategory.QUICK_MEALS,
            'score': 78.9,
            'growth_rate': 12.8,
            'is_rising': True,
            'related': ['meal prep ideas', 'healthy meal prep', 'weekly meal prep']
        }
    ]
    
    for data in trend_data:
        trend = TrendKeyword(
            keyword=data['keyword'],
            category=data['category'],
            score=TrendScore(
                current_score=data['score'],
                peak_score=min(data['score'] * 1.05, 100.0),  # Ensure peak_score <= 100
                growth_rate=data['growth_rate']
            ),
            platform_metrics=[
                PlatformMetrics(
                    source=TrendSource.GOOGLE_TRENDS,
                    engagement_score=data['score'],
                    last_updated=datetime.now()
                ),
                PlatformMetrics(
                    source=TrendSource.INSTAGRAM,
                    engagement_score=data['score'] * 0.9,
                    last_updated=datetime.now()
                )
            ],
            related_keywords=data['related'],
            first_detected=datetime.now(),
            last_updated=datetime.now(),
            is_rising=data['is_rising']
        )
        trends.append(trend)
    
    return trends


def test_trend_integration():
    """Test trend integration with templates"""
    print("🧪 Testing Trend-Template Integration")
    print("=" * 50)
    
    try:
        # Create mock trends
        trends = create_mock_trends()
        print(f"✓ Created {len(trends)} mock trends")
        
        # Initialize integrator
        integrator = TrendTemplateIntegrator()
        
        # Test context enhancement for different platforms
        base_context = {
            'tone': 'engaging',
            'keywords': ['recipe', 'delicious'],
            'hashtags': ['#recipe', '#food']
        }
        
        platforms_to_test = ['instagram', 'twitter', 'pinterest', 'facebook']
        
        for platform in platforms_to_test:
            print(f"\n📱 Testing {platform.upper()} integration...")
            
            # Mock the trend retrieval to return our test trends
            integrator._get_relevant_trends = lambda p, prefs=None: trends
            
            enhanced_context = integrator.enhance_template_context(
                base_context, 
                platform=platform,
                trend_preferences={'min_score': 70.0}
            )
            
            print(f"   Keywords: {enhanced_context.get('keywords', [])}")
            print(f"   Hashtags: {enhanced_context.get('hashtags', [])}")
            print(f"   Tone: {enhanced_context.get('tone', 'N/A')}")
            
            if 'trend_insights' in enhanced_context:
                insights = enhanced_context['trend_insights']
                print(f"   Trending: {', '.join(insights['trending_keywords'][:3])}")
                if insights['viral_potential']:
                    viral = insights['viral_potential'][0]
                    print(f"   Viral Potential: {viral['keyword']} ({viral['score']:.1f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Trend integration test failed: {e}")
        return False


def test_content_generation_with_trends():
    """Test full content generation with trend data"""
    print("\n🎯 Testing Trend-Driven Content Generation")
    print("=" * 50)
    
    try:
        # Load a template
        template = load_template_config('recipe_twitter')
        print(f"✓ Loaded template: {template.name}")
        
        # Create a test account
        test_account = Account(
            account_id="trend_test",
            name="Trend Test Account",
            site="@foodieguru",
            template_id="recipe_twitter",
            keywords=["recipe", "healthy", "quick"],
            tone="exciting",
            hashtags=["#recipe", "#healthy"]
        )
        
        # Initialize integrator and add mock trends
        integrator = TrendTemplateIntegrator()
        trends = create_mock_trends()
        integrator._get_relevant_trends = lambda p, prefs=None: trends
        
        # Test context enhancement
        base_context = {
            'tone': test_account.tone,
            'keywords': test_account.keywords,
            'hashtags': test_account.hashtags
        }
        
        enhanced_context = integrator.enhance_template_context(
            base_context, 
            'twitter',
            template.trend_preferences
        )
        
        print("✓ Enhanced context with trends")
        print(f"   Original keywords: {base_context['keywords']}")
        print(f"   Enhanced keywords: {enhanced_context['keywords']}")
        
        # Test hashtag optimization
        optimized_hashtags = integrator.optimize_hashtags_for_trends(
            base_context['hashtags'],
            trends,
            'twitter'
        )
        print(f"   Original hashtags: {base_context['hashtags']}")
        print(f"   Optimized hashtags: {optimized_hashtags}")
        
        # Test content timing suggestions
        timing = integrator.suggest_content_timing(trends)
        print(f"   Content timing: {timing['urgency_level']} urgency")
        print(f"   Recommendation: {timing['recommendation']}")
        
        # Generate content variations
        print("\n📝 Generating Content Variations...")
        
        # Mock template content for demonstration
        template_content = """Create a {{ tone }} Twitter post about {{ keywords[0] }}.
        
{% if trend_insights %}
🔥 Trending: {{ trend_insights.trending_keywords[0] }}
{% endif %}

Focus on {{ keywords | join(' and ') }}.
Use hashtags: {{ hashtags | join(' ') }}

{% if content_suggestions %}
💡 {{ content_suggestions[0] }}
{% endif %}"""
        
        variations = integrator.generate_trending_variations(
            template_content, 
            trends[:3], 
            variations=3
        )
        
        for i, variation in enumerate(variations, 1):
            print(f"\n   Variation {i}:")
            print(f"   {variation[:100]}...")
        
        print(f"\n✅ Generated {len(variations)} content variations")
        
        return True
        
    except Exception as e:
        print(f"❌ Content generation test failed: {e}")
        return False


def test_trend_analysis():
    """Test trend analysis capabilities"""
    print("\n📊 Testing Trend Analysis")
    print("=" * 50)
    
    try:
        analyzer = TrendAnalyzer()
        trends = create_mock_trends()
        
        # Test trend classification
        print("🏷️  Trend Classification:")
        for trend in trends[:3]:
            trend_type = analyzer.classify_trend_type(trend)
            composite_score = analyzer.calculate_composite_score(trend)
            print(f"   {trend.keyword}: {trend_type} (Score: {composite_score:.1f})")
        
        # Test trend comparison
        print("\n⚖️  Trend Comparison:")
        if len(trends) >= 2:
            comparison = analyzer.compare_trends(trends[0], trends[1])
            print(f"   Winner: {comparison['winner']}")
            print(f"   Score Difference: {comparison['score_difference']:.1f}")
        
        # Test trend analysis
        print("\n🔍 Comprehensive Analysis:")
        analysis = analyzer.analyze_trends(trends)
        
        print(f"   Total trends analyzed: {analysis['total_trends']}")
        print(f"   Average score: {analysis['score_distribution']['mean']:.1f}")
        print(f"   Rising trends: {analysis['growth_analysis']['rising_trends']}")
        
        if analysis['insights']:
            print("   Key insights:")
            for insight in analysis['insights'][:2]:
                print(f"     • {insight}")
        
        if analysis['recommendations']:
            print("   Recommendations:")
            for rec in analysis['recommendations'][:2]:
                print(f"     • {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Trend analysis test failed: {e}")
        return False


def test_trend_filtering():
    """Test trend filtering capabilities"""
    print("\n🔍 Testing Trend Filtering")
    print("=" * 50)
    
    try:
        filter_service = RecipeTrendFilter()
        trends = create_mock_trends()
        
        # Test food relevance filtering
        filtered_trends = filter_service.filter_food_trends(trends, min_relevance_score=0.5)
        print(f"✓ Food relevance filter: {len(filtered_trends)}/{len(trends)} trends passed")
        
        # Test categorization
        categorized = filter_service.categorize_food_trends(filtered_trends)
        print(f"✓ Categorized into {len(categorized)} categories:")
        for category, trend_list in categorized.items():
            if trend_list:  # Only show non-empty categories
                print(f"   {category.value}: {len(trend_list)} trends")
        
        # Test dietary filtering
        vegan_trends = filter_service.filter_by_dietary_restrictions(
            filtered_trends, 
            ['vegan', 'plant based']
        )
        print(f"✓ Vegan-friendly trends: {len(vegan_trends)} found")
        
        # Test skill level filtering
        beginner_trends = filter_service.filter_by_cooking_skill(
            filtered_trends, 
            'beginner'
        )
        print(f"✓ Beginner-friendly trends: {len(beginner_trends)} found")
        
        # Test trend enhancement
        enhanced_trends = filter_service.enhance_trend_keywords(filtered_trends[:2])
        print(f"✓ Enhanced {len(enhanced_trends)} trends with related keywords")
        
        for trend in enhanced_trends:
            if hasattr(trend, 'content_suggestions') and trend.content_suggestions:
                print(f"   {trend.keyword}: {len(trend.content_suggestions)} content suggestions")
        
        return True
        
    except Exception as e:
        print(f"❌ Trend filtering test failed: {e}")
        return False


def main():
    """Run all trend integration tests"""
    print("🔬 Void Loop Content Engine - Trend Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Trend Integration", test_trend_integration),
        ("Content Generation", test_content_generation_with_trends),
        ("Trend Analysis", test_trend_analysis),
        ("Trend Filtering", test_trend_filtering)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED! Trend-driven content generation is working!")
        print("\n🚀 Ready to use trend-driven features:")
        print("   • python cli.py scrape-trends")
        print("   • python cli.py list-trends")
        print("   • python cli.py analyze-trends")
        print("   • python cli.py generate-report")
        print("   • python cli.py start-scheduler")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("🔧 Try running the basic trend test first:")
        print("   python test_trends.py")


if __name__ == "__main__":
    main()