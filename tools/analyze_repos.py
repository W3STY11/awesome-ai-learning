#!/usr/bin/env python3
"""
Advanced Repository Analysis Tool

This script analyzes GitHub repositories using NLP techniques to:
- Categorize repositories intelligently
- Score repositories based on multiple factors
- Generate comprehensive analysis reports

Author: AI Learning System
Date: 2025-07-30
"""

import json
import logging
import os
import pickle
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import warnings

import click
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

# Suppress transformers warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logging.warning("sentence-transformers not available. Using TF-IDF fallback.")

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("transformers not available. Using basic NLP.")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analyze_repos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """Advanced repository analyzer using NLP and ML techniques."""
    
    # Predefined categories with keywords for classification
    CATEGORIES = {
        'LLMs & Foundation Models': {
            'keywords': [
                'llm', 'large language model', 'transformer', 'gpt', 'bert', 'attention',
                'generative', 'foundation model', 'language model', 'nlp model',
                'chatbot', 'conversational ai', 'dialogue', 'text generation',
                'prompt engineering', 'fine-tuning', 'pre-trained'
            ],
            'description': 'Large Language Models, transformers, and foundation models'
        },
        'Computer Vision': {
            'keywords': [
                'computer vision', 'cv', 'image', 'video', 'vision', 'cnn',
                'object detection', 'segmentation', 'classification', 'opencv',
                'yolo', 'rcnn', 'gan', 'diffusion', 'stable diffusion',
                'image processing', 'face recognition', 'pose estimation'
            ],
            'description': 'Computer vision, image processing, and visual AI'
        },
        'Natural Language Processing': {
            'keywords': [
                'nlp', 'natural language', 'text processing', 'sentiment',
                'tokenization', 'parsing', 'ner', 'named entity', 'spacy',
                'nltk', 'text mining', 'information extraction', 'summarization',
                'translation', 'text classification', 'pos tagging'
            ],
            'description': 'Natural Language Processing and text analysis'
        },
        'MLOps & Infrastructure': {
            'keywords': [
                'mlops', 'ml ops', 'deployment', 'infrastructure', 'pipeline',
                'kubernetes', 'docker', 'model serving', 'monitoring',
                'orchestration', 'airflow', 'kubeflow', 'mlflow', 'wandb',
                'experiment tracking', 'model management', 'ci/cd', 'devops'
            ],
            'description': 'MLOps, deployment, and ML infrastructure'
        },
        'Data Science & Analytics': {
            'keywords': [
                'data science', 'analytics', 'visualization', 'jupyter',
                'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
                'data analysis', 'statistics', 'exploratory', 'dashboard',
                'business intelligence', 'data mining', 'etl'
            ],
            'description': 'Data science, analytics, and visualization'
        },
        'Machine Learning Frameworks': {
            'keywords': [
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'xgboost',
                'lightgbm', 'catboost', 'sklearn', 'jax', 'flax', 'haiku',
                'framework', 'library', 'ml framework', 'deep learning framework'
            ],
            'description': 'Machine learning frameworks and libraries'
        },
        'Educational Resources': {
            'keywords': [
                'tutorial', 'course', 'learning', 'education', 'teach',
                'example', 'demo', 'guide', 'handbook', 'introduction',
                'beginner', 'primer', 'workshop', 'lesson', 'curriculum',
                'bootcamp', 'exercises', 'practice'
            ],
            'description': 'Educational materials and learning resources'
        },
        'Research Papers & Implementations': {
            'keywords': [
                'paper', 'research', 'implementation', 'reproduction',
                'arxiv', 'neurips', 'icml', 'iclr', 'aaai', 'acl',
                'conference', 'academic', 'sota', 'state-of-the-art',
                'benchmark', 'baseline', 'official implementation'
            ],
            'description': 'Research paper implementations and academic work'
        },
        'Developer Tools & APIs': {
            'keywords': [
                'api', 'sdk', 'tool', 'utility', 'cli', 'command line',
                'automation', 'script', 'helper', 'wrapper', 'client',
                'development', 'productivity', 'extension', 'plugin'
            ],
            'description': 'Developer tools, APIs, and utilities'
        },
        'Reinforcement Learning': {
            'keywords': [
                'reinforcement learning', 'rl', 'q-learning', 'policy',
                'reward', 'agent', 'environment', 'gym', 'openai gym',
                'game', 'control', 'robotics', 'atari', 'mujoco'
            ],
            'description': 'Reinforcement learning and control systems'
        },
        'Audio & Speech': {
            'keywords': [
                'audio', 'speech', 'voice', 'sound', 'music', 'asr',
                'speech recognition', 'text to speech', 'tts', 'wav2vec',
                'whisper', 'audio processing', 'signal processing'
            ],
            'description': 'Audio processing and speech recognition'
        },
        'Time Series & Forecasting': {
            'keywords': [
                'time series', 'forecasting', 'prediction', 'temporal',
                'prophet', 'arima', 'lstm', 'sequence', 'trend',
                'seasonality', 'anomaly detection', 'financial'
            ],
            'description': 'Time series analysis and forecasting'
        },
        'Multimodal AI': {
            'keywords': [
                'multimodal', 'vision language', 'clip', 'dalle',
                'text to image', 'image to text', 'cross-modal',
                'vision transformer', 'vit', 'unified model'
            ],
            'description': 'Multimodal AI combining text, vision, and other modalities'
        },
        'Other': {
            'keywords': [],
            'description': 'Other AI/ML projects that don\'t fit into specific categories'
        }
    }
    
    def __init__(self, data_path: str, cache_dir: str = "cache"):
        """Initialize the analyzer."""
        self.data_path = Path(data_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize models
        self.sentence_model = None
        self.classifier = None
        
        # Data storage
        self.repositories = []
        self.embeddings = None
        self.categories_assigned = {}
        
        logger.info(f"Initialized RepositoryAnalyzer with data path: {self.data_path}")
    
    def load_sentence_model(self) -> bool:
        """Load sentence transformer model with caching."""
        if not HAS_SENTENCE_TRANSFORMERS:
            logger.warning("sentence-transformers not available")
            return False
            
        model_cache = self.cache_dir / "sentence_model.pkl"
        
        try:
            if model_cache.exists():
                logger.info("Loading cached sentence model...")
                with open(model_cache, 'rb') as f:
                    self.sentence_model = pickle.load(f)
            else:
                logger.info("Loading sentence transformer model...")
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                
                # Cache the model
                with open(model_cache, 'wb') as f:
                    pickle.dump(self.sentence_model, f)
                    
            return True
        except Exception as e:
            logger.error(f"Error loading sentence model: {e}")
            return False
    
    def load_repositories(self) -> bool:
        """Load repository data from JSON file."""
        try:
            logger.info(f"Loading repositories from {self.data_path}")
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.repositories = json.load(f)
            
            logger.info(f"Loaded {len(self.repositories)} repositories")
            return True
        except Exception as e:
            logger.error(f"Error loading repositories: {e}")
            return False
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep spaces and common punctuation
        text = re.sub(r'[^\w\s\-\+\.]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def create_repo_text(self, repo: Dict) -> str:
        """Create comprehensive text representation of a repository."""
        parts = []
        
        # Repository name (give it more weight)
        if repo.get('name'):
            name = repo['name'].replace('-', ' ').replace('_', ' ')
            parts.extend([name] * 3)  # Triple weight for name
        
        # Description (most important)
        if repo.get('description'):
            parts.extend([repo['description']] * 2)  # Double weight for description
        
        # Language
        if repo.get('language'):
            parts.append(str(repo['language']))
        
        # Topics/tags if available
        if repo.get('topics'):
            parts.extend(repo['topics'])
        
        # Homepage URL domain (might indicate type)
        if repo.get('homepage'):
            try:
                from urllib.parse import urlparse
                domain = urlparse(repo['homepage']).netloc
                if domain:
                    parts.append(domain.replace('.', ' '))
            except:
                pass
        
        # Owner name (sometimes indicates purpose)
        if repo.get('owner'):
            owner = repo['owner'].replace('-', ' ').replace('_', ' ')
            parts.append(owner)
        
        text = ' '.join(parts)
        return self.preprocess_text(text)
    
    def calculate_freshness_score(self, repo: Dict) -> float:
        """Calculate freshness score based on recent activity."""
        try:
            now = datetime.now(timezone.utc)
            
            # Parse dates
            updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
            pushed_at = datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00'))
            created_at = datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00'))
            
            # Days since last update/push
            days_since_update = (now - updated_at).days
            days_since_push = (now - pushed_at).days
            days_since_creation = (now - created_at).days
            
            # Recent activity is more important
            recent_activity = min(days_since_update, days_since_push)
            
            # Freshness score (0-1, higher is better)
            if recent_activity <= 7:
                freshness = 1.0
            elif recent_activity <= 30:
                freshness = 0.8
            elif recent_activity <= 90:
                freshness = 0.6
            elif recent_activity <= 365:
                freshness = 0.4
            elif recent_activity <= 730:
                freshness = 0.2
            else:
                freshness = 0.1
            
            # Bonus for newer projects that are actively maintained
            if days_since_creation <= 365 and recent_activity <= 30:
                freshness *= 1.2
            
            return min(freshness, 1.0)
            
        except Exception as e:
            logger.warning(f"Error calculating freshness for {repo.get('name', 'unknown')}: {e}")
            return 0.5
    
    def calculate_popularity_score(self, repo: Dict) -> float:
        """Calculate popularity score based on stars, forks, watchers."""
        stars = repo.get('stars', 0)
        forks = repo.get('forks', 0)
        watchers = repo.get('watchers', 0)
        
        # Log scale for stars (most important)
        star_score = np.log10(stars + 1) / np.log10(100000)  # Normalize to 100k stars
        
        # Fork ratio (engagement)
        fork_ratio = forks / max(stars, 1)
        fork_score = min(fork_ratio * 2, 1.0)  # Cap at 1.0
        
        # Watchers (interest)
        watcher_score = np.log10(watchers + 1) / np.log10(10000)  # Normalize to 10k watchers
        
        # Weighted combination
        popularity = (star_score * 0.6 + fork_score * 0.2 + watcher_score * 0.2)
        
        return min(popularity, 1.0)
    
    def calculate_learning_value_score(self, repo: Dict, repo_text: str) -> float:
        """Calculate learning value score for beginners."""
        score = 0.5  # Base score
        
        # Educational keywords
        educational_terms = [
            'tutorial', 'guide', 'example', 'demo', 'learn', 'beginner',
            'introduction', 'getting started', 'how to', 'step by step',
            'course', 'lesson', 'exercise', 'practice', 'handbook'
        ]
        
        for term in educational_terms:
            if term in repo_text:
                score += 0.1
        
        # Documentation indicators
        if repo.get('has_wiki') or 'documentation' in repo_text:
            score += 0.1
        
        # Jupyter notebooks (often educational)
        if repo.get('language') == 'Jupyter Notebook':
            score += 0.15
        
        # Good description (indicates effort)
        description = repo.get('description', '')
        if len(description) > 50:
            score += 0.1
        
        # Not too complex (reasonable size)
        size = repo.get('size', 0)
        if 100 < size < 50000:  # Sweet spot for learning projects
            score += 0.1
        
        return min(score, 1.0)
    
    def calculate_documentation_score(self, repo: Dict) -> float:
        """Estimate documentation quality."""
        score = 0.3  # Base score
        
        # Has README (basic requirement)
        # Most repos should have this, so we assume it exists
        score += 0.2
        
        # Has wiki
        if repo.get('has_wiki'):
            score += 0.2
        
        # Has homepage/documentation link
        if repo.get('homepage'):
            score += 0.2
        
        # Good description
        description = repo.get('description', '')
        if len(description) > 30:
            score += 0.1
            if len(description) > 100:
                score += 0.1
        
        # Language with good documentation culture
        lang = repo.get('language') or ''
        lang = lang.lower() if lang else ''
        if lang in ['python', 'javascript', 'typescript', 'java', 'c#']:
            score += 0.1
        
        return min(score, 1.0)
    
    def classify_repository_rule_based(self, repo: Dict, repo_text: str) -> str:
        """Classify repository using rule-based approach."""
        scores = {}
        
        for category, info in self.CATEGORIES.items():
            if category == 'Other':
                continue
                
            score = 0
            keywords = info['keywords']
            
            for keyword in keywords:
                if keyword in repo_text:
                    # Weight by keyword length (longer keywords are more specific)
                    weight = len(keyword.split())
                    score += weight
            
            scores[category] = score
        
        # Find best match
        if scores:
            best_category = max(scores, key=scores.get)
            if scores[best_category] > 0:
                return best_category
        
        return 'Other'
    
    def classify_repositories_with_embeddings(self) -> Dict[str, str]:
        """Classify repositories using sentence embeddings and clustering."""
        if not HAS_SENTENCE_TRANSFORMERS or not self.sentence_model:
            logger.info("Using rule-based classification")
            return self.classify_repositories_rule_based()
        
        logger.info("Generating embeddings for repositories...")
        
        # Create text representations
        repo_texts = [self.create_repo_text(repo) for repo in self.repositories]
        
        # Generate embeddings
        embeddings_cache = self.cache_dir / "embeddings.npy"
        if embeddings_cache.exists():
            logger.info("Loading cached embeddings...")
            self.embeddings = np.load(embeddings_cache)
        else:
            logger.info("Computing embeddings...")
            self.embeddings = self.sentence_model.encode(
                repo_texts, 
                show_progress_bar=True,
                batch_size=32
            )
            np.save(embeddings_cache, self.embeddings)
        
        # Create category embeddings
        category_texts = [info['description'] + ' ' + ' '.join(info['keywords']) 
                         for category, info in self.CATEGORIES.items() if category != 'Other']
        category_names = [cat for cat in self.CATEGORIES.keys() if cat != 'Other']
        category_embeddings = self.sentence_model.encode(category_texts)
        
        # Classify using similarity
        classifications = {}
        similarities = cosine_similarity(self.embeddings, category_embeddings)
        
        for i, repo in enumerate(self.repositories):
            best_category_idx = np.argmax(similarities[i])
            similarity_score = similarities[i][best_category_idx]
            
            # Use threshold for classification
            if similarity_score > 0.3:  # Tunable threshold
                classifications[repo['full_name']] = category_names[best_category_idx]
            else:
                classifications[repo['full_name']] = 'Other'
        
        return classifications
    
    def classify_repositories_rule_based(self) -> Dict[str, str]:
        """Classify repositories using rule-based approach only."""
        classifications = {}
        
        for repo in tqdm(self.repositories, desc="Classifying repositories"):
            repo_text = self.create_repo_text(repo)
            category = self.classify_repository_rule_based(repo, repo_text)
            classifications[repo['full_name']] = category
        
        return classifications
    
    def calculate_comprehensive_scores(self) -> Dict[str, Dict[str, float]]:
        """Calculate comprehensive scores for all repositories."""
        logger.info("Calculating comprehensive scores...")
        
        scores = {}
        
        for repo in tqdm(self.repositories, desc="Scoring repositories"):
            repo_text = self.create_repo_text(repo)
            
            # Calculate individual scores
            popularity = self.calculate_popularity_score(repo)
            freshness = self.calculate_freshness_score(repo)
            learning_value = self.calculate_learning_value_score(repo, repo_text)
            documentation = self.calculate_documentation_score(repo)
            
            # Calculate composite score
            composite = (
                popularity * 0.3 +
                freshness * 0.25 +
                learning_value * 0.25 +
                documentation * 0.2
            )
            
            scores[repo['full_name']] = {
                'popularity': popularity,
                'freshness': freshness,
                'learning_value': learning_value,
                'documentation': documentation,
                'composite': composite
            }
        
        return scores
    
    def generate_statistics(self, categorized_repos: Dict) -> Dict:
        """Generate comprehensive statistics."""
        stats = {
            'total_repositories': len(self.repositories),
            'categories': {},
            'top_languages': {},
            'activity_stats': {},
            'size_stats': {}
        }
        
        # Category statistics
        for category in self.CATEGORIES.keys():
            repos_in_category = [repo for repo in categorized_repos['repositories'] 
                               if repo['category'] == category]
            stats['categories'][category] = {
                'count': len(repos_in_category),
                'percentage': len(repos_in_category) / len(self.repositories) * 100,
                'avg_stars': np.mean([repo['stars'] for repo in repos_in_category]) if repos_in_category else 0,
                'total_stars': sum([repo['stars'] for repo in repos_in_category])
            }
        
        # Language statistics
        languages = {}
        for repo in self.repositories:
            lang = repo.get('language') or 'Unknown'
            languages[lang] = languages.get(lang, 0) + 1
        
        stats['top_languages'] = dict(sorted(languages.items(), 
                                           key=lambda x: x[1], 
                                           reverse=True)[:10])
        
        # Activity statistics
        now = datetime.now(timezone.utc)
        active_last_month = 0
        active_last_year = 0
        
        for repo in self.repositories:
            try:
                updated = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
                days_since = (now - updated).days
                
                if days_since <= 30:
                    active_last_month += 1
                if days_since <= 365:
                    active_last_year += 1
            except:
                continue
        
        stats['activity_stats'] = {
            'active_last_month': active_last_month,
            'active_last_year': active_last_year,
            'inactive_percentage': (len(self.repositories) - active_last_year) / len(self.repositories) * 100
        }
        
        # Size statistics
        sizes = [repo.get('size', 0) for repo in self.repositories]
        stats['size_stats'] = {
            'avg_size_kb': np.mean(sizes),
            'median_size_kb': np.median(sizes),
            'total_size_mb': sum(sizes) / 1024
        }
        
        return stats
    
    def analyze(self) -> Dict:
        """Main analysis function."""
        logger.info("Starting repository analysis...")
        
        # Load data
        if not self.load_repositories():
            raise Exception("Failed to load repository data")
        
        # Load models
        embedding_available = self.load_sentence_model()
        
        # Classify repositories
        if embedding_available:
            classifications = self.classify_repositories_with_embeddings()
        else:
            classifications = self.classify_repositories_rule_based()
        
        # Calculate scores
        scores = self.calculate_comprehensive_scores()
        
        # Combine data
        categorized_repos = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_repositories': len(self.repositories),
                'analysis_method': 'embeddings' if embedding_available else 'rule-based',
                'version': '1.0.0'
            },
            'repositories': []
        }
        
        for repo in self.repositories:
            full_name = repo['full_name']
            category = classifications.get(full_name, 'Other')
            repo_scores = scores.get(full_name, {})
            
            enhanced_repo = {
                **repo,
                'category': category,
                'scores': repo_scores,
                'analysis_text': self.create_repo_text(repo)
            }
            
            categorized_repos['repositories'].append(enhanced_repo)
        
        # Generate statistics
        stats = self.generate_statistics(categorized_repos)
        categorized_repos['statistics'] = stats
        
        # Sort repositories by composite score within each category
        categorized_repos['repositories'].sort(
            key=lambda x: (x['category'], -x['scores'].get('composite', 0))
        )
        
        logger.info("Analysis completed successfully!")
        return categorized_repos


