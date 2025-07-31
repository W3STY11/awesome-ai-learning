#!/usr/bin/env python3
"""
Test script for the repository analyzer.
"""

import json
import sys
from pathlib import Path

# Add tools directory to path
sys.path.append(str(Path(__file__).parent))

from analyze_repos import RepositoryAnalyzer


def test_basic_functionality():
    """Test basic analyzer functionality without heavy ML dependencies."""
    print("Testing Repository Analyzer...")
    
    # Test data path
    data_path = Path(__file__).parent.parent / "data" / "starred_repos_latest.json"
    cache_path = Path(__file__).parent.parent / "cache_test"
    
    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        return False
    
    try:
        # Initialize analyzer
        analyzer = RepositoryAnalyzer(data_path, cache_path)
        
        # Test loading repositories
        if not analyzer.load_repositories():
            print("❌ Failed to load repositories")
            return False
        
        print(f"✅ Loaded {len(analyzer.repositories)} repositories")
        
        # Test text processing
        sample_repo = analyzer.repositories[0]
        repo_text = analyzer.create_repo_text(sample_repo)
        print(f"✅ Text processing works. Sample: {repo_text[:100]}...")
        
        # Test scoring functions
        popularity = analyzer.calculate_popularity_score(sample_repo)
        freshness = analyzer.calculate_freshness_score(sample_repo)
        learning_value = analyzer.calculate_learning_value_score(sample_repo, repo_text)
        documentation = analyzer.calculate_documentation_score(sample_repo)
        
        print(f"✅ Scoring works. Sample scores:")
        print(f"   Popularity: {popularity:.3f}")
        print(f"   Freshness: {freshness:.3f}")
        print(f"   Learning Value: {learning_value:.3f}")
        print(f"   Documentation: {documentation:.3f}")
        
        # Test rule-based classification
        category = analyzer.classify_repository_rule_based(sample_repo, repo_text)
        print(f"✅ Classification works. Sample category: {category}")
        
        print("✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sample_analysis():
    """Test analysis on a small sample."""
    print("\nTesting sample analysis...")
    
    data_path = Path(__file__).parent.parent / "data" / "starred_repos_latest.json"
    cache_path = Path(__file__).parent.parent / "cache_test"
    
    try:
        analyzer = RepositoryAnalyzer(data_path, cache_path)
        
        # Load and analyze just the first 10 repositories
        if not analyzer.load_repositories():
            print("❌ Failed to load repositories")
            return False
        
        # Limit to first 10 for testing
        original_repos = analyzer.repositories
        analyzer.repositories = analyzer.repositories[:10]
        
        print(f"Testing with {len(analyzer.repositories)} repositories...")
        
        # Run rule-based analysis (faster)
        classifications = analyzer.classify_repositories_rule_based()
        scores = analyzer.calculate_comprehensive_scores()
        
        print("✅ Sample analysis completed!")
        print("\nSample results:")
        
        for i, repo in enumerate(analyzer.repositories[:5]):
            full_name = repo['full_name']
            category = classifications.get(full_name, 'Unknown')
            composite_score = scores.get(full_name, {}).get('composite', 0)
            
            print(f"  {i+1}. {repo['name']}")
            print(f"     Category: {category}")
            print(f"     Score: {composite_score:.3f}")
            print(f"     Stars: {repo['stars']}")
            print()
        
        # Restore original repositories
        analyzer.repositories = original_repos
        
        return True
        
    except Exception as e:
        print(f"❌ Sample analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Repository Analyzer Test Suite")
    print("=" * 40)
    
    # Run tests
    basic_passed = test_basic_functionality()
    
    if basic_passed:
        sample_passed = test_sample_analysis()
        
        if sample_passed:
            print("\n🎉 All tests passed! The analyzer is ready to use.")
            print("\nTo run the full analysis:")
            print("  cd tools/")
            print("  python analyze_repos.py --help")
            print("  python analyze_repos.py --no-embeddings  # Fast mode")
            print("  python analyze_repos.py                  # Full mode with embeddings")
        else:
            print("\n⚠️  Basic tests passed but sample analysis failed.")
    else:
        print("\n❌ Basic tests failed. Please check the setup.")