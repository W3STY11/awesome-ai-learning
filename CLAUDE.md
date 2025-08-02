# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an automated AI learning resource collection that curates and categorizes 645+ AI/ML repositories. It includes Python tools for fetching, analyzing, and generating documentation from GitHub repositories.

## Architecture

```
awesome-ai-learning/
├── tools/                    # Python analysis and generation tools
│   ├── fetch_stars.py       # GitHub API data collector
│   ├── analyze_repos.py     # Repository categorization engine
│   ├── generate_markdown.py # Documentation generator
│   └── generate_docs.sh     # Shell script orchestrator
├── markdown_output/         # Generated documentation
│   ├── categories/          # Category-specific pages
│   ├── languages/           # Language-specific collections
│   ├── INDEX.md            # Complete repository index
│   ├── TOP_REPOSITORIES.md # Top 50 ranked repos
│   └── BEGINNER_GUIDE.md   # Structured learning path
└── data/                    # JSON data files (if present)
```

## Key Components

### Python Tools
- **fetch_stars.py**: Uses GitHub GraphQL API to fetch repository metadata
- **analyze_repos.py**: Categorizes repos using rule-based classification
- **generate_markdown.py**: Creates professional markdown documentation
- **test_analyzer.py**: Unit tests for analysis functionality

### Generated Documentation
- Category pages with top repositories
- Language-specific collections
- Beginner's guide with 4-phase learning path
- Top 50 repositories by composite score
- Comprehensive index and navigation

## Common Tasks

### Update Repository Data
```bash
cd tools
python fetch_stars.py
python analyze_repos.py
```

### Generate Documentation
```bash
cd tools
./generate_docs.sh
# or
python generate_markdown.py
```

### Run Tests
```bash
cd tools
python test_analyzer.py
```

## Scoring Algorithm

Repositories are scored on 4 dimensions:
- **Popularity** (25%): Stars, forks, community engagement
- **Freshness** (25%): Recent commits, maintenance activity
- **Learning Value** (30%): Documentation, tutorials, examples
- **Documentation** (20%): README quality, guides, API docs

## Important Notes

### GitHub API
- Requires GITHUB_TOKEN environment variable for higher rate limits
- Uses GraphQL API v4 for efficient data fetching
- Implements rate limiting and error handling

### Data Flow
1. fetch_stars.py → raw repository data
2. analyze_repos.py → categorized and scored data
3. generate_markdown.py → beautiful markdown documentation

### URL References
- All GitHub URLs should use W3STY11, not aiwithnick
- Ensure internal links use relative paths
- External links should be validated

### Quality Standards
- Professional formatting with consistent styling
- Clear navigation and cross-linking
- Mobile-responsive markdown
- Accessibility considerations

## Maintenance

### Regular Updates
- Repository data should be refreshed periodically
- Statistics in README need updating after data changes
- Broken links should be checked and fixed
- Categories may need adjustment as new repos are added

### Code Quality
- Python code follows PEP 8
- Type hints where appropriate
- Comprehensive error handling
- Logging for debugging

## Known Issues to Fix
- URLs reference "aiwithnick" instead of "W3STY11"
- Multiple README files causing confusion
- Statistics may be outdated
- Some category classifications need refinement
- .swarm directory should be reviewed/removed