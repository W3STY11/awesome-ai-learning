#!/bin/bash
# Quick start script to fetch starred repositories

echo "🌟 GitHub Stars Fetcher"
echo "====================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Create .env file from the provided token
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
GITHUB_TOKEN=YOUR_GITHUB_TOKEN_HERE
GITHUB_USERNAME=YOUR_GITHUB_USERNAME_HERE
EOF
fi

# Run the fetcher
echo "Fetching starred repositories..."
python tools/fetch_stars.py

echo "✅ Done! Check the data/ directory for results."