@click.command()
@click.option('--input-file', '-i', 
              default='../data/starred_repos_latest.json',
              help='Input JSON file with repository data')
@click.option('--output-file', '-o',
              default='../data/categorized_repos.json',
              help='Output JSON file for categorized data')
@click.option('--cache-dir', '-c',
              default='../cache',
              help='Directory for caching models and embeddings')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
@click.option('--no-embeddings', is_flag=True,
              help='Use only rule-based classification (faster)')
def main(input_file: str, output_file: str, cache_dir: str, verbose: bool, no_embeddings: bool):
    """Analyze GitHub repositories using NLP techniques."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Resolve paths
    input_path = Path(__file__).parent / input_file
    output_path = Path(__file__).parent / output_file
    cache_path = Path(__file__).parent / cache_dir
    
    # Create output directory
    output_path.parent.mkdir(exist_ok=True)
    
    logger.info(f"Input file: {input_path}")
    logger.info(f"Output file: {output_path}")
    logger.info(f"Cache directory: {cache_path}")
    
    if no_embeddings:
        logger.info("Embeddings disabled - using rule-based classification only")
        global HAS_SENTENCE_TRANSFORMERS, HAS_TRANSFORMERS
        HAS_SENTENCE_TRANSFORMERS = False
        HAS_TRANSFORMERS = False
    
    try:
        # Initialize analyzer
        analyzer = RepositoryAnalyzer(input_path, cache_path)
        
        # Run analysis
        results = analyzer.analyze()
        
        # Save results
        logger.info(f"Saving results to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Print summary
        stats = results['statistics']
        print("\n" + "="*60)
        print("REPOSITORY ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total Repositories: {stats['total_repositories']}")
        print(f"Analysis Method: {results['metadata']['analysis_method']}")
        print(f"Date: {results['metadata']['analysis_date']}")
        
        print("\nCategory Distribution:")
        for category, info in stats['categories'].items():
            if info['count'] > 0:
                print(f"  {category}: {info['count']} repos ({info['percentage']:.1f}%)")
        
        print(f"\nTop Languages:")
        for lang, count in list(stats['top_languages'].items())[:5]:
            percentage = count / stats['total_repositories'] * 100
            print(f"  {lang}: {count} repos ({percentage:.1f}%)")
        
        print(f"\nActivity Stats:")
        print(f"  Active last month: {stats['activity_stats']['active_last_month']}")
        print(f"  Active last year: {stats['activity_stats']['active_last_year']}")
        print(f"  Inactive: {stats['activity_stats']['inactive_percentage']:.1f}%")
        
        print("\nTop Repositories by Category:")
        for category in RepositoryAnalyzer.CATEGORIES.keys():
            category_repos = [r for r in results['repositories'] if r['category'] == category]
            if category_repos:
                top_repo = category_repos[0]
                score = top_repo['scores'].get('composite', 0)
                print(f"  {category}: {top_repo['name']} (score: {score:.3f})")
        
        print(f"\nResults saved to: {output_path}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise click.ClickException(f"Analysis failed: {e}")


if __name__ == '__main__':
    main()