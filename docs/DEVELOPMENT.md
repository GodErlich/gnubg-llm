# 🔧 Development Guide

## Python Files Explanations

### Core Files
- **[`main.py`](../main.py)** - Entry point for batch game execution. Handles command-line arguments, manages multiple game runs, and provides statistics. Uses subprocess to run games silently via gnubg.
- **[`app.py`](../app.py)** - Bridge script that sets up the Python environment and imports the game logic. This is the file that gnubg actually executes with the `-p` flag.

### Source Directory ([`src/`](../src/))
- **[`game_orchestrator.py`](../src/game_orchestrator.py)** - Main game orchestrator that reads environment variables, creates agents, initializes logging, and starts a single game.
- **[`game.py`](../src/game.py)** - Core game loop implementation. Manages turns, dice rolling, move validation, and determines winners.
- **[`logger.py`](../src/logger.py)** - Singleton logger class that handles file and console logging with different severity levels.
- **[`interfaces.py`](../src/interfaces.py)** - TypedDict definitions for type safety across agent inputs and hint structures.

### Utils Directory ([`src/utils/`](../src/utils/))
The utils module has been restructured into separate files for better organization:
- **[`__init__.py`](../src/utils/__init__.py)** - Package initialization that exports all utility functions.
- **[`gnubg_utils.py`](../src/utils/gnubg_utils.py)** - Utility functions for gnubg command wrappers, board operations, and move validation.
- **[`llm_utils.py`](../src/utils/llm_utils.py)** - LLM integration utilities including API calls, response parsing, and schema validation.
- **[`game_utils.py`](../src/utils/game_utils.py)** - Game-specific utility functions for dice rolling, move generation, and game state management.

### Agents Directory ([`src/agents/`](../src/agents/))
- **[`base.py`](../src/agents/base.py)** - Abstract base class defining the agent interface, input filtering mechanism, and invalid move handling contract. All agents must implement both [`choose_move()`](../src/agents/base.py:18) and [`handle_invalid_move()`](../src/agents/base.py:22) methods.
- **[`random_agent.py`](../src/agents/random_agent.py)** - Simple agent that selects random valid moves from available options.
- **[`best_move_agent.py`](../src/agents/best_move_agent.py)** - Agent that always selects the gnubg engine's best move.
- **[`llm_agent.py`](../src/agents/llm_agent.py)** - AI agent that uses external LLM APIs to analyze positions and select moves based on strategic reasoning. Supports custom prompts and response schemas for structured output.
- **[`live_code_agent.py`](../src/agents/live_code_agent.py)** - Experimental agent that asks an LLM to generate Python code for move selection and executes it dynamically.
- **[`__init__.py`](../src/agents/__init__.py)** - Package initialization file that exports all agent classes.

## Project Flow

The project follows this execution flow:

1. **Entry Point**: [`main.py`](../main.py) parses command-line arguments and starts batch execution
2. **Game Launcher**: For each game, [`main.py`](../main.py) calls `gnubg -t -p app.py` with environment variables
3. **Environment Setup**: [`app.py`](../app.py) sets up Python paths and imports [`src.game_orchestrator.main`](../src/game_orchestrator.py:19)
4. **Game Initialization**: [`game_orchestrator.py`](../src/game_orchestrator.py) reads config from environment, creates agents and logger, initializes a [`Game`](../src/game.py:9) instance
5. **Game Loop**: [`game.py`](../src/game.py) runs the main game loop:
   - Checks for game end conditions
   - Determines current player
   - Rolls dice using gnubg
   - Gets available moves, hints, and best moves from gnubg
   - Calls agent's [`choose_move()`](../src/agents/base.py:18) method
   - Validates and executes the chosen move using [`move_piece()`](../src/utils/gnubg_utils.py:71) with retry logic
   - If move is invalid, calls agent's [`handle_invalid_move()`](../src/agents/base.py:22) method up to `MAX_RETIRES` times
   - Repeats until game ends or max turns reached
6. **Agent Decision**: Each agent type implements its own strategy:
   - **RandomAgent**: Picks randomly from valid moves
   - **BestMoveAgent**: Always picks best move according to gnubg engine
   - **LLMAgent**: Sends game state to external LLM for strategic analysis
   - **LiveCodeAgent**: Asks LLM to generate and execute Python code
7. **Logging**: Throughout execution, [`logger.py`](../src/logger.py) records game events and debug information
8. **Results**: Game winner is determined and returned to [`main.py`](../main.py) for statistics tracking

## gnubg Documentation

### Core Functions
- **[`gnubg.board()`](../src/utils/gnubg_utils.py:86)** - Returns the current board state
- **[`gnubg.command(cmd)`](../src/utils/gnubg_utils.py:171)** - Executes a gnubg command-line command
- **[`gnubg.match()`](../src/utils/gnubg_utils.py:24)** - Returns information about the current match
- **[`gnubg.hint()`](../src/utils/gnubg_utils.py:181)** - Gets move suggestions with equity evaluations
- **[`gnubg.posinfo()`](../src/utils/gnubg_utils.py:43)** - Returns position information including current player and dice

