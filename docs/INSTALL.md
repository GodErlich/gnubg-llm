# 📦 Installation Guide

## Prerequisites for Local Setup:

### Windows OS
1. Install WSL2
(In powershell as admin run: `wsl --install` or  [install manually](https://documentation.ubuntu.com/wsl/latest/howto/install-ubuntu-wsl2/))
2. Ubuntu 22.04+
(In powershell as admin run: `wsl --install Ubuntu-24.04` or [install manually](https://documentation.ubuntu.com/wsl/latest/howto/install-ubuntu-wsl2/))
3. Follow Quick Installation

### Linux
- **Linux**: Ubuntu 22.04+ or Debian 11+
- **Package Manager**: `apt` with `sudo` access
- **Python**: 3.8+

## Quick Installation

Open bash where you want to clone the project. (Windows users open WSL). Then run the following commands:

1. `git clone https://github.com/GodErlich/gnubg-llm.git`
2. `cd gnubg-llm`
3. `make all` # Complete setup - might take 30-60 seconds.
4. Optional - To open in vscode write: `code .` or open the cloned project with your favorite IDE
