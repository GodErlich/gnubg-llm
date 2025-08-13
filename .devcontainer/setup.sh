#!/bin/bash

set -e

echo "🚀 Setting up GNU Backgammon Research Environment..."

# Add gnubg to PATH first
export PATH="/usr/games:$PATH"
echo 'export PATH="/usr/games:$PATH"' >> ~/.bashrc

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    python3-dev \
    git \
    wget \
    gnubg \
    make \
    build-essential

# Install Python dependencies to user directory first
echo "🐍 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Python dependencies installed"
else
    echo "⚠️ No requirements.txt found, skipping Python dependencies"
fi

# Install Jupyter and additional packages for interactive demos
echo "📓 Installing Jupyter and demo dependencies..."
pip install jupyter ipywidgets matplotlib pandas
echo "✅ Jupyter environment ready"

# Install packages globally for gnubg access (Step 3 fix from Colab)
echo "🔧 Installing packages globally for GNU Backgammon access..."
echo "Using the proven method that works in Colab..."

# Method 1: Standard global installation
echo "1️⃣ Global installation..."
sudo pip install --upgrade requests python-dotenv certifi charset-normalizer idna urllib3

# Method 2: Install to system site-packages
echo "2️⃣ System site-packages installation..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
sudo pip install --target /usr/lib/python3/dist-packages --upgrade requests python-dotenv || true
sudo pip install --target /usr/lib/python${PYTHON_VERSION}/dist-packages --upgrade requests python-dotenv || true
sudo pip install --target /usr/local/lib/python3.10/site-packages --upgrade requests python-dotenv || true

# Method 3: Install to multiple gnubg-compatible locations
echo "3️⃣ Multiple location installation..."
LOCATIONS=(
    "/usr/lib/python3/dist-packages"
    "/usr/lib/python${PYTHON_VERSION}/dist-packages"
    "/usr/local/lib/python3.10/site-packages"
)

for location in "${LOCATIONS[@]}"; do
    if [ -d "$(dirname "$location")" ]; then
        sudo pip install --target "$location" --upgrade requests python-dotenv || true
    fi
done

# Method 4: Force reinstall
echo "4️⃣ Force reinstall..."
sudo pip install --force-reinstall --no-deps requests || true
sudo pip install --force-reinstall --no-deps python-dotenv || true

# Test installation
echo "🧪 Testing GNU Backgammon installation..."
if gnubg --version > /dev/null 2>&1; then
    echo "✅ GNU Backgammon test passed"
else
    echo "❌ GNU Backgammon installation failed!"
    exit 1
fi

# Test package access from gnubg
echo "🧪 Testing package access from GNU Backgammon..."
echo "import requests; print('✅ requests works')" > test_requests.py
if timeout 10 gnubg -t -p test_requests.py 2>/dev/null | grep -q "✅"; then
    echo "✅ GNU Backgammon can access Python packages"
else
    echo "⚠️ GNU Backgammon package access needs additional setup"
fi
rm -f test_requests.py

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