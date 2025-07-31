# Advanced Repository Analysis System

A sophisticated NLP-powered system for analyzing and categorizing GitHub repositories using machine learning techniques.

## Features

### 🧠 Intelligent Categorization
- **AI-Powered Classification**: Uses sentence transformers and embeddings for semantic understanding
- **Rule-Based Fallback**: Robust keyword-based classification when ML models unavailable
- **13+ Categories**: Specialized categories for different AI/ML domains:
  - LLMs & Foundation Models
  - Computer Vision
  - Natural Language Processing
  - MLOps & Infrastructure
  - Data Science & Analytics
  - Machine Learning Frameworks
  - Educational Resources
  - Research Papers & Implementations
  - Developer Tools & APIs
  - Reinforcement Learning
  - Audio & Speech
  - Time Series & Forecasting
  - Multimodal AI

### 📊 Multi-Factor Scoring System
- **Popularity Score**: Based on stars, forks, watchers with logarithmic scaling
- **Freshness Score**: Recent activity and maintenance status
- **Learning Value Score**: Beginner-friendliness and educational content
- **Documentation Score**: Quality of documentation and examples
- **Composite Score**: Weighted combination optimized for learning value

### 🚀 Performance & Reliability
- **Two Analysis Modes**: Fast rule-based mode (~30s) or full AI mode (~5-10min)
- **Intelligent Caching**: Models and embeddings cached for subsequent runs
- **Robust Error Handling**: Graceful degradation when dependencies unavailable
- **Production Ready**: Comprehensive logging, CLI interface, progress tracking

## Quick Start

### 1. Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x run_analysis.sh
chmod +x tools/analyze_repos.py
```

### 2. Run Analysis
```bash
# Interactive mode - choose fast or full analysis
./run_analysis.sh

# Or run directly:
cd tools/
python analyze_repos.py --help
python analyze_repos.py --no-embeddings  # Fast mode
python analyze_repos.py                  # Full mode with AI
```

### 3. Results
- **Categorized Data**: `data/categorized_repos.json`
- **Analysis Log**: `tools/analyze_repos.log`  
- **Statistics**: Included in JSON output

## System Architecture

### Core Components

#### `analyze_repos.py`
Main analysis engine with the following classes and functions:

- **RepositoryAnalyzer**: Core analysis class
  - `load_repositories()`: Data loading and validation
  - `classify_repositories_*()`: Multi-modal classification
  - `calculate_*_score()`: Scoring algorithms
  - `generate_statistics()`: Comprehensive analytics

#### `test_analyzer.py` 
Test suite for validation:
- Basic functionality tests
- Sample analysis verification
- Error handling validation

#### `run_analysis.sh`
Interactive runner script:
- Dependency checking
- Mode selection
- Progress monitoring
- Result validation

### Data Flow

```
starred_repos_latest.json 
    ↓
[Load & Preprocess]
    ↓
[Text Processing & Feature Extraction]
    ↓
[Classification: Rule-based / AI Embeddings]
    ↓
[Multi-Factor Scoring]
    ↓
[Statistics & Analytics]
    ↓
categorized_repos.json
```

### Classification Methods

#### Method 1: Rule-Based Classification
- **Speed**: ~30 seconds for 650+ repos
- **Dependencies**: None (built-in)
- **Accuracy**: Good for clear-cut categories
- **Process**:
  1. Extract text from name, description, language, topics
  2. Match against keyword dictionaries
  3. Weight matches by keyword specificity
  4. Assign to highest-scoring category

#### Method 2: AI Embeddings
- **Speed**: ~5-10 minutes for 650+ repos (first run)
- **Dependencies**: sentence-transformers, torch
- **Accuracy**: Excellent semantic understanding
- **Process**:
  1. Generate sentence embeddings using `all-MiniLM-L6-v2`
  2. Create category embeddings from descriptions
  3. Calculate cosine similarity
  4. Assign based on similarity threshold

### Scoring Algorithms

#### Popularity Score (30% weight)
```python
star_score = log10(stars + 1) / log10(100000)
fork_ratio = forks / max(stars, 1)  
watcher_score = log10(watchers + 1) / log10(10000)
popularity = star_score * 0.6 + fork_ratio * 0.2 + watcher_score * 0.2
```

#### Freshness Score (25% weight)
```python
days_since_activity = min(days_since_update, days_since_push)
if days_since_activity <= 7: freshness = 1.0
elif days_since_activity <= 30: freshness = 0.8
elif days_since_activity <= 90: freshness = 0.6
# ... with bonuses for new active projects
```

#### Learning Value Score (25% weight)
- Educational keywords detection
- Jupyter notebook bonus
- Documentation indicators
- Reasonable complexity assessment

#### Documentation Score (20% weight) 
- README presence assumption
- Wiki availability
- Homepage/docs links
- Description quality
- Language documentation culture

## Output Format

### JSON Structure
```json
{
  "metadata": {
    "analysis_date": "2025-07-30T19:40:14.123456",
    "total_repositories": 645,
    "analysis_method": "embeddings|rule-based",
    "version": "1.0.0"
  },
  "repositories": [
    {
      "name": "repo-name",
      "full_name": "owner/repo-name", 
      "category": "LLMs & Foundation Models",
      "scores": {
        "popularity": 0.795,
        "freshness": 1.000,
        "learning_value": 0.850,
        "documentation": 0.800,
        "composite": 0.861
      },
      "stars": 13384,
      "description": "...",
      "analysis_text": "processed text for analysis",
      // ... other GitHub API fields
    }
  ],
  "statistics": {
    "total_repositories": 645,
    "categories": {
      "LLMs & Foundation Models": {
        "count": 156,
        "percentage": 24.2,
        "avg_stars": 8932.1,
        "total_stars": 1393410
      }
      // ... other categories
    },
    "top_languages": {
      "Python": 198,
      "Jupyter Notebook": 87,
      "JavaScript": 45
      // ... other languages  
    },
    "activity_stats": {
      "active_last_month": 234,
      "active_last_year": 456,
      "inactive_percentage": 29.3
    }
  }
}
```

## Advanced Usage

### CLI Options
```bash
python analyze_repos.py [OPTIONS]

