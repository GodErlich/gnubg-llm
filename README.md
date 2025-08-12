This code uses [gnubg module](https://www.gnu.org/software/gnubg/) to create backgamon "agents".

It will be used by other developers to research different agents by themselves and let them play
against each other.
This code is an infrastructure for research.


## Prequisites:
## Windows OS
1. Install WSL2 + Ubuntu 22.04 (you can run: `wsl --install Ubuntu-22.04` or install manually)
2. Follow linux quick start

## Linux(Ubunto) OS
1. None

## Quick start
Open bash where you want to clone the project. (Windows users open WSL). Then run the following commands:
1. git clone https://github.com/GodErlich/gnubg-llm.git
2. cd gnubg-llm
3. chmod +x setup.sh && ./setup.sh # might take some time

Now to open in vscode write: `code .` or open the cloned project with your favorite IDE

## How to run?
1. Make sure you are inside the root folder of the project
2. Make sure you ran the setup.sh file. If not run: `chmod +x setup.sh && ./setup.sh`
3. In the terminal write: `python3 main.py`
4. If you wish to stop the run in the middle, just click `Ctrl + c` in the terminal.

## Run configurations
There are few parameters that can be passed to the program.
  -h, --help            show this help message and exit
  --log_file_name, --fn  LOG_FILE_NAME,
                        Name for the log file (default: game)
  --log_folder_path, --fp LOG_FOLDER_PATH,
                        Folder path for logs (default: output)
  --agent1, --a1 {DebugAgent,RandomAgent,LLMAgent,LiveCodeAgent},
                        Agent type for player 1 (default: DebugAgent)
  --agent2, --a2 {DebugAgent,RandomAgent,LLMAgent,LiveCodeAgent},
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

### 1. setup.sh
This script sets up the complete GNU Backgammon development environment by:
- Installing system dependencies (Python 3, build tools, libraries required for gnubg compilation)
- Downloading and compiling GNU Backgammon from source with Python bindings enabled
- Installing Python package dependencies globally (needed because gnubg has embedded Python)
- Testing the installation to ensure everything works correctly

This comprehensive setup is necessary because gnubg requires specific compilation flags and system libraries to enable Python scripting support.

### 2. requirements.txt
Please notice this is not a classic requirements.txt file. This file will install additional requirements to the
gnubg environment, This is needed because gnubg runs on its own seperated environment. This is why there is no
`gnubg` package in the requirements.txt file.

3. .env
This file will store url and secret key, that will allow it to ask the llm provider questions.
You have to create this file by yourself. Just duplicate `example.env` file change the name to .env
and put the real values in there.

## Python Files Explanations

### Core Files
- **[`main.py`](main.py:1)** - Entry point for batch game execution. Handles command-line arguments, manages multiple game runs, and provides statistics. Uses subprocess to run games silently via gnubg.
- **[`app.py`](app.py:1)** - Bridge script that sets up the Python environment and imports the game logic. This is the file that gnubg actually executes with the `-p` flag.

### Source Directory ([`src/`](src/))
- **[`example.py`](src/example.py:1)** - Main game orchestrator that reads environment variables, creates agents, initializes logging, and starts a single game.
- **[`game.py`](src/game.py:1)** - Core game loop implementation. Manages turns, dice rolling, move validation, and determines winners.
- **[`utils.py`](src/utils.py:1)** - Utility functions for board operations, move validation, LLM integration, and gnubg command wrappers.
- **[`logger.py`](src/logger.py:1)** - Singleton logger class that handles file and console logging with different severity levels.
- **[`interfaces.py`](src/interfaces.py:1)** - TypedDict definitions for type safety across agent inputs and hint structures.

### Agents Directory ([`src/agents/`](src/agents/))
- **[`base.py`](src/agents/base.py:1)** - Abstract base class defining the agent interface and input filtering mechanism.
- **[`random_agent.py`](src/agents/random_agent.py:1)** - Simple agent that selects random valid moves from available options.
- **[`debug_agent.py`](src/agents/debug_agent.py:1)** - Development agent that logs detailed game state information while making random moves.
- **[`llm_agent.py`](src/agents/llm_agent.py:1)** - AI agent that uses external LLM APIs to analyze positions and select moves based on strategic reasoning.
- **[`live_code_agent.py`](src/agents/live_code_agent.py:1)** - Experimental agent that asks an LLM to generate Python code for move selection and executes it dynamically.
- **[`__init__.py`](src/agents/__init__.py:1)** - Package initialization file that exports all agent classes.

## Project Flow

The project follows this execution flow:

1. **Entry Point**: [`main.py`](main.py:1) parses command-line arguments and starts batch execution
2. **Game Launcher**: For each game, [`main.py`](main.py:1) calls `gnubg -t -p app.py` with environment variables
3. **Environment Setup**: [`app.py`](app.py:1) sets up Python paths and imports [`src.example.main`](src/example.py:19)
4. **Game Initialization**: [`example.py`](src/example.py:1) reads config from environment, creates agents and logger, initializes a [`Game`](src/game.py:9) instance
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
   - **DebugAgent**: Logs detailed information then picks randomly
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

#### Special Move Notations:
- **Hit and Move**: `"move 24/22*"` - Move from 24 to 22 and hit opponent's checker (the `*` indicates a hit)
- **Move from Bar**: `"move bar/22"` - Move a checker from the bar to point 22
- **Bear Off**: `"move 6/off"` - Bear off a checker from point 6 (when in bearing off phase)

#### Advanced Move Examples:
- **Complex Multi-Move**: `"move 13/11 24/22 8/6 6/4"` - Four separate moves in one turn (when doubles are rolled)
- **Hit and Continue**: `"move 24/22*/20"` - Move from 24 to 22 (hitting), then continue same checker to 20
- **Bar to Hit**: `"move bar/22*"` - Move from bar to point 22 and hit opponent's checker

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

## Features: 

### Run the game in batches
We could run the game loop more than once to get statistics on the ability of our agents.

### Debugging
Debugging the code is not simple because gnubg engine uses compiled binary files.
The solution for it is using ([pdb.](https://docs.python.org/3/library/pdb.html)).
Works only when running gnubg directly by writing ( gnubg -p main.py )
1. In the line you want to break write: breakpoint()
2. The program will break there in the console.


### Additional customization ( proceed with caution )
To change the code that runs, create a yourfile.py file in the src folder with a main function, you can check example.py for reference.
use game class to create a game, add agents and their configurations.
When you are done, change the import in the main.py file to your file.
In line 26 in main.py file: "from src.example import main" change to "from src.yourfile import main"

You can also change directly the code in example.py file.


# Additional links
[gnubg offical python docs](https://www.gnu.org/software/gnubg/manual/html_node/Python-scripting.html)
