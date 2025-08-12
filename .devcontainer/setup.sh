#!/bin/bash

set -e

echo "🚀 Setting up GNU Backgammon Research Environment..."

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    wget \
    gnubg \
    make

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install --user -r requirements.txt
    echo "✅ Python dependencies installed"
else
    echo "⚠️ No requirements.txt found, skipping Python dependencies"
fi

# Install Jupyter and additional packages for interactive demos
echo "📓 Installing Jupyter and demo dependencies..."
pip3 install --user jupyter ipywidgets matplotlib pandas
echo "✅ Jupyter environment ready"

# Test installation
echo "🧪 Testing GNU Backgammon installation..."
if gnubg --version > /dev/null 2>&1; then
    echo "✅ GNU Backgammon test passed"
else
    echo "❌ GNU Backgammon installation failed!"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p output

# Set executable permissions
chmod +x main.py

echo "✅ Setup complete! GNU Backgammon Research Environment is ready! 🎉"
echo ""
echo "🎮 Quick Start:"
echo "  Run a simple game: python3 main.py"
echo "  Run multiple games: python3 main.py --n 5"
echo "  See all options: python3 main.py --help"
echo ""
echo "📚 For more information, check the README.md"