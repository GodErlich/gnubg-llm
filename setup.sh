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

cd ~/gnubg-llm
pip3 install --user -r requirements.txt # Install Python dependencies globally because gnubg has embedded Python.


# Test installation
echo "🧪 Testing..."
gnubg --version > /dev/null

if [ $? -ne 0 ]; then
    echo "❌ GNU Backgammon installation failed!"
    exit 1
else
    echo "✅ GNU Backgammon installed successfully! 🎉"
fi