Options:
  -i, --input-file TEXT   Input JSON file path (default: ../data/starred_repos_latest.json)
  -o, --output-file TEXT  Output JSON file path (default: ../data/categorized_repos.json)  
  -c, --cache-dir TEXT    Cache directory for models (default: ../cache)
  -v, --verbose           Enable detailed logging
  --no-embeddings         Use only rule-based classification (faster)
  --help                  Show help message
```

### Custom Categories
To add new categories, edit the `CATEGORIES` dictionary in `analyze_repos.py`:

```python
CATEGORIES = {
    'Your New Category': {
        'keywords': ['keyword1', 'keyword2', 'multi word keyword'],
        'description': 'Description for embedding similarity'
    }
}
```

### Performance Tuning

#### For Speed:
```bash
# Use rule-based mode only
python analyze_repos.py --no-embeddings

# Reduce batch size for embeddings
# Edit line ~398: batch_size=16  # Instead of 32
```

#### For Accuracy:
```bash
# Use full embedding mode
python analyze_repos.py

# Adjust similarity threshold
# Edit line ~417: if similarity_score > 0.2  # Lower threshold
```

### Caching System
- **Models**: `cache/sentence_model.pkl` (~150MB)
- **Embeddings**: `cache/embeddings.npy` (~3MB for 650 repos)
- **Cache Persistence**: Survives across runs, cleared by deleting cache directory

## Troubleshooting

### Common Issues

#### "sentence-transformers not available"
```bash
pip install sentence-transformers torch
```

#### "Failed to load repositories"
```bash
# Check if data file exists
ls -la data/starred_repos_latest.json

# Run fetch_stars.py first if missing
cd tools && python fetch_stars.py
```

#### "Analysis failed with NoneType error"
- Fixed in v1.0+ with robust null handling
- Update to latest version if using older code

#### "Out of memory during embedding generation"
```bash
# Reduce batch size in analyze_repos.py line ~398
batch_size=8  # Instead of 32
```

### Performance Benchmarks
- **Rule-based mode**: ~30 seconds for 645 repos
- **Full AI mode**: ~5-10 minutes first run, ~2-3 minutes subsequent
- **Memory usage**: ~2GB peak with embeddings, ~200MB rule-based
- **Disk usage**: ~500MB for models and cache

## Testing

### Test Suite
```bash
cd tools/
python test_analyzer.py
```

Tests include:
- Data loading validation
- Text processing verification  
- Scoring algorithm accuracy
- Classification correctness
- Error handling robustness

### Sample Analysis
Test with first 10 repositories:
```bash
# Integrated into test_analyzer.py
python test_analyzer.py
```

## Integration

### With Other Tools
```python
from analyze_repos import RepositoryAnalyzer

# Initialize analyzer
analyzer = RepositoryAnalyzer('data/repos.json', 'cache/')

# Run analysis
results = analyzer.analyze()

# Access results
for repo in results['repositories']:
    print(f"{repo['name']}: {repo['category']} (score: {repo['scores']['composite']:.3f})")
```

### Data Pipeline
1. **Fetch**: `fetch_stars.py` → `starred_repos_latest.json`
2. **Analyze**: `analyze_repos.py` → `categorized_repos.json` 
3. **Generate**: `generate_markdown.py` → Category pages
4. **Deploy**: Static site generation

## Contributing

### Adding New Features
1. **New Categories**: Edit `CATEGORIES` dictionary
2. **New Scores**: Add methods following `calculate_*_score()` pattern
3. **New Classification**: Implement in `classify_repositories_*()` methods

### Code Style
- Follow existing patterns and naming conventions
- Add comprehensive error handling
- Include progress bars for long operations
- Add logging for debugging
- Write tests for new functionality

## Version History

### v1.0.0 (2025-07-30)
- Initial release with full NLP analysis
- 13 predefined categories
- Multi-factor scoring system
- AI embeddings with rule-based fallback
- Comprehensive CLI interface
- Production-ready error handling
- Caching system for performance
- Full test suite

---

## License

This project is part of the awesome-ai-learning repository. See main repository for license information.

## Support

For issues, feature requests, or questions:
1. Check the troubleshooting section above
2. Run the test suite to validate your environment
3. Check log files for detailed error information
4. Review the code documentation for implementation details