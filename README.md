# 🎲 GNU Backgammon Research Environment
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/GodErlich/gnubg-llm/blob/main/demo.ipynb)
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-908a85?logo=gitpod)](https://gitpod.io/#https://github.com/GodErlich/gnubg-llm)

This code uses [gnubg module](https://www.gnu.org/software/gnubg/) to create backgammon "agents".

It will be used by other developers to research different agents by themselves and let them play against each other. This code is an infrastructure for research.

## 🚀 Try It Now - No Installation Required!

### Option 1: Google Colab (No Account Required)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/GodErlich/gnubg-llm/blob/main/demo.ipynb)
1. Click the **"Open In Colab"** badge above
2. **No sign-up required** - runs immediately
3. Click **"Run All"** to set up everything automatically
4. Follow the steps to understand everything better.
5. Start experimenting!

### Option 2: Gitpod
**[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-908a85?logo=gitpod)](https://gitpod.io/#https://github.com/GodErlich/gnubg-llm)**
1. Click the **"Gitpod Ready-to-Code"** badge above
2. Sign in with GitHub
3. Wait for environment setup
4. Make sure you are inside gnubg-llm folder
5. Run: `python3 main.py` in the terminal
6. Start experimenting!

## Quick start
Open bash where you want to clone the project. (Windows users open WSL). Then run the following commands:
1. git clone https://github.com/GodErlich/gnubg-llm.git
2. cd gnubg-llm
3. make all # Complete setup - might take 30-60 seconds.
4. Optional - To open in vscode write: `code .` or open the cloned project with your favorite IDE

## How to run?
1. Make sure you are inside the root folder of the project
2. Make sure you ran the setup. If not run: `make all`
3. In the terminal write: `python3 main.py`
4. If you wish to stop the run in the middle, just click `Ctrl + c` in the terminal.

### Basic Examples:
- `python3 main.py --a1 RandomAgent --a2 RandomAgent --n 3 --d`
  Will run 3 games with RandomAgent vs RandomAgent and debug logs.
- `python3 main.py --a1 LLMAgent --a2 BestMoveAgent --p "Play aggressively" --sp "You are a backgammon expert" --pm --hi`
  Will run LLM agent with custom prompts and additional input (possible moves and hints).

## What is an agent in the project context?
Agent will get as input these parameters:
1. only the board ( make sure no invalid move happen)
2. board and all possible moves
3. board + hints
4. board + best possible move

The agent will decide what to do with the above input + additional text(prompt), and will output a move accordingly.

## 📚 Documentation

For detailed information, please refer to the following documentation:

- **[📦 Installation Guide](docs/INSTALL.md)** - Complete installation instructions, prerequisites, and setup requirements
- **[📖 How to Use](docs/HOW_TO_USE.md)** - Comprehensive usage guide with all command-line options and configuration details
- **[🔧 Development Guide](docs/DEVELOPMENT.md)** - Development information, file explanations, project architecture, and how to create custom agents

## Notice!
To run Agents that use LLM you have to create a .env file with your parameters.
Just duplicate `example.env` file, change the duplicated file name to .env and put the real values in there.

## Additional links
[gnubg offical python docs](https://www.gnu.org/software/gnubg/manual/html_node/Python-scripting.html)