### gnubg.board()
Returns 2 tuples of size 25. Each index represents the number of checkers in that position. The last index (24) represents the Bar (when a checker gets hit, it's sent to the middle bar).

The first tuple represents the current player's checkers, the second tuple represents the opponent's checkers. Use [`get_simple_board()`](../src/utils/gnubg_utils.py:85) to get raw board data or [`default_board_representation()`](../src/utils/gnubg_utils.py:123) for human-readable format.

### gnubg.command('cmd')
Executes any gnubg command. Common commands used in this project:
- `"new game"` - Starts a new game
- `"set player 0 human"` - Sets player 0 to human control
- `"set player 1 human"` - Sets player 1 to human control
- `"roll"` - Rolls the dice
- `"move X/Y"` - Moves a checker from point X to point Y
- `"play"` - Makes an automatic move as last resort. If it's called something went wrong.

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
If an invalid move is provided, the [`move_piece()`](../src/utils/gnubg_utils.py:71) function implements a robust retry system:
- Validates move format using [`is_valid_move()`](../src/utils/game_utils.py) before execution
- Calls agent's [`handle_invalid_move()`](../src/agents/base.py:22) method when move is invalid
- Retries up to 3 times with agent-provided replacement moves
- Falls back to [`force_move()`](../src/utils/gnubg_utils.py:150) (gnubg auto play) if all attempts fail
- If `force_move` fails, the game throws an error and stops.

### gnubg.hint()
Returns detailed move analysis including:
- All possible moves with equity evaluations
- Win probabilities for each move
- Gammon probabilities
- Move quality rankings

Used by [`get_possible_moves()`](../src/utils/gnubg_utils.py:179), [`get_hints()`](../src/utils/gnubg_utils.py:193), and [`get_best_move()`](../src/utils/gnubg_utils.py:207).

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

## Create New Agents

If you want to add a new agent with different behavior, follow these steps:

1. **Create Agent File**: Add a new file called "your_agent_name.py" to the agents folder under src
2. **Import Agent**: Add the import in the `__init__.py` file inside the agents folder
3. **Implement Agent Class**: In this file create an Agent class (for reference look into `random_agent.py`)
4. **Customize Functions**: Implement the `choose_move` and `handle_invalid_move` methods as you wish
5. **Register Agent**: Add the agent class to the `create_agent` factory function in [`game_orchestrator.py`](../src/game_orchestrator.py)

### Agent Base Class
All agents must inherit from the base Agent class and implement:
- **[`choose_move()`](../src/agents/base.py:18)** - Main method for selecting moves
- **[`handle_invalid_move()`](../src/agents/base.py:22)** - Method for handling invalid move attempts

### Agent Invalid Move Handling System

The project implements a robust invalid move handling system that gives each agent full control over how to respond to invalid moves:

1. **Move Validation**: [`move_piece()`](../src/utils/gnubg_utils.py:71) validates each move using [`is_valid_move()`](../src/utils/game_utils.py) before execution
2. **Agent Control**: When a move is invalid, the agent's [`handle_invalid_move()`](../src/agents/base.py:22) method is called
3. **Retry Logic**: The system retries up to `MAX_RETRIES` times with agent-provided replacement moves
4. **Fallback**: If all attempts fail, [`force_move()`](../src/utils/gnubg_utils.py:150) triggers auto play

## Advanced Customization

## Custom Board Representation

The [`Game`](../src/game.py:9) class supports custom board representation functions that can be passed during initialization. This allows teams to customize how the board state is displayed to their agents.

### How to Use Custom Board Representation

1. **Create a custom function** that takes no arguments and returns a string:
   ```python
   def my_custom_board_representation() -> str:
       # Your custom logic here
       from src.utils import get_simple_board
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

If no custom function is provided, the game uses [`default_board_representation()`](../src/utils/gnubg_utils.py:123) which provides a board of the format:
`Backgammon board state:	1: O has 1	2: empty	3: O has 1	4: empty	5: empty	6: X has 5	7: empty	8: X has 3	9: empty	10: empty	11: empty	12: O has 4	13: X has 5	14: empty	15: empty	16: empty	17: O has 4	18: empty	19: O has 5	20: empty	21: empty	22: empty	23: empty	24: X has 2	Bar: X has 0, O has 0`


### Additional Customization (Proceed with caution)
To change the code that runs:
1. Create a `yourfile.py` file in the src folder with a main function
2. Check `game_orchestrator.py` for reference
3. Use game class to create a game, add agents and their configurations
4. Change the import in the `main.py` file to your file
5. In line 26 in `main.py` file: `"from src.game_orchestrator import main"` change to `"from src.yourfile import main"`

You can also change directly the code in `game_orchestrator.py` file.

## Development Environment

### Local Development
- Use `make all` for complete setup
- Use `make help` to see all available build targets
- Use `make status` to check installation status

### Cloud Development
- Gitpod integration for instant development
- Google collab for understanding the project

### Debugging
Debugging the code is not simple because gnubg engine uses compiled binary files.
The solution is using [pdb](https://docs.python.org/3/library/pdb.html):
- Works only when running gnubg directly: `gnubg -p main.py`
1. In the line you want to break write: `breakpoint()`
2. The program will break there in the console

## Testing
- Use the demo notebook for quick testing
- Run batch games with `--number_of_games` for statistical analysis
- Use debug mode (`--debug_mode` or `--d`) for detailed logging
- Use JSON logs (`--json_logs`) for easier parsing and analysis

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

This comprehensive setup is necessary because gnubg requires specific compilation flags and system libraries to enable Python scripting support. Currently there is no other way to install gnubg full engine. There is a PyPi package of gnubg, but the package can't run game, only evaluate them.

### 2. requirements.txt
Please notice this is not a classic requirements.txt file. This file will install additional requirements to the gnubg environment, This is needed because gnubg runs on its own seperated environment. This is why there is no `gnubg` package in the requirements.txt file.

### 3. .env
This file will store url and secret key, that will allow it to ask the llm provider questions. You have to create this file by yourself. Just duplicate `example.env` file change the name to .env and put the real values in there.
