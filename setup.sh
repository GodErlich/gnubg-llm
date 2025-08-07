#!/bin/bash
set -e

echo "🎯 Setting up GNU Backgammon debugging environment..."

# Install dependencies
sudo apt-get update && sudo apt-get install -y \
    python3 python3-pip python3-dev python3-venv git wget build-essential \
    automake autoconf libtool pkg-config libglib2.0-dev libreadline-dev \
    libxml2-dev libxslt1-dev flex bison texinfo swig

# Create workspace and build GNU Backgammon
mkdir -p ~/gnubg-workspace
cd ~/gnubg-workspace

if [ ! -d "gnubg" ]; then
    git clone --depth 1 --branch release-1_08_003 https://git.savannah.gnu.org/git/gnubg.git
fi

cd gnubg
./autogen.sh
./configure --without-gtk --enable-simd=sse2 --enable-python
make -j$(nproc)
sudo make install
sudo ldconfig

# Setup Python environment
cd ~/gnubg-llm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test installation
echo "🧪 Testing..."
gnubg --version > /dev/null
echo 'print("✅ Setup complete!")' | gnubg -t -p /dev/stdin

echo ""
echo "🎉 Setup complete!"
