# 🎲 GNU Backgammon Research Environment
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/GodErlich/gnubg-llm/blob/main/demo.ipynb)
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-908a85?logo=gitpod)](https://gitpod.io/#https://github.com/GodErlich/gnubg-llm)

This code uses [gnubg module](https://www.gnu.org/software/gnubg/) to create backgammon "agents".

It will be used by other developers to research different agents by themselves and let them play
against each other.
This code is an infrastructure for research.

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


## Prerequisites for Local Setup:
### Windows OS
1. Install WSL2
(In powershell as admin run: `wsl --install` or  [install manually](https://documentation.ubuntu.com/wsl/latest/howto/install-ubuntu-wsl2/))
2. Ubuntu 22.04+
(In powershell as admin run: `wsl --install Ubuntu-24.04` or [install manually](https://documentation.ubuntu.com/wsl/latest/howto/install-ubuntu-wsl2/))
3. Follow linux quick start

### Linux
- **Linux**: Ubuntu 22.04+ or Debian 11+
- **Package Manager**: `apt` with `sudo` access
- **Python**: 3.8+

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

## Run configurations
There are few parameters that can be passed to the program.
  -h, --help            show this help message and exit
  --log_file_name, --fn  LOG_FILE_NAME,
                        Name for the log file (default: game)
  --log_folder_path, --fp LOG_FOLDER_PATH,
                        Folder path for logs (default: output)
  --agent1, --a1 {BestMoveAgent,RandomAgent,LLMAgent,LiveCodeAgent},
                        Agent type for player 1 (default: BestMoveAgent)
  --agent2, --a2 {BestMoveAgent,RandomAgent,LLMAgent,LiveCodeAgent},
                        Agent type for player 2 (default: RandomAgent)
  --number_of_games, --n NUMBER_OF_GAMES,
                        Number of games to play (default: 1)
  --debug_mode, --d     Enable debug mode for detailed logging (default: False)

For example: `python3 main.py --a1 RandomAgent --a2 RandomAgent --n 3 --d`
Will run the game for 3 times with RandomAgent vs RandomAgent and additional debug logs will be printed.

## Notice!
To run Agents that uses llm you have to create .env file with your parameters.
Just duplicate `example.env` file change the duplicated file name to .env and put the real values in there.

## Important Files Explanations

### 1. Makefile
The Makefile provides a comprehensive build system:

**Common Commands:**
- `make all` - Complete setup
- `make help` - Show all available targets
- `make status` - Check installation status
- `make deps` - Install only system dependencies
- `make clean` - Clean build artifacts
- `make update` - Update GNU Backgammon to latest version
- `make uninstall` - Remove GNU Backgammon from system

This comprehensive setup is necessary because gnubg requires specific compilation flags and system libraries to enable Python scripting support. Currently there is no other way to install gnubg full engine. There is a PyPi
package of gnubg, but the package can't run game, only evaluate them.

### 3. requirements.txt
Please notice this is not a classic requirements.txt file. This file will install additional requirements to the
gnubg environment, This is needed because gnubg runs on its own seperated environment. This is why there is no
`gnubg` package in the requirements.txt file.

### 4. .env
This file will store url and secret key, that will allow it to ask the llm provider questions.
You have to create this file by yourself. Just duplicate `example.env` file change the name to .env
and put the real values in there.

## Python Files Explanations

### Core Files
- **[`main.py`](main.py:1)** - Entry point for batch game execution. Handles command-line arguments, manages multiple game runs, and provides statistics. Uses subprocess to run games silently via gnubg.
- **[`app.py`](app.py:1)** - Bridge script that sets up the Python environment and imports the game logic. This is the file that gnubg actually executes with the `-p` flag.

### Source Directory ([`src/`](src/))
- **[`game_orchestrator.py`](src/game_orchestrator.py:1)** - Main game orchestrator that reads environment variables, creates agents, initializes logging, and starts a single game.
- **[`game.py`](src/game.py:1)** - Core game loop implementation. Manages turns, dice rolling, move validation, and determines winners.
- **[`utils.py`](src/utils.py:1)** - Utility functions for board operations, move validation, LLM integration, and gnubg command wrappers.
- **[`logger.py`](src/logger.py:1)** - Singleton logger class that handles file and console logging with different severity levels.
- **[`interfaces.py`](src/interfaces.py:1)** - TypedDict definitions for type safety across agent inputs and hint structures.

### Agents Directory ([`src/agents/`](src/agents/))
- **[`base.py`](src/agents/base.py:1)** - Abstract base class defining the agent interface and input filtering mechanism.
- **[`random_agent.py`](src/agents/random_agent.py:1)** - Simple agent that selects random valid moves from available options.
- **[`best_move_agent.py`](src/agents/best_move_agent.py:1)** - Development agent that logs detailed game state information while making random moves.
- **[`llm_agent.py`](src/agents/llm_agent.py:1)** - AI agent that uses external LLM APIs to analyze positions and select moves based on strategic reasoning.
- **[`live_code_agent.py`](src/agents/live_code_agent.py:1)** - Experimental agent that asks an LLM to generate Python code for move selection and executes it dynamically.
- **[`__init__.py`](src/agents/__init__.py:1)** - Package initialization file that exports all agent classes.

## Project Flow

The project follows this execution flow:

1. **Entry Point**: [`main.py`](main.py:1) parses command-line arguments and starts batch execution
2. **Game Launcher**: For each game, [`main.py`](main.py:1) calls `gnubg -t -p app.py` with environment variables
3. **Environment Setup**: [`app.py`](app.py:1) sets up Python paths and imports [`src.game_orchestrator.main`](src/game_orchestrator.py:19)
4. **Game Initialization**: [`game_orchestrator.py`](src/game_orchestrator.py:1) reads config from environment, creates agents and logger, initializes a [`Game`](src/game.py:9) instance
5. **Game Loop**: [`game.py`](src/game.py:1) runs the main game loop:
   - Checks for game end conditions
   - Determines current player
   - Rolls dice using gnubg
   - Gets available moves, hints, and best moves from gnubg
   - Calls agent's [`choose_move()`](src/agents/base.py:23) method
   - Validates and executes the chosen move
   - Repeats until game ends or max turns reached
6. **Agent Decision**: Each agent type implements its own strategy:
   - **RandomAgent**: Picks randomly from valid moves
   - **BestMoveAgent**: Always picks best move according to gnubg engine
   - **LLMAgent**: Sends game state to external LLM for strategic analysis
   - **LiveCodeAgent**: Asks LLM to generate and execute Python code
7. **Logging**: Throughout execution, [`logger.py`](src/logger.py:1) records game events and debug information
8. **Results**: Game winner is determined and returned to [`main.py`](main.py:1) for statistics tracking

## gnubg Documentation

### Core Functions
- **[`gnubg.board()`](src/utils.py:86)** - Returns the current board state
- **[`gnubg.command(cmd)`](src/utils.py:171)** - Executes a gnubg command-line command
- **[`gnubg.evaluate()`](src/utils.py:36)** - Evaluates the current position
- **[`gnubg.match()`](src/utils.py:24)** - Returns information about the current match
- **[`gnubg.hint()`](src/utils.py:181)** - Gets move suggestions with equity evaluations
- **[`gnubg.posinfo()`](src/utils.py:43)** - Returns position information including current player and dice

### gnubg.board()
Returns 2 tuples of size 25. Each index represents the number of checkers in that position. The last index (24) represents the Bar (when a checker gets hit, it's sent to the middle bar).

The first tuple represents the current player's checkers, the second tuple represents the opponent's checkers. Use [`get_simple_board()`](src/utils.py:85) to get raw board data or [`default_board_representation()`](src/utils.py:123) for human-readable format.

### gnubg.command('cmd')
Executes any gnubg command. Common commands used in this project:
- `"new game"` - Starts a new game
- `"set player 0 human"` - Sets player 0 to human control
- `"set player 1 human"` - Sets player 1 to human control
- `"roll"` - Rolls the dice
- `"move X/Y"` - Moves a checker from point X to point Y
- `"play"` - Makes an automatic move

### gnubg.command('move move_cmd')
Executes a checker move using gnubg's move notation. The move command accepts various formats:

#### Basic Move Formats:
- **Single Move**: `"move 24/22"` - Move one checker from point 24 to point 22
- **Multiple Moves**: `"move 13/11 8/6"` - Move one checker from 13 to 11 AND one checker from 8 to 6
- **Same Point Multiple Moves**: `"move 6/4 6/4"` - Move two checkers from point 6 to point 4
- **Parenthetical Notation**: `"move 8/5(2)"` - Move two checkers from point 8 to point 5
- **Mixed Parenthetical**: `"move 13/10 8/5(3)"` - Move one checker from 13 to 10 AND three checkers from 8 to 5

#### Special Move Notations:
- **Hit and Move**: `"move 24/22*"` - Move from 24 to 22 and hit opponent's checker (the `*` indicates a hit)
- **Move from Bar**: `"move bar/22"` - Move a checker from the bar to point 22
- **Bear Off**: `"move 6/off"` - Bear off a checker from point 6 (when in bearing off phase)

#### Advanced Move Examples:
- **Complex Multi-Move**: `"move 13/11 24/22 8/6 6/4"` - Four separate moves in one turn (when doubles are rolled)
- **Hit and Continue**: `"move 24/22*/20"` - Move from 24 to 22 (hitting), then continue same checker to 20
- **Multiple Hits**: `"move 24/18*/17*"` - Move from 24 to 18 (hitting), then continue to 17 (hitting again)
- **Bar to Hit**: `"move bar/22*"` - Move from bar to point 22 and hit opponent's checker
- **Bar Multiple Hits**: `"move bar/20*/19*"` - Move from bar to 20 (hitting), then continue to 19 (hitting again)
- **Hit with Multiple Checkers**: `"move 8/2*(2)"` - Move two checkers from 8 to 2 and hit opponent's checker
- **Mixed Complex**: `"move 10/4(2) 8/2*(2)"` - Move 2 checkers from 10 to 4 AND move 2 checkers from 8 to 2 (hitting)

#### Move Validation:
- Moves must correspond to dice rolled (e.g., with dice 3,2 you can move 3 and 2 points)
- Cannot move to points occupied by 2+ opponent checkers
- Must move from bar first if any checkers are on the bar
- Must bear off legally when in home board and no checkers behind

#### Error Handling:
If an invalid move is provided, gnubg will ignore the command. Always use [`move_piece()`](src/utils.py:161) which includes error handling.

### gnubg.hint()
Returns detailed move analysis including:
- All possible moves with equity evaluations
- Win probabilities for each move
- Gammon probabilities
- Move quality rankings

Used by [`get_possible_moves()`](src/utils.py:179), [`get_hints()`](src/utils.py:193), and [`get_best_move()`](src/utils.py:207).

### gnubg.posinfo()
Returns position information including:
- Current player turn (0 or 1)
- Dice values
- Game state information

### gnubg.match()
Returns comprehensive match information including:
- Game history
- Current game state
- Winner information (when game ends)
- Score tracking

### Other gnubg Functions Used
- **[`gnubg.pip()`](src/utils.py:43)** - Returns pip count (distance to finish) for each player
- **[`gnubg.positionid()`](src/utils.py:50)** - Returns unique position identifier
- **[`gnubg.evaluate()`](src/utils.py:36)** - Returns detailed position evaluation


## What is an agent in the project context?
Agent will get as input these parameters:
1. only the board ( make sure no invalid move happen)
2. board and all possible moves
3. board + hints
4. board + best possible move


The agent will decide what to do with the above input + additional text(prompt), and will output a valid move
1. use gnubg engine only ( it will ignore the prompt)
2. use llm to decide
3. let an llm write code to solve the problem at hand


## Create new agents
If you want to add a new agent with different behavior, add a new file called "your_agent_name.py" to the agents folder under src, then add the import in the __init__.py file inside the agents folder.
In this file create an Agent class (for reference look into random_agent.py), lastly customize the
function choose_move as you wish.

## Custom Board Representation

The [`Game`](src/game.py:9) class supports custom board representation functions that can be passed during initialization. This allows teams to customize how the board state is displayed to their agents.

### How to Use Custom Board Representation

1. **Create a custom function** that takes no arguments and returns a string:
   ```python
   def my_custom_board_representation() -> str:
       # Your custom logic here
       board = get_simple_board()  # Get raw board data
       # Format the board as needed for your agent
       return f"Custom board format: {board}"
   ```

2. **Pass it to the Game class** during initialization, in file game_orchestrator:
   ```python
   game = Game(
       agent1=agent1,
       agent2=agent2,
       board_representation=my_custom_board_representation
   )
   ```
   
3. **Type hint specification**: The `board_representation` parameter accepts any function with the signature `Callable[[], str]` - meaning it takes no arguments and returns a string.

### Default Board Representation

If no custom function is provided, the game uses [`default_board_representation()`](src/utils.py:123) which provides a board of the format:
Backgammon board state:	1: O has 1	2: empty	3: O has 1	4: empty	5: empty	6: X has 5	7: empty	8: X has 3	9: empty	10: empty	11: empty	12: O has 4	13: X has 5	14: empty	15: empty	16: empty	17: O has 4	18: empty	19: O has 5	20: empty	21: empty	22: empty	23: empty	24: X has 2	Bar: X has 0, O has 0

This flexibility allows research teams to experiment with different board representations to see how they affect agent performance and decision-making.

## Features: 

### Run the game in batches
We could run the game loop more than once to get statistics on the ability of our agents.

### Run gnubg directly (not recommended)
using: gnubg -p main.py
will run gnubg directly without filtering any logs, only one game at a time.


### Debugging
Debugging the code is not simple because gnubg engine uses compiled binary files.
The solution for it is using ([pdb.](https://docs.python.org/3/library/pdb.html)).
Works only when running gnubg directly by writing ( gnubg -p main.py )
1. In the line you want to break write: breakpoint()
2. The program will break there in the console.


### Additional customization ( proceed with caution )
To change the code that runs, create a yourfile.py file in the src folder with a main function, you can check game_orchestrator.py for reference.
use game class to create a game, add agents and their configurations.
When you are done, change the import in the main.py file to your file.
In line 26 in main.py file: "from src.game_orchestrator import main" change to "from src.yourfile import main"

You can also change directly the code in game_orchestrator.py file.


## 🌐 Cloud Development Features

### GitHub Codespaces Benefits:
- ✅ **Full Ubuntu environment** with all dependencies pre-installed
- ✅ **VS Code in browser** with Python extensions
- ✅ **Instant setup** - no local installation needed
- ✅ **Team collaboration** - share workspaces easily
- ✅ **Consistent environment** - same setup for everyone

### Available Workflows:
1. **Demo Workflow** (`/.github/workflows/demo.yml`):
   - Runs automatically on push/PR
   - Manual trigger with custom agent selection
   - Tests installation and runs sample games

### Quick Commands in Cloud Environment:
```bash
# Run a single game
python3 main.py

# Run 3 games with debug mode
python3 main.py --a1 RandomAgent --a2 RandomAgent --n 3 --d

```

## 🔧 Development Container Details

The project includes a complete dev container configuration:
- **Base**: Ubuntu 22.04 with Python 3.11
- **Includes**: GNU Backgammon, Python dev tools, VS Code extensions
- **Auto-setup**: Runs [`setup.sh`](.devcontainer/setup.sh:1) on container creation
- **Ready-to-use**: No manual setup required


# Additional links
[gnubg offical python docs](https://www.gnu.org/software/gnubg/manual/html_node/Python-scripting.html)
