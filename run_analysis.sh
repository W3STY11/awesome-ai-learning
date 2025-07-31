#!/bin/bash

# Advanced Repository Analysis Runner
# This script runs the repository analysis in different modes

echo "🚀 Advanced Repository Analysis"
echo "================================"

# Change to tools directory
cd "$(dirname "$0")/tools" || exit 1

# Check if data exists
if [ ! -f "../data/starred_repos_latest.json" ]; then
    echo "❌ Data file not found. Please run fetch_stars.py first."
    exit 1
fi

# Check Python environment
if ! python -c "import pandas, numpy, scikit-learn, tqdm, click" 2>/dev/null; then
    echo "❌ Required Python packages not installed."
    echo "   Run: pip install -r ../requirements.txt"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Ask user which mode to run
echo "Choose analysis mode:"
echo "1. Fast Mode (rule-based classification only) - ~30 seconds"
echo "2. Full Mode (with AI embeddings) - ~5-10 minutes, requires internet"
echo "3. Run tests only"
echo ""
read -p "Enter choice (1/2/3): " choice

case $choice in
    1)
        echo "🏃 Running Fast Mode Analysis..."
        python analyze_repos.py --no-embeddings -v
        ;;
    2)
        echo "🧠 Running Full Mode Analysis with AI embeddings..."
        echo "   This will download AI models on first run (~500MB)"
        python analyze_repos.py -v
        ;;
    3)
        echo "🧪 Running Tests..."
        python test_analyzer.py
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

# Check if analysis completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Analysis completed successfully!"
    echo ""
    echo "📁 Output files:"
    if [ -f "../data/categorized_repos.json" ]; then
        echo "   📊 ../data/categorized_repos.json"
        file_size=$(du -h "../data/categorized_repos.json" | cut -f1)
        echo "      Size: $file_size"
        
        # Show basic stats
        repo_count=$(python -c "import json; data=json.load(open('../data/categorized_repos.json')); print(data['metadata']['total_repositories'])" 2>/dev/null)
        if [ ! -z "$repo_count" ]; then
            echo "      Repositories: $repo_count"
        fi
    fi
    
    if [ -f "analyze_repos.log" ]; then
        echo "   📋 tools/analyze_repos.log"
    fi
    
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Check the categorized results in data/categorized_repos.json"
    echo "   2. Run generate_markdown.py to create category pages"
    echo "   3. View the log file for detailed analysis information"
    echo ""
else
    echo ""
    echo "❌ Analysis failed. Check the error messages above."
    echo "   Try running in fast mode (option 1) if full mode fails."
    exit 1
fi