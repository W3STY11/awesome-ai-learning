#!/bin/bash

# generate_docs.sh - Easy documentation generation script
# This script generates beautiful markdown documentation from repository data

echo "🚀 Generating Beautiful AI Learning Documentation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if data file exists
DATA_FILE="../data/categorized_repos.json"
if [ ! -f "$DATA_FILE" ]; then
    echo "❌ Error: Data file not found at $DATA_FILE"
    echo "💡 Please run the repository analysis first:"
    echo "   cd tools && python analyze_repos.py"
    exit 1
fi

# Create output directory
OUTPUT_DIR="../markdown_output"
mkdir -p "$OUTPUT_DIR"

echo "📊 Found $(jq '.repositories | length' "$DATA_FILE") repositories to process..."
echo "📁 Output directory: $OUTPUT_DIR"
echo ""

# Run the markdown generator
echo "🔄 Generating markdown files..."
python generate_markdown.py --verbose

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 SUCCESS! Documentation generated successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📂 Generated files:"
    echo "   📋 Main README.md - Overview and navigation"
    echo "   🔰 BEGINNER_GUIDE.md - Learning paths and tutorials"
    echo "   🏆 TOP_REPOSITORIES.md - Top 50 highest-rated repos"
    echo "   📖 INDEX.md - Complete repository index"
    echo "   🗺️  SITEMAP.md - Navigation guide"
    echo ""
    echo "📁 Organized by category ($(ls -1 "$OUTPUT_DIR/categories" | wc -l) categories):"
    ls -1 "$OUTPUT_DIR/categories" | head -5 | sed 's/^/   📝 /'
    if [ $(ls -1 "$OUTPUT_DIR/categories" | wc -l) -gt 5 ]; then
        echo "   ... and $(($(ls -1 "$OUTPUT_DIR/categories" | wc -l) - 5)) more categories"
    fi
    echo ""
    echo "💻 Language-specific pages ($(ls -1 "$OUTPUT_DIR/languages" | wc -l) languages):"
    ls -1 "$OUTPUT_DIR/languages" | head -5 | sed 's/^/   🔗 /'
    if [ $(ls -1 "$OUTPUT_DIR/languages" | wc -l) -gt 5 ]; then
        echo "   ... and $(($(ls -1 "$OUTPUT_DIR/languages" | wc -l) - 5)) more languages"
    fi
    echo ""
    echo "🌐 Ready to publish:"
    echo "   • Copy files to your website/GitHub Pages"
    echo "   • Share the README.md as your main documentation"
    echo "   • Direct beginners to BEGINNER_GUIDE.md"
    echo ""
    echo "🔗 Quick links:"
    echo "   • Main README: $OUTPUT_DIR/README.md"
    echo "   • Beginner Guide: $OUTPUT_DIR/BEGINNER_GUIDE.md"
    echo "   • Top Repositories: $OUTPUT_DIR/TOP_REPOSITORIES.md"
    echo ""
    echo "✨ Your AI learning repository collection is ready!"
else
    echo ""
    echo "❌ Generation failed. Please check the error messages above."
    exit 1
fi