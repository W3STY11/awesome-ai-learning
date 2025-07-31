#!/usr/bin/env python3
"""
generate_markdown.py - Beautiful Markdown Generator for AI Learning Repositories

Generates stunning markdown documentation from categorized repository data including:
- Main README with overview and navigation
- Individual category pages with top repositories
- Beginner guide with learning paths
- Language-specific collections
- Top repositories ranking
- Comprehensive index and sitemap

Author: Claude Code Assistant
Version: 1.0.0
"""

import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from dataclasses import dataclass
from urllib.parse import quote
import re


@dataclass
class RepositoryData:
    """Structured repository data"""
    name: str
    full_name: str
    owner: str
    description: str
    url: str
    stars: int
    forks: int
    language: str
    category: str
    scores: Dict[str, float]
    updated_at: str
    created_at: str
    has_readme: bool
    is_ai_ml_related: bool
    readme_preview: str = ""
    homepage: str = ""
    license: str = ""
    topics: List[str] = None

    def __post_init__(self):
        if self.topics is None:
            self.topics = []


class MarkdownGenerator:
    """Main markdown generator class"""
    
    # Category emojis and descriptions
    CATEGORY_INFO = {
        'Natural Language Processing': {
            'emoji': '📝',
            'description': 'Advanced text processing, language models, and NLP frameworks',
            'learning_path': ['Tokenization', 'Language Models', 'Text Classification', 'Named Entity Recognition', 'Sentiment Analysis']
        },
        'Computer Vision': {
            'emoji': '👁️',
            'description': 'Image processing, object detection, and visual AI applications',
            'learning_path': ['Image Processing', 'CNN Architectures', 'Object Detection', 'Image Segmentation', 'Generative Models']
        },
        'Machine Learning': {
            'emoji': '🤖', 
            'description': 'Core ML algorithms, frameworks, and general-purpose AI tools',
            'learning_path': ['Supervised Learning', 'Unsupervised Learning', 'Deep Learning', 'Model Evaluation', 'Hyperparameter Tuning']
        },
        'Deep Learning': {
            'emoji': '🧠',
            'description': 'Neural networks, deep architectures, and advanced AI models',
            'learning_path': ['Neural Networks', 'Backpropagation', 'CNN/RNN/Transformers', 'Transfer Learning', 'Model Optimization']
        },
        'Data Science': {
            'emoji': '📊',
            'description': 'Data analysis, visualization, and scientific computing tools',
            'learning_path': ['Data Wrangling', 'Exploratory Analysis', 'Statistical Modeling', 'Data Visualization', 'Big Data Tools']
        },
        'Reinforcement Learning': {
            'emoji': '🎮',
            'description': 'RL algorithms, environments, and agent-based learning systems',
            'learning_path': ['Q-Learning', 'Policy Gradients', 'Actor-Critic', 'Multi-Agent RL', 'Advanced RL']
        },
        'Audio & Speech': {
            'emoji': '🎵',
            'description': 'Speech recognition, audio processing, and voice synthesis',
            'learning_path': ['Audio Processing', 'Speech Recognition', 'Voice Synthesis', 'Music AI', 'Audio Analysis']
        },
        'Robotics': {
            'emoji': '🤖',
            'description': 'Robotic systems, control algorithms, and embodied AI',
            'learning_path': ['Robot Kinematics', 'Control Systems', 'SLAM', 'Path Planning', 'Robot Learning']
        },
        'MLOps': {
            'emoji': '⚙️',
            'description': 'ML operations, deployment, monitoring, and production systems',
            'learning_path': ['Model Deployment', 'CI/CD for ML', 'Model Monitoring', 'A/B Testing', 'MLOps Platforms']
        },
        'Generative AI': {
            'emoji': '✨',
            'description': 'AI content generation, GANs, and creative AI applications',
            'learning_path': ['GANs', 'VAEs', 'Diffusion Models', 'Text Generation', 'Creative AI']
        },
        'Time Series': {
            'emoji': '📈',
            'description': 'Time series analysis, forecasting, and temporal data modeling',
            'learning_path': ['Time Series Basics', 'ARIMA Models', 'Neural Forecasting', 'Anomaly Detection', 'Real-time Processing']
        },
        'Optimization': {
            'emoji': '🎯',
            'description': 'Mathematical optimization, hyperparameter tuning, and search algorithms',
            'learning_path': ['Linear Programming', 'Gradient Descent', 'Evolutionary Algorithms', 'Bayesian Optimization', 'Multi-objective Optimization']
        },
        'Quantum Computing': {
            'emoji': '⚛️',
            'description': 'Quantum algorithms, quantum machine learning, and quantum computing frameworks',
            'learning_path': ['Quantum Basics', 'Quantum Gates', 'Quantum Algorithms', 'Quantum ML', 'Quantum Frameworks']
        },
        'Other': {
            'emoji': '🔧',
            'description': 'Miscellaneous AI tools, utilities, and specialized applications',
            'learning_path': ['Tool Selection', 'Integration Patterns', 'Best Practices', 'Community Resources', 'Emerging Technologies']
        }
    }
    
    def __init__(self, data_file: str, output_dir: str):
        """Initialize generator with data file and output directory"""
        self.data_file = Path(data_file)
        self.output_dir = Path(output_dir)
        self.repositories: List[RepositoryData] = []
        self.categories: Dict[str, List[RepositoryData]] = {}
        self.languages: Dict[str, List[RepositoryData]] = {}
        self.metadata: Dict = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('markdown_generation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_data(self) -> None:
        """Load and parse repository data"""
        try:
            self.logger.info(f"Loading data from {self.data_file}")
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metadata = data.get('metadata', {})
            repos_data = data.get('repositories', [])
            
            # Convert to structured data
            for repo_data in repos_data:
                try:
                    repo = RepositoryData(
                        name=repo_data.get('name', ''),
                        full_name=repo_data.get('full_name', ''),
                        owner=repo_data.get('owner', ''),
                        description=repo_data.get('description', ''),
                        url=repo_data.get('url', ''),
                        stars=repo_data.get('stars', 0),
                        forks=repo_data.get('forks', 0),
                        language=repo_data.get('language', 'Unknown'),
                        category=repo_data.get('category', 'Other'),
                        scores=repo_data.get('scores', {}),
                        updated_at=repo_data.get('updated_at', ''),
                        created_at=repo_data.get('created_at', ''),
                        has_readme=repo_data.get('has_readme', False),
                        is_ai_ml_related=repo_data.get('is_ai_ml_related', False),
                        readme_preview=repo_data.get('readme_preview', ''),
                        homepage=repo_data.get('homepage', ''),
                        license=repo_data.get('license', ''),
                        topics=repo_data.get('topics', [])
                    )
                    self.repositories.append(repo)
                except Exception as e:
                    self.logger.warning(f"Failed to parse repository {repo_data.get('name', 'unknown')}: {e}")
            
            # Organize by categories and languages
            self._organize_data()
            self.logger.info(f"Loaded {len(self.repositories)} repositories across {len(self.categories)} categories")
            
        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            raise
    
    def _organize_data(self) -> None:
        """Organize repositories by categories and languages"""
        self.categories = {}
        self.languages = {}
        
        for repo in self.repositories:
            # Group by category
            if repo.category not in self.categories:
                self.categories[repo.category] = []
            self.categories[repo.category].append(repo)
            
            # Group by language
            lang = repo.language or 'Unknown'
            if lang not in self.languages:
                self.languages[lang] = []
            self.languages[lang].append(repo)
        
        # Sort repositories within each category by composite score
        for category in self.categories:
            self.categories[category].sort(
                key=lambda x: x.scores.get('composite', 0), 
                reverse=True
            )
        
        # Sort repositories within each language by stars
        for language in self.languages:
            self.languages[language].sort(
                key=lambda x: x.stars, 
                reverse=True
            )
    
    def _create_shields_badge(self, label: str, message: str, color: str = "blue") -> str:
        """Create shields.io badge URL"""
        label_encoded = quote(label)
        message_encoded = quote(str(message))
        return f"![{label}](https://img.shields.io/badge/{label_encoded}-{message_encoded}-{color})"
    
    def _format_number(self, num: int) -> str:
        """Format large numbers with K/M suffixes"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        return str(num)
    
    def _get_score_bar(self, score: float) -> str:
        """Generate ASCII progress bar for scores"""
        filled = int(score * 10)
        empty = 10 - filled
        return f"{'█' * filled}{'░' * empty} {score:.2f}"
    
    def _get_difficulty_badge(self, repo: RepositoryData) -> str:
        """Determine difficulty level and return appropriate badge"""
        # Simple heuristic based on various factors
        learning_score = repo.scores.get('learning_value', 0.5)
        has_good_docs = repo.scores.get('documentation', 0.5) > 0.6
        is_popular = repo.stars > 1000
        
        if learning_score > 0.8 and has_good_docs and repo.has_readme:
            return self._create_shields_badge("Difficulty", "Beginner", "green")
        elif learning_score > 0.6 and (has_good_docs or is_popular):
            return self._create_shields_badge("Difficulty", "Intermediate", "yellow")
        else:
            return self._create_shields_badge("Difficulty", "Advanced", "red")
    
    def _get_activity_badge(self, repo: RepositoryData) -> str:
        """Get activity level badge based on freshness score"""
        freshness = repo.scores.get('freshness', 0.5)
        if freshness > 0.8:
            return self._create_shields_badge("Activity", "Very Active", "brightgreen")
        elif freshness > 0.6:
            return self._create_shields_badge("Activity", "Active", "green")
        elif freshness > 0.4:
            return self._create_shields_badge("Activity", "Moderate", "yellow")
        else:
            return self._create_shields_badge("Activity", "Low", "red")
    
    def generate_main_readme(self) -> None:
        """Generate main README.md file"""
        self.logger.info("Generating main README.md")
        
        content = f"""# 🚀 Awesome AI Learning Repository Collection

> A curated collection of {len(self.repositories)} high-quality AI and Machine Learning repositories, automatically categorized and scored for learning value.

{self._create_shields_badge("Repositories", len(self.repositories), "blue")} {self._create_shields_badge("Categories", len(self.categories), "green")} {self._create_shields_badge("Languages", len(self.languages), "purple")} {self._create_shields_badge("Last Updated", self.metadata.get('analysis_date', '2024')[:10], "orange")}

---

## 📚 Quick Navigation

### 🎯 **[🔰 Beginner's Guide](BEGINNER_GUIDE.md)** - Start your AI learning journey here!
### 🏆 **[📊 Top 50 Repositories](TOP_REPOSITORIES.md)** - The best of the best
### 🗂️ **[📋 Complete Index](INDEX.md)** - Browse all repositories

---

## 🎨 Categories Overview

"""
        
        # Add category overview with stats
        for category, repos in sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True):
            if category in self.CATEGORY_INFO:
                emoji = self.CATEGORY_INFO[category]['emoji']
                description = self.CATEGORY_INFO[category]['description']
            else:
                emoji = '🔧'
                description = 'Specialized AI tools and applications'
            
            top_repo = repos[0] if repos else None
            avg_stars = sum(r.stars for r in repos) // len(repos) if repos else 0
            
            content += f"""### {emoji} [{category}](categories/{category.lower().replace(' ', '_').replace('&', 'and')}.md)

{description}

- **{len(repos)} repositories** | **Avg {self._format_number(avg_stars)} stars**
- **Top repository:** [{top_repo.name}]({top_repo.url}) ({self._format_number(top_repo.stars)} ⭐)

"""
        
        # Add language stats
        content += f"""---

## 💻 Programming Languages

"""
        
        top_languages = sorted(self.languages.items(), key=lambda x: len(x[1]), reverse=True)[:8]
        for lang, repos in top_languages:
            if lang != 'Unknown':
                total_stars = sum(r.stars for r in repos)
                content += f"**{lang}**: {len(repos)} repos ({self._format_number(total_stars)} total ⭐) | "
        
        content = content.rstrip(" | ") + "\n\n"
        
        # Add learning paths
        content += f"""---

## 🎓 Learning Paths

Choose your adventure based on your interests and experience level:

### 🟢 **Beginner Path**
1. **[Data Science](categories/data_science.md)** - Start with data manipulation and visualization
2. **[Machine Learning](categories/machine_learning.md)** - Learn core ML concepts and algorithms  
3. **[Deep Learning](categories/deep_learning.md)** - Dive into neural networks

### 🟡 **Intermediate Path**
1. **[Computer Vision](categories/computer_vision.md)** - Image processing and visual AI
2. **[Natural Language Processing](categories/natural_language_processing.md)** - Text processing and language models
3. **[MLOps](categories/mlops.md)** - Production ML systems

### 🔴 **Advanced Path**
1. **[Reinforcement Learning](categories/reinforcement_learning.md)** - Agent-based learning
2. **[Generative AI](categories/generative_ai.md)** - Creative AI and content generation
3. **[Quantum Computing](categories/quantum_computing.md)** - Next-generation computing

---

## 📊 Repository Statistics

| Metric | Value |
|--------|-------|
| Total Repositories | {len(self.repositories)} |
| Average Stars | {self._format_number(sum(r.stars for r in self.repositories) // len(self.repositories))} |
| Total Stars | {self._format_number(sum(r.stars for r in self.repositories))} |
| Most Popular Language | {max(self.languages.items(), key=lambda x: len(x[1]))[0]} ({len(max(self.languages.items(), key=lambda x: len(x[1]))[1])} repos) |
| Newest Repository | {max(self.repositories, key=lambda x: x.created_at).name} |
| Most Active | {max(self.repositories, key=lambda x: x.scores.get('freshness', 0)).name} |

---

## 🤝 Contributing

This collection is automatically curated and updated. To suggest repositories or improvements:

1. **Star interesting repositories** - They'll be automatically discovered
2. **Submit issues** for manual additions or corrections
3. **Contribute to scoring algorithms** to improve categorization

---

## 📝 Methodology

Repositories are automatically:
- **Discovered** from starred collections and AI-related topics
- **Categorized** using intelligent rule-based classification
- **Scored** on multiple dimensions:
  - 🌟 **Popularity**: Stars, forks, and community engagement
  - 🔄 **Freshness**: Recent updates and maintenance activity  
  - 📚 **Learning Value**: Documentation quality and educational content
  - 📊 **Composite Score**: Weighted combination of all factors

---

## 📈 Updates

- **Last Analysis**: {self.metadata.get('analysis_date', 'Unknown')[:19]}
- **Analysis Method**: {self.metadata.get('analysis_method', 'Unknown')}
- **Version**: {self.metadata.get('version', 'Unknown')}

Generated with ❤️ by AI-powered curation system.

---

*Happy Learning! 🚀*
"""
        
        # Write to file
        output_file = self.output_dir / "README.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Main README generated: {output_file}")
    
    def generate_category_pages(self) -> None:
        """Generate individual category pages"""
        self.logger.info("Generating category pages")
        
        categories_dir = self.output_dir / "categories"
        categories_dir.mkdir(parents=True, exist_ok=True)
        
        for category, repos in self.categories.items():
            if not repos:
                continue
                
            # Generate filename
            filename = category.lower().replace(' ', '_').replace('&', 'and') + '.md'
            
            # Get category info
            category_info = self.CATEGORY_INFO.get(category, {
                'emoji': '🔧',
                'description': 'Specialized AI tools and applications',
                'learning_path': ['Basics', 'Intermediate', 'Advanced', 'Expert', 'Research']
            })
            
            content = f"""# {category_info['emoji']} {category}

{category_info['description']}

{self._create_shields_badge("Repositories", len(repos), "blue")} {self._create_shields_badge("Total Stars", self._format_number(sum(r.stars for r in repos)), "yellow")} {self._create_shields_badge("Avg Score", f"{sum(r.scores.get('composite', 0) for r in repos) / len(repos):.2f}", "green")}

---

## 📊 Category Statistics

| Metric | Value |
|--------|--------|
| Total Repositories | {len(repos)} |
| Total Stars | {self._format_number(sum(r.stars for r in repos))} |
| Average Stars | {self._format_number(sum(r.stars for r in repos) // len(repos))} |
| Top Language | {max(set(r.language for r in repos), key=lambda x: sum(1 for r in repos if r.language == x))} |
| Avg Composite Score | {sum(r.scores.get('composite', 0) for r in repos) / len(repos):.3f} |
| Active Repositories | {sum(1 for r in repos if r.scores.get('freshness', 0) > 0.6)} |

---

## 🎓 Learning Path

Master {category.lower()} by following this progression:

"""
            
            for i, step in enumerate(category_info['learning_path'], 1):
                content += f"{i}. **{step}**\n"
            
            content += f"""
---

## 🏆 Top Repositories

Here are the highest-rated repositories in this category:

"""
            
            # Show top 20 repositories
            top_repos = repos[:20]
            
            for i, repo in enumerate(top_repos, 1):
                # Repository header with ranking
                content += f"""### {i}. [{repo.name}]({repo.url}) 

**{repo.owner}** | {self._create_shields_badge("⭐", self._format_number(repo.stars), "yellow")} {self._create_shields_badge("Language", repo.language, "blue")} {self._get_activity_badge(repo)} {self._get_difficulty_badge(repo)}

{repo.description}

**Scores:**
- Popularity: {self._get_score_bar(repo.scores.get('popularity', 0))}
- Freshness: {self._get_score_bar(repo.scores.get('freshness', 0))}
- Learning Value: {self._get_score_bar(repo.scores.get('learning_value', 0))}
- Documentation: {self._get_score_bar(repo.scores.get('documentation', 0))}
- **Composite: {self._get_score_bar(repo.scores.get('composite', 0))}**

"""
                
                # Add additional info if available
                if repo.homepage:
                    content += f"🏠 **Homepage:** [{repo.homepage}]({repo.homepage})\n\n"
                if repo.license:
                    content += f"📄 **License:** {repo.license}\n\n"
                if repo.topics:
                    topics_str = " ".join([f"`{topic}`" for topic in repo.topics[:5]])
                    content += f"🏷️ **Topics:** {topics_str}\n\n"
                
                content += "---\n\n"
            
            # Add more repositories if there are any
            if len(repos) > 20:
                content += f"""
## 📚 More Repositories

This category contains {len(repos) - 20} additional repositories. [View the complete index](../INDEX.md#{category.lower().replace(' ', '-').replace('&', 'and')}) to see all repositories.

"""
            
            # Add navigation
            content += f"""
---

## 🧭 Navigation

- [🏠 Main README](../README.md)
- [🔰 Beginner's Guide](../BEGINNER_GUIDE.md) 
- [🏆 Top 50 Repositories](../TOP_REPOSITORIES.md)
- [📋 Complete Index](../INDEX.md)

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | AI-powered curation*
"""
            
            # Write category page
            output_file = categories_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Generated category page: {output_file}")
    
    def generate_beginner_guide(self) -> None:
        """Generate beginner's guide with learning paths"""
        self.logger.info("Generating beginner's guide")
        
        content = f"""# 🔰 Beginner's Guide to AI & Machine Learning

Welcome to your AI learning journey! This guide will help you navigate through {len(self.repositories)} carefully curated repositories to build your skills progressively.

{self._create_shields_badge("Difficulty", "Beginner Friendly", "green")} {self._create_shields_badge("Learning Path", "Structured", "blue")} {self._create_shields_badge("Resources", f"{len([r for r in self.repositories if r.scores.get('learning_value', 0) > 0.7])}", "purple")}

---

## 🎯 Before You Start

### Prerequisites
- **Programming Experience**: Basic familiarity with Python (most repositories use Python)
- **Math Background**: High school math is sufficient to start
- **Time Commitment**: Plan for 2-4 hours per week consistently
- **Environment**: Set up Python, Jupyter notebooks, and Git

### Essential Tools
1. **Python 3.8+** - The lingua franca of AI/ML
2. **Jupyter Notebooks** - Interactive development environment
3. **Git** - Version control for code
4. **Anaconda/Miniconda** - Package management
5. **VS Code or PyCharm** - Code editor with AI extensions

---

## 🚀 Learning Path: Zero to AI Hero

### Phase 1: Foundation (Weeks 1-4)
**Goal**: Understand data manipulation and basic statistics

#### 🎯 Start Here - Data Science Essentials

"""
        
        # Get beginner-friendly data science repos
        data_science_repos = self.categories.get('Data Science', [])
        beginner_ds = [r for r in data_science_repos if r.scores.get('learning_value', 0) > 0.7][:5]
        
        for repo in beginner_ds:
            content += f"""**[{repo.name}]({repo.url})** {self._get_difficulty_badge(repo)}
- {repo.description}
- ⭐ {self._format_number(repo.stars)} stars | 📚 Learning Value: {repo.scores.get('learning_value', 0):.2f}

"""
        
        content += f"""
**Learning Objectives:**
- [ ] Master pandas for data manipulation
- [ ] Create visualizations with matplotlib/seaborn
- [ ] Understand descriptive statistics
- [ ] Work with different data formats (CSV, JSON, etc.)
- [ ] Complete 3-5 data analysis projects

---

### Phase 2: Machine Learning Basics (Weeks 5-8)
**Goal**: Understand core ML concepts and algorithms

#### 🤖 Machine Learning Fundamentals

"""
        
        # Get beginner-friendly ML repos
        ml_repos = self.categories.get('Machine Learning', [])
        beginner_ml = [r for r in ml_repos if r.scores.get('learning_value', 0) > 0.7][:5]
        
        for repo in beginner_ml:
            content += f"""**[{repo.name}]({repo.url})** {self._get_difficulty_badge(repo)}
- {repo.description}
- ⭐ {self._format_number(repo.stars)} stars | 📚 Learning Value: {repo.scores.get('learning_value', 0):.2f}

"""
        
        content += f"""
**Learning Objectives:**
- [ ] Understand supervised vs unsupervised learning
- [ ] Implement linear regression and classification
- [ ] Learn model evaluation techniques
- [ ] Master scikit-learn library
- [ ] Build your first ML project end-to-end

---

### Phase 3: Deep Learning Introduction (Weeks 9-12)
**Goal**: Neural networks and deep learning frameworks

#### 🧠 Deep Learning Fundamentals

"""
        
        # Get beginner-friendly deep learning repos
        dl_repos = self.categories.get('Deep Learning', [])
        beginner_dl = [r for r in dl_repos if r.scores.get('learning_value', 0) > 0.6][:5]
        
        for repo in beginner_dl:
            content += f"""**[{repo.name}]({repo.url})** {self._get_difficulty_badge(repo)}
- {repo.description}
- ⭐ {self._format_number(repo.stars)} stars | 📚 Learning Value: {repo.scores.get('learning_value', 0):.2f}

"""
        
        content += f"""
**Learning Objectives:**
- [ ] Understand neural network basics
- [ ] Learn TensorFlow or PyTorch
- [ ] Build simple neural networks
- [ ] Understand backpropagation
- [ ] Create an image classifier

---

### Phase 4: Specialization (Weeks 13-16)
**Goal**: Choose your focus area and dive deeper

#### 🎨 Choose Your Specialization:

##### 👁️ Computer Vision Track
Perfect for: Image processing, medical imaging, autonomous vehicles

**Top Beginner Resources:**
"""
        
        cv_repos = self.categories.get('Computer Vision', [])
        beginner_cv = [r for r in cv_repos if r.scores.get('learning_value', 0) > 0.6][:3]
        
        for repo in beginner_cv:
            content += f"- **[{repo.name}]({repo.url})** - {repo.description[:100]}...\n"
        
        content += f"""

##### 📝 Natural Language Processing Track  
Perfect for: Chatbots, text analysis, language translation

**Top Beginner Resources:**
"""
        
        nlp_repos = self.categories.get('Natural Language Processing', [])
        beginner_nlp = [r for r in nlp_repos if r.scores.get('learning_value', 0) > 0.6][:3]
        
        for repo in beginner_nlp:
            content += f"- **[{repo.name}]({repo.url})** - {repo.description[:100]}...\n"
        
        content += f"""

##### 🎮 Reinforcement Learning Track
Perfect for: Game AI, robotics, optimization

**Top Beginner Resources:**
"""
        
        rl_repos = self.categories.get('Reinforcement Learning', [])
        beginner_rl = [r for r in rl_repos if r.scores.get('learning_value', 0) > 0.6][:3]
        
        for repo in beginner_rl:
            content += f"- **[{repo.name}]({repo.url})** - {repo.description[:100]}...\n"
        
        content += f"""

---

## 💡 Learning Tips & Best Practices

### 🎯 Effective Learning Strategies

1. **Practice-First Approach**
   - Clone repositories and run examples
   - Modify code to see what happens
   - Don't just read - implement!

2. **Project-Based Learning**
   - Build real projects, not just tutorials  
   - Start small, iterate and improve
   - Share your work on GitHub

3. **Community Engagement**
   - Join AI/ML communities (Reddit, Discord, Stack Overflow)
   - Attend local meetups or online events
   - Follow researchers and practitioners on Twitter

4. **Consistent Schedule**
   - Better to study 30 minutes daily than 4 hours once a week
   - Set specific, measurable goals
   - Track your progress

### 🚫 Common Beginner Mistakes

- **Jumping too quickly to advanced topics** - Master the basics first
- **Only following tutorials** - Build original projects
- **Ignoring math foundations** - Understand the underlying concepts
- **Not practicing regularly** - Consistency beats intensity
- **Working in isolation** - Join communities and collaborate

---

## 📚 Essential Learning Resources

### 📖 Books for Beginners
- **"Hands-On Machine Learning"** by Aurélien Géron
- **"Python Machine Learning"** by Sebastian Raschka
- **"The Elements of Statistical Learning"** (free PDF)

### 🎥 Video Courses
- **Andrew Ng's Machine Learning Course** (Coursera)
- **CS229 Stanford Machine Learning** (YouTube)
- **3Blue1Brown Neural Networks** (YouTube)

### 💻 Practice Platforms
- **Kaggle** - Competitions and datasets
- **Google Colab** - Free GPU access
- **Papers With Code** - Latest research implementations

---

## 🎯 Project Ideas by Level

### 🟢 Beginner Projects
1. **House Price Prediction** - Linear regression with real estate data
2. **Iris Flower Classification** - Classic ML classification problem
3. **Movie Recommendation** - Collaborative filtering basics
4. **Sales Forecasting** - Time series analysis
5. **Sentiment Analysis** - Text classification with reviews

### 🟡 Intermediate Projects
1. **Image Classification** - CNN with custom dataset
2. **Chatbot** - NLP with intent recognition
3. **Stock Price Prediction** - LSTM for time series
4. **Object Detection** - YOLO implementation
5. **Anomaly Detection** - Unsupervised learning

### 🔴 Advanced Projects
1. **GANs for Image Generation** - Generative models
2. **Reinforcement Learning Game** - Q-learning agent
3. **Neural Machine Translation** - Seq2seq models
4. **Speech Recognition** - Audio processing pipeline
5. **Multi-Modal AI** - Combining text, image, and audio

---

## 🏆 Success Metrics

Track your progress with these milestones:

### Month 1 ✅
- [ ] Complete first data analysis project
- [ ] Understand pandas and matplotlib
- [ ] Build 3 data visualizations
- [ ] Set up development environment

### Month 2 ✅
- [ ] Implement linear regression from scratch
- [ ] Complete classification project with scikit-learn
- [ ] Understand cross-validation
- [ ] Deploy model to Heroku/Streamlit

### Month 3 ✅
- [ ] Build neural network with TensorFlow/PyTorch
- [ ] Complete image classification project
- [ ] Understand CNNs and RNNs
- [ ] Contribute to open source project

### Month 4+ ✅
- [ ] Choose specialization area
- [ ] Complete advanced project in chosen field
- [ ] Present work at meetup or create blog post
- [ ] Mentor another beginner

---

## 🆘 Getting Help

When you're stuck (and you will be!):

1. **Read Error Messages Carefully** - They usually tell you exactly what's wrong
2. **Google the Error** - Add "python" or the library name to your search
3. **Check Repository Issues** - Others likely had the same problem
4. **Ask Specific Questions** - Provide context, code, and error messages
5. **Use AI Assistants** - ChatGPT, Claude, and GitHub Copilot can explain code

### 🤝 Community Resources
- **r/MachineLearning** - Reddit community
- **ML Twitter** - Follow @karpathy, @ylecun, @AndrewYNg
- **Papers With Code** - Latest research with code
- **Towards Data Science** - Medium publication
- **Kaggle Forums** - Competition discussions

---

## 🚀 Ready to Start?

Your AI journey begins with a single step. Pick your first repository from Phase 1, clone it, and start experimenting!

Remember: **Everyone started as a beginner.** The key is consistent practice and never stopping to learn.

---

## 📊 Beginner-Friendly Repository Stats

{self._create_shields_badge("Beginner Repos", len([r for r in self.repositories if r.scores.get('learning_value', 0) > 0.7]), "green")} {self._create_shields_badge("Well Documented", len([r for r in self.repositories if r.scores.get('documentation', 0) > 0.7]), "blue")} {self._create_shields_badge("Active Projects", len([r for r in self.repositories if r.scores.get('freshness', 0) > 0.7]), "orange")}

---

## 🧭 Navigation

- [🏠 Main README](README.md)
- [🏆 Top 50 Repositories](TOP_REPOSITORIES.md)
- [📊 Browse by Category](README.md#-categories-overview)
- [📋 Complete Index](INDEX.md)

---

*Good luck on your AI learning journey! Remember: the best time to start was yesterday, the second best time is now. 🚀*

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | AI-powered curation*
"""
        
        # Write beginner guide
        output_file = self.output_dir / "BEGINNER_GUIDE.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Beginner guide generated: {output_file}")
    
    def generate_top_repositories(self) -> None:
        """Generate top 50 repositories page"""
        self.logger.info("Generating top repositories page")
        
        # Sort all repositories by composite score
        top_repos = sorted(self.repositories, key=lambda x: x.scores.get('composite', 0), reverse=True)[:50]
        
        content = f"""# 🏆 Top 50 AI & Machine Learning Repositories

The absolute best repositories for AI and Machine Learning, ranked by our comprehensive scoring algorithm that evaluates popularity, freshness, learning value, and documentation quality.

{self._create_shields_badge("Top Repositories", "50", "gold")} {self._create_shields_badge("Total Stars", self._format_number(sum(r.stars for r in top_repos)), "yellow")} {self._create_shields_badge("Avg Score", f"{sum(r.scores.get('composite', 0) for r in top_repos) / len(top_repos):.3f}", "green")}

---

## 📊 Overview

| Metric | Value |
|--------|--------|
| Total Stars | {self._format_number(sum(r.stars for r in top_repos))} |
| Average Stars | {self._format_number(sum(r.stars for r in top_repos) // len(top_repos))} |
| Average Score | {sum(r.scores.get('composite', 0) for r in top_repos) / len(top_repos):.3f} |
| Top Category | {max(set(r.category for r in top_repos), key=lambda x: sum(1 for r in top_repos if r.category == x))} |
| Top Language | {max(set(r.language for r in top_repos), key=lambda x: sum(1 for r in top_repos if r.language == x))} |

---

## 🥇 The Elite 50

"""
        
        for i, repo in enumerate(top_repos, 1):
            # Medal emojis for top 3
            if i == 1:
                rank_emoji = "🥇"
            elif i == 2:
                rank_emoji = "🥈"
            elif i == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"**{i}.**"
            
            # Category emoji
            category_emoji = self.CATEGORY_INFO.get(repo.category, {}).get('emoji', '🔧')
            
            content += f"""### {rank_emoji} [{repo.name}]({repo.url})

{category_emoji} **{repo.category}** | **{repo.owner}**

{repo.description}

{self._create_shields_badge("⭐", self._format_number(repo.stars), "yellow")} {self._create_shields_badge("🍴", self._format_number(repo.forks), "blue")} {self._create_shields_badge("Language", repo.language, "green")} {self._get_activity_badge(repo)} {self._get_difficulty_badge(repo)}

**📊 Detailed Scores:**
- **Composite Score: {repo.scores.get('composite', 0):.3f}** ⭐
- Popularity: {self._get_score_bar(repo.scores.get('popularity', 0))}
- Freshness: {self._get_score_bar(repo.scores.get('freshness', 0))}
- Learning Value: {self._get_score_bar(repo.scores.get('learning_value', 0))}
- Documentation: {self._get_score_bar(repo.scores.get('documentation', 0))}

"""
            
            # Add additional metadata
            if repo.homepage:
                content += f"🏠 **Homepage:** [{repo.homepage}]({repo.homepage})\n"
            if repo.license:
                content += f"📄 **License:** {repo.license}\n"
            if repo.topics:
                topics_str = " ".join([f"`{topic}`" for topic in repo.topics[:6]])
                content += f"🏷️ **Topics:** {topics_str}\n"
            
            content += "\n---\n\n"
        
        # Add methodology
        content += f"""
## 📈 Ranking Methodology

Our composite scoring algorithm evaluates repositories across four key dimensions:

### 🌟 Popularity Score (25% weight)
- GitHub stars and forks
- Community engagement metrics
- Social proof indicators

### 🔄 Freshness Score (25% weight)  
- Recent commit activity
- Issue and PR responsiveness
- Maintenance indicators

### 📚 Learning Value Score (30% weight)
- Documentation quality
- Educational content
- Example availability
- Tutorial resources

### 📊 Documentation Score (20% weight)
- README completeness
- Code comments
- API documentation
- User guides

**Final Composite Score = (Popularity × 0.25) + (Freshness × 0.25) + (Learning Value × 0.30) + (Documentation × 0.20)**

---

## 🎯 Score Distribution

"""
        
        # Add score distribution stats
        scores = [r.scores.get('composite', 0) for r in top_repos]
        content += f"""
- **Highest Score:** {max(scores):.3f} ({top_repos[0].name})
- **Lowest Score:** {min(scores):.3f} ({top_repos[-1].name})
- **Average Score:** {sum(scores) / len(scores):.3f}
- **Median Score:** {sorted(scores)[len(scores)//2]:.3f}

**Score Ranges:**
- 🏆 **Elite (0.8+):** {len([s for s in scores if s >= 0.8])} repositories
- 🥇 **Excellent (0.7-0.8):** {len([s for s in scores if 0.7 <= s < 0.8])} repositories  
- 🥈 **Very Good (0.6-0.7):** {len([s for s in scores if 0.6 <= s < 0.7])} repositories
- 🥉 **Good (0.5-0.6):** {len([s for s in scores if 0.5 <= s < 0.6])} repositories

---

## 💡 How to Use This List

### 🔰 For Beginners
Focus on repositories with:
- High Learning Value scores (📚 > 0.7)
- Good Documentation scores (📊 > 0.6)  
- {self._create_shields_badge("Difficulty", "Beginner", "green")} badges

### 🚀 For Practitioners
Look for repositories with:
- High Popularity scores (🌟 > 0.7)
- Recent Freshness scores (🔄 > 0.6)
- Active community engagement

### 🔬 For Researchers  
Consider repositories with:
- Cutting-edge techniques
- High composite scores
- Active development
- Research paper implementations

---

## 🧭 Navigation

- [🏠 Main README](README.md)
- [🔰 Beginner's Guide](BEGINNER_GUIDE.md)
- [📊 Browse by Category](README.md#-categories-overview)
- [📋 Complete Index](INDEX.md)

---

## 📅 Last Updated

This ranking was generated on **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}** using data from **{self.metadata.get('analysis_date', 'Unknown')[:10]}**.

Rankings are updated automatically as new repositories are discovered and existing ones are re-evaluated.

---

*These are the repositories that define the state of AI and Machine Learning. Start exploring and happy learning! 🚀*

*Generated with ❤️ by AI-powered curation system*
"""
        
        # Write top repositories page
        output_file = self.output_dir / "TOP_REPOSITORIES.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Top repositories page generated: {output_file}")
    
    def generate_index_page(self) -> None:
        """Generate comprehensive index page"""
        self.logger.info("Generating index page")
        
        content = f"""# 📋 Complete Repository Index

Comprehensive index of all {len(self.repositories)} AI and Machine Learning repositories, organized for easy browsing and discovery.

{self._create_shields_badge("Total Repositories", len(self.repositories), "blue")} {self._create_shields_badge("Categories", len(self.categories), "green")} {self._create_shields_badge("Languages", len(self.languages), "purple")}

---

## 🧭 Quick Navigation

- [📊 **By Category**](#-by-category) - Browse repositories by domain
- [💻 **By Language**](#-by-programming-language) - Find repositories in your preferred language  
- [⭐ **By Popularity**](#-by-popularity) - Sorted by GitHub stars
- [🔄 **By Activity**](#-by-recent-activity) - Recently updated projects
- [📚 **By Learning Value**](#-by-learning-value) - Best for education

---

## 🎨 By Category

"""
        
        # Add category sections
        for category, repos in sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True):
            if not repos:
                continue
                
            category_info = self.CATEGORY_INFO.get(category, {'emoji': '🔧'})
            anchor = category.lower().replace(' ', '-').replace('&', 'and')
            
            content += f"""### {category_info['emoji']} {category} ({len(repos)} repositories)

"""
            
            # Sort by composite score and show all
            sorted_repos = sorted(repos, key=lambda x: x.scores.get('composite', 0), reverse=True)
            
            for repo in sorted_repos:
                stars_badge = self._create_shields_badge("⭐", self._format_number(repo.stars), "yellow")
                lang_badge = self._create_shields_badge("Lang", repo.language, "blue")
                score = repo.scores.get('composite', 0)
                
                content += f"- **[{repo.name}]({repo.url})** ({score:.3f}) {stars_badge} {lang_badge}\n  *{repo.description[:120]}{'...' if len(repo.description) > 120 else ''}*\n\n"
            
            content += "---\n\n"
        
        # By programming language
        content += f"""## 💻 By Programming Language

"""
        
        for language, repos in sorted(self.languages.items(), key=lambda x: len(x[1]), reverse=True):
            if language == 'Unknown' or len(repos) < 3:
                continue
                
            content += f"""### {language} ({len(repos)} repositories)

"""
            
            # Sort by stars and show top 10 per language
            sorted_repos = sorted(repos, key=lambda x: x.stars, reverse=True)[:10]
            
            for repo in sorted_repos:
                stars_badge = self._create_shields_badge("⭐", self._format_number(repo.stars), "yellow")
                cat_emoji = self.CATEGORY_INFO.get(repo.category, {}).get('emoji', '🔧')
                
                content += f"- **[{repo.name}]({repo.url})** {stars_badge} {cat_emoji} {repo.category}\n  *{repo.description[:120]}{'...' if len(repo.description) > 120 else ''}*\n\n"
            
            if len(repos) > 10:
                content += f"*... and {len(repos) - 10} more {language} repositories*\n\n"
            
            content += "---\n\n"
        
        # By popularity (stars)
        content += f"""## ⭐ By Popularity

Top repositories sorted by GitHub stars:

"""
        
        popular_repos = sorted(self.repositories, key=lambda x: x.stars, reverse=True)[:30]
        
        for i, repo in enumerate(popular_repos, 1):
            cat_emoji = self.CATEGORY_INFO.get(repo.category, {}).get('emoji', '🔧')
            content += f"{i:2d}. **[{repo.name}]({repo.url})** ({self._format_number(repo.stars)} ⭐) {cat_emoji} {repo.category}\n    *{repo.description[:100]}{'...' if len(repo.description) > 100 else ''}*\n\n"
        
        content += "---\n\n"
        
        # By activity (freshness)
        content += f"""## 🔄 By Recent Activity

Most recently updated and actively maintained projects:

"""
        
        active_repos = sorted(self.repositories, key=lambda x: x.scores.get('freshness', 0), reverse=True)[:20]
        
        for i, repo in enumerate(active_repos, 1):
            cat_emoji = self.CATEGORY_INFO.get(repo.category, {}).get('emoji', '🔧')
            freshness = repo.scores.get('freshness', 0)
            activity_badge = self._get_activity_badge(repo)
            
            content += f"{i:2d}. **[{repo.name}]({repo.url})** (Freshness: {freshness:.3f}) {activity_badge} {cat_emoji} {repo.category}\n    *{repo.description[:100]}{'...' if len(repo.description) > 100 else ''}*\n\n"
        
        content += "---\n\n"
        
        # By learning value
        content += f"""## 📚 By Learning Value

Best repositories for learning, sorted by educational value:

"""
        
        learning_repos = sorted(self.repositories, key=lambda x: x.scores.get('learning_value', 0), reverse=True)[:20]
        
        for i, repo in enumerate(learning_repos, 1):
            cat_emoji = self.CATEGORY_INFO.get(repo.category, {}).get('emoji', '🔧')
            learning_value = repo.scores.get('learning_value', 0)
            difficulty_badge = self._get_difficulty_badge(repo)
            
            content += f"{i:2d}. **[{repo.name}]({repo.url})** (Learning: {learning_value:.3f}) {difficulty_badge} {cat_emoji} {repo.category}\n    *{repo.description[:100]}{'...' if len(repo.description) > 100 else ''}*\n\n"
        
        content += f"""---

## 📊 Repository Statistics

### Category Distribution
"""
        
        for category, repos in sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True):
            emoji = self.CATEGORY_INFO.get(category, {}).get('emoji', '🔧')
            percentage = (len(repos) / len(self.repositories)) * 100
            content += f"- {emoji} **{category}**: {len(repos)} repositories ({percentage:.1f}%)\n"
        
        content += f"""
### Language Distribution
"""
        
        top_languages = sorted(self.languages.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for language, repos in top_languages:
            if language != 'Unknown':
                percentage = (len(repos) / len(self.repositories)) * 100
                content += f"- **{language}**: {len(repos)} repositories ({percentage:.1f}%)\n"
        
        content += f"""
### Quality Metrics
- **High Learning Value (>0.7)**: {len([r for r in self.repositories if r.scores.get('learning_value', 0) > 0.7])} repositories
- **Well Documented (>0.7)**: {len([r for r in self.repositories if r.scores.get('documentation', 0) > 0.7])} repositories
- **Very Active (>0.8)**: {len([r for r in self.repositories if r.scores.get('freshness', 0) > 0.8])} repositories
- **Highly Popular (>10K stars)**: {len([r for r in self.repositories if r.stars > 10000])} repositories

---

## 🔍 Search Tips

When browsing this index:

1. **Use Ctrl+F** to search for specific topics, libraries, or techniques
2. **Check multiple categories** - some repositories span multiple domains
3. **Look at composite scores** for overall quality assessment
4. **Consider your skill level** when choosing repositories
5. **Check activity badges** for maintenance status

---

## 🧭 Navigation

- [🏠 Main README](README.md)
- [🔰 Beginner's Guide](BEGINNER_GUIDE.md)
- [🏆 Top 50 Repositories](TOP_REPOSITORIES.md)
- [📊 Browse by Category](README.md#-categories-overview)

---

## 📅 Index Information

- **Total Repositories Indexed**: {len(self.repositories)}
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Data Source**: {self.metadata.get('analysis_date', 'Unknown')[:10]}
- **Analysis Version**: {self.metadata.get('version', '1.0.0')}

---

*This comprehensive index helps you discover the perfect AI/ML repository for your needs. Happy exploring! 🚀*

*Generated with ❤️ by AI-powered curation system*
"""
        
        # Write index page
        output_file = self.output_dir / "INDEX.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Index page generated: {output_file}")
    
    def generate_language_pages(self) -> None:
        """Generate language-specific collection pages"""
        self.logger.info("Generating language-specific pages")
        
        # Create languages directory
        languages_dir = self.output_dir / "languages"
        languages_dir.mkdir(parents=True, exist_ok=True)
        
        # Only generate pages for languages with significant repositories
        significant_languages = {lang: repos for lang, repos in self.languages.items() 
                               if len(repos) >= 5 and lang != 'Unknown'}
        
        for language, repos in significant_languages.items():
            filename = f"{language.lower().replace('+', 'plus').replace('#', 'sharp')}.md"
            
            content = f"""# 💻 {language} AI & Machine Learning Repositories

Curated collection of {len(repos)} high-quality AI and Machine Learning repositories written in {language}.

{self._create_shields_badge("Language", language, "blue")} {self._create_shields_badge("Repositories", len(repos), "green")} {self._create_shields_badge("Total Stars", self._format_number(sum(r.stars for r in repos)), "yellow")}

---

## 📊 {language} Statistics

| Metric | Value |
|--------|--------|
| Total Repositories | {len(repos)} |
| Total Stars | {self._format_number(sum(r.stars for r in repos))} |
| Average Stars | {self._format_number(sum(r.stars for r in repos) // len(repos))} |
| Most Popular | [{max(repos, key=lambda x: x.stars).name}]({max(repos, key=lambda x: x.stars).url}) ({self._format_number(max(repos, key=lambda x: x.stars).stars)} ⭐) |
| Top Category | {max(set(r.category for r in repos), key=lambda x: sum(1 for r in repos if r.category == x))} |
| Avg Composite Score | {sum(r.scores.get('composite', 0) for r in repos) / len(repos):.3f} |

---

## 🎯 Why {language} for AI/ML?

"""
            
            # Add language-specific benefits
            language_benefits = {
                'Python': [
                    "🐍 **Dominant in ML**: 80%+ of ML projects use Python",
                    "📚 **Rich Ecosystem**: NumPy, Pandas, Scikit-learn, TensorFlow, PyTorch",
                    "🔰 **Beginner Friendly**: Simple syntax, extensive documentation",
                    "🌐 **Community**: Largest AI/ML community and resources",
                    "🔬 **Research**: Preferred language in academia and research"
                ],
                'R': [
                    "📊 **Statistical Computing**: Built for data analysis and statistics",
                    "📈 **Data Visualization**: ggplot2, plotly, advanced plotting",
                    "🔬 **Research Focus**: Strong in academic and research environments",
                    "📦 **CRAN**: 18,000+ packages for specialized analysis",
                    "💡 **Interactive**: RStudio, R Notebooks for exploration"
                ],
                'JavaScript': [
                    "🌐 **Web Native**: Perfect for web-based ML applications",
                    "⚡ **Real-time**: Client-side ML without server round-trips",
                    "📱 **Cross-platform**: Runs on web, mobile, and desktop",
                    "🎨 **Visualization**: D3.js, Chart.js for interactive displays",
                    "🚀 **TensorFlow.js**: Full ML pipeline in the browser"
                ],
                'Julia': [
                    "⚡ **High Performance**: C-like speed with Python-like syntax",
                    "🔢 **Numerical Computing**: Designed for scientific computing",
                    "🔬 **Research**: Growing adoption in computational research",
                    "🌉 **Interoperability**: Easy integration with Python, R, C",
                    "📈 **Growing Ecosystem**: Flux.jl, MLJ.jl for modern ML"
                ],
                'C++': [
                    "🚀 **Performance**: Maximum speed for production systems",
                    "🎮 **Real-time**: Gaming, robotics, real-time inference",
                    "📱 **Mobile**: Efficient deployment on resource-constrained devices",
                    "🏭 **Production**: Core of many ML frameworks (PyTorch, TensorFlow)",
                    "🔧 **System Level**: CUDA programming, hardware optimization"
                ]
            }
            
            benefits = language_benefits.get(language, [
                f"💼 **Specialized**: {language} offers unique advantages for specific ML domains",
                f"🔧 **Tools**: Rich ecosystem of {language}-specific ML libraries",
                f"🎯 **Focus**: Optimized for particular types of ML applications",
                f"🌟 **Community**: Active {language} ML community and contributions"
            ])
            
            for benefit in benefits:
                content += f"{benefit}\n"
            
            content += f"""
---

## 🏆 Top {language} Repositories

Here are the highest-rated {language} repositories for AI and Machine Learning:

"""
            
            # Sort by composite score and show top repositories
            top_repos = sorted(repos, key=lambda x: x.scores.get('composite', 0), reverse=True)[:15]
            
            for i, repo in enumerate(top_repos, 1):
                cat_emoji = self.CATEGORY_INFO.get(repo.category, {}).get('emoji', '🔧')
                
                content += f"""### {i}. [{repo.name}]({repo.url})

{cat_emoji} **{repo.category}** | **{repo.owner}**

{repo.description}

{self._create_shields_badge("⭐", self._format_number(repo.stars), "yellow")} {self._create_shields_badge("🍴", self._format_number(repo.forks), "blue")} {self._get_activity_badge(repo)} {self._get_difficulty_badge(repo)}

**Scores:** Composite: {repo.scores.get('composite', 0):.3f} | Learning: {repo.scores.get('learning_value', 0):.2f} | Freshness: {repo.scores.get('freshness', 0):.2f}

"""
                
                if repo.homepage:
                    content += f"🏠 **Homepage:** [{repo.homepage}]({repo.homepage})\n"
                if repo.topics:
                    topics_str = " ".join([f"`{topic}`" for topic in repo.topics[:5]])
                    content += f"🏷️ **Topics:** {topics_str}\n"
                
                content += "\n---\n\n"
            
            # Add category breakdown
            content += f"""## 📊 Categories in {language}

"""
            
            # Count repositories by category
            category_counts = {}
            for repo in repos:
                category_counts[repo.category] = category_counts.get(repo.category, 0) + 1
            
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                emoji = self.CATEGORY_INFO.get(category, {}).get('emoji', '🔧')
                percentage = (count / len(repos)) * 100
                content += f"- {emoji} **{category}**: {count} repositories ({percentage:.1f}%)\n"
            
            # Add learning resources specific to the language
            content += f"""
---

## 📚 Learning {language} for AI/ML

### 🎯 Getting Started
1. **Set up your {language} environment** for ML development
2. **Learn core {language} concepts** relevant to data science
3. **Explore {language}-specific ML libraries** from the repositories above
4. **Build projects** using {language} ML tools
5. **Join the {language} ML community**

### 📖 Recommended Learning Path
"""
            
            # Language-specific learning paths
            if language == 'Python':
                learning_steps = [
                    "Master Python basics (data types, functions, classes)",
                    "Learn NumPy for numerical computing",
                    "Understand Pandas for data manipulation",
                    "Practice with Matplotlib/Seaborn for visualization",
                    "Explore Scikit-learn for traditional ML",
                    "Dive into TensorFlow or PyTorch for deep learning"
                ]
            elif language == 'R':
                learning_steps = [
                    "Understand R syntax and data structures",
                    "Master data.frame and tibble operations",
                    "Learn ggplot2 for advanced visualization",
                    "Explore tidyverse for data science workflow",
                    "Practice with caret for machine learning",
                    "Study specialized packages for your domain"
                ]
            elif language == 'JavaScript':
                learning_steps = [
                    "Learn modern JavaScript (ES6+, async/await)",
                    "Understand Node.js for backend development",
                    "Explore TensorFlow.js for browser ML",
                    "Practice with D3.js for data visualization",
                    "Build interactive ML web applications",
                    "Deploy models to web platforms"
                ]
            else:
                learning_steps = [
                    f"Learn {language} fundamentals and syntax",
                    f"Understand {language} data structures and libraries",
                    f"Explore {language}-specific ML frameworks",
                    f"Practice with real-world {language} ML projects",
                    f"Connect with the {language} ML community",
                    f"Contribute to open-source {language} ML projects"
                ]
            
            for i, step in enumerate(learning_steps, 1):
                content += f"{i}. **{step}**\n"
            
            content += f"""
---

## 🧭 Navigation

- [🏠 Main README](../README.md)
- [🔰 Beginner's Guide](../BEGINNER_GUIDE.md)
- [🏆 Top 50 Repositories](../TOP_REPOSITORIES.md)
- [📋 Complete Index](../INDEX.md)
- [📊 All Languages](../README.md#-programming-languages)

---

*Explore the power of {language} in AI and Machine Learning! These {len(repos)} repositories represent the best of {language} in the ML ecosystem.*

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | AI-powered curation*
"""
            
            # Write language page
            output_file = languages_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Generated language page: {output_file}")
    
    def generate_sitemap(self) -> None:
        """Generate sitemap and navigation index"""
        self.logger.info("Generating sitemap")
        
        content = f"""# 🗺️ Site Map & Navigation

Complete navigation guide for the AI & Machine Learning Repository Collection.

---

## 📋 Main Pages

### 🏠 Core Documentation
- **[README.md](README.md)** - Main overview and category navigation
- **[BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)** - Complete beginner's learning guide
- **[TOP_REPOSITORIES.md](TOP_REPOSITORIES.md)** - Top 50 highest-rated repositories
- **[INDEX.md](INDEX.md)** - Comprehensive index of all repositories

---

## 🎨 Category Pages ({len(self.categories)} categories)

### 📁 categories/
"""
        
        for category in sorted(self.categories.keys()):
            emoji = self.CATEGORY_INFO.get(category, {}).get('emoji', '🔧')
            filename = category.lower().replace(' ', '_').replace('&', 'and') + '.md'
            repo_count = len(self.categories[category])
            
            content += f"- {emoji} **[{category}](categories/{filename})** ({repo_count} repositories)\n"
        
        content += f"""
---

## 💻 Language Pages ({len([l for l in self.languages.keys() if l != 'Unknown' and len(self.languages[l]) >= 5])} languages)

### 📁 languages/
"""
        
        # Only show significant languages
        significant_languages = {lang: repos for lang, repos in self.languages.items() 
                               if len(repos) >= 5 and lang != 'Unknown'}
        
        for language in sorted(significant_languages.keys()):
            filename = f"{language.lower().replace('+', 'plus').replace('#', 'sharp')}.md"
            repo_count = len(significant_languages[language])
            
            content += f"- 💻 **[{language}](languages/{filename})** ({repo_count} repositories)\n"
        
        content += f"""
---

## 📊 Repository Statistics

- **Total Repositories**: {len(self.repositories)}
- **Total Categories**: {len(self.categories)}
- **Programming Languages**: {len(self.languages)}
- **Total GitHub Stars**: {self._format_number(sum(r.stars for r in self.repositories))}
- **Average Rating**: {sum(r.scores.get('composite', 0) for r in self.repositories) / len(self.repositories):.3f}

---

## 🧭 Quick Access Links

### 🎯 By Experience Level
- **[Beginner Friendly](BEGINNER_GUIDE.md#-learning-path-zero-to-ai-hero)** - Start your AI journey
- **[Intermediate Projects](INDEX.md#-by-learning-value)** - Build on your foundation  
- **[Advanced Research](TOP_REPOSITORIES.md)** - Cutting-edge repositories

### 🏷️ By Domain
"""
        
        # Add quick domain links
        domain_categories = [
            ('Computer Vision', '👁️'),
            ('Natural Language Processing', '📝'),
            ('Machine Learning', '🤖'),
            ('Deep Learning', '🧠'),
            ('Reinforcement Learning', '🎮'),
            ('Data Science', '📊')
        ]
        
        for domain, emoji in domain_categories:
            if domain in self.categories:
                filename = domain.lower().replace(' ', '_').replace('&', 'and') + '.md'
                content += f"- {emoji} **[{domain}](categories/{filename})**\n"
        
        content += f"""

### 📈 By Popularity
- **[Most Starred](INDEX.md#-by-popularity)** - Community favorites
- **[Most Active](INDEX.md#-by-recent-activity)** - Recently updated
- **[Best Documented](INDEX.md#-by-learning-value)** - Learning resources

### 💾 By Language
"""
        
        # Add top language quick links
        top_langs = sorted(significant_languages.items(), key=lambda x: len(x[1]), reverse=True)[:6]
        for language, repos in top_langs:
            filename = f"{language.lower().replace('+', 'plus').replace('#', 'sharp')}.md"
            content += f"- 💻 **[{language}](languages/{filename})** ({len(repos)} repos)\n"
        
        content += f"""
---

## 🔍 Search & Discovery

### Finding the Right Repository
1. **Browse by Category** - Start with your area of interest
2. **Check Learning Value** - Look for high educational scores
3. **Consider Difficulty** - Match repositories to your skill level
4. **Review Activity** - Choose actively maintained projects
5. **Read Documentation** - Ensure good learning resources

### Search Tips
- Use **Ctrl+F** on any page to find specific technologies
- Check **multiple categories** - some repos span domains
- Look at **composite scores** for overall quality
- Consider **star count** for community validation
- Review **activity badges** for maintenance status

---

## 📱 File Structure

```
awesome-ai-learning/
├── README.md                 # Main overview
├── BEGINNER_GUIDE.md        # Learning guide
├── TOP_REPOSITORIES.md      # Top 50 repos
├── INDEX.md                 # Complete index
├── SITEMAP.md               # This navigation guide
├── categories/              # Category pages
│   ├── computer_vision.md
│   ├── natural_language_processing.md
│   ├── machine_learning.md
│   └── ... (all categories)
└── languages/              # Language-specific pages
    ├── python.md
    ├── javascript.md
    ├── r.md
    └── ... (major languages)
```

---

## 🔄 Updates & Maintenance

- **Auto-generated**: All pages are automatically generated from repository data
- **Regular Updates**: Content refreshed as new repositories are discovered
- **Quality Scoring**: Repositories continuously re-evaluated for relevance
- **Community Driven**: Star repositories to help improve curation

---

## 📞 Getting Help

Lost or looking for something specific?

1. **Check the [INDEX.md](INDEX.md)** - Comprehensive list of all repositories
2. **Use category pages** - Browse by your area of interest
3. **Try the language pages** - Find repos in your preferred language
4. **Start with [BEGINNER_GUIDE.md](BEGINNER_GUIDE.md)** - If you're new to AI/ML
5. **Browse [TOP_REPOSITORIES.md](TOP_REPOSITORIES.md)** - For the highest quality projects

---

## 📈 Usage Statistics

This sitemap helps navigate:
- **{len(self.repositories):,}** curated repositories
- **{len(self.categories)}** specialized categories  
- **{len(significant_languages)}** programming languages
- **{sum(len(repos) for repos in self.categories.values()):,}** total category assignments
- **{self._format_number(sum(r.stars for r in self.repositories))}** total GitHub stars

---

*Everything you need to navigate the world of AI & Machine Learning repositories! 🚀*

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Write sitemap
        output_file = self.output_dir / "SITEMAP.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Sitemap generated: {output_file}")
    
    def generate_all(self) -> None:
        """Generate all markdown files"""
        try:
            self.logger.info("Starting complete markdown generation")
            
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Load data
            self.load_data()
            
            # Generate all pages
            self.generate_main_readme()
            self.generate_category_pages()
            self.generate_beginner_guide()
            self.generate_top_repositories()
            self.generate_index_page()
            self.generate_language_pages()
            self.generate_sitemap()
            
            # Summary
            self.logger.info("✅ Markdown generation completed successfully!")
            self.logger.info(f"📁 Output directory: {self.output_dir}")
            self.logger.info(f"📊 Generated documentation for {len(self.repositories)} repositories")
            self.logger.info(f"🎨 Created {len(self.categories)} category pages")
            self.logger.info(f"💻 Created {len([l for l in self.languages.keys() if l != 'Unknown' and len(self.languages[l]) >= 5])} language pages")
            
            # List generated files
            generated_files = list(self.output_dir.glob('**/*.md'))
            self.logger.info(f"📝 Total files generated: {len(generated_files)}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate markdown: {e}")
            raise


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Generate beautiful markdown documentation from AI repository data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_markdown.py
  python generate_markdown.py --data custom_data.json --output /path/to/output
  python generate_markdown.py --verbose
        """
    )
    
    parser.add_argument(
        '--data', 
        default='../data/categorized_repos.json',
        help='Path to categorized repository data JSON file (default: ../data/categorized_repos.json)'
    )
    
    parser.add_argument(
        '--output',
        default='../markdown_output',
        help='Output directory for generated markdown files (default: ../markdown_output)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize generator
        generator = MarkdownGenerator(args.data, args.output)
        
        # Generate all markdown files
        generator.generate_all()
        
        print("🎉 Success! Beautiful markdown documentation has been generated.")
        print(f"📁 Check the output directory: {Path(args.output).absolute()}")
        print("🚀 Your AI learning repository collection is ready!")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Generation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())