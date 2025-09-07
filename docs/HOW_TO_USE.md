# 📖 How to Use the GNU Backgammon Research Environment

## Basic Usage

### How to run?
1. Make sure you are inside the root folder of the project
2. Make sure you ran the setup. If not run: `make all`
3. In the terminal write: `python3 main.py`
4. If you wish to stop the run in the middle, just click `Ctrl + c` in the terminal.

## Run configurations

There are several parameters that can be passed to the program:

```
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
  --prompt, --p         Custom prompt for the LLM agent (default: None)
  --system_prompt, --sp Custom system prompt for the LLM agent (default: None)
  --possible_moves, --pm Enable possible moves input for agents
  --hints, --hi         Enable hints input for agents
  --best_move, --bm     Enable best move input for agents
  --json_logs, --json   Use JSON format for logs (better for parsing)
```

## Examples:

### Basic Examples:
- `python3 main.py --a1 RandomAgent --a2 RandomAgent --n 3 --d`
  Will run 3 games with RandomAgent vs RandomAgent and debug logs.
- `python3 main.py --a1 LLMAgent --a2 BestMoveAgent --p "Play aggressively" --sp "You are a backgammon expert" --pm --hi`
  Will run LLM agent with custom prompts and additional input (possible moves and hints).
- `python3 main.py --a1 LiveCodeAgent --a2 RandomAgent --pm --hi --bm --d --json`
  Will run LiveCodeAgent with all inputs and JSON-formatted logs for easier parsing.

## Advanced LLM Features

### Notice!
To run Agents that use LLM you have to create a .env file with your parameters.
Just duplicate `example.env` file, change the duplicated file name to .env and put the real values in there.

### Custom Prompts
You can provide custom prompts and system prompts for LLM agents:
- Use `--prompt` or `--p` to set a custom user prompt
- Use `--system_prompt` or `--sp` to set a custom system prompt

### Response Schema Support
The LLM agent supports structured response schemas. When using a schema, the LLM will attempt to return JSON-formatted responses that match the expected structure. This enables more reliable parsing of complex agent responses beyond simple move selection.

### Agent Input Configuration
Control what information is provided to agents:
- `--possible_moves` (`--pm`): Provides list of all valid moves
- `--hints` (`--hi`): Provides move quality hints and evaluations
- `--best_move` (`--bm`): Provides the engine's recommended best move

### Logging Options
Configure log output format for easier parsing:
- `--json_logs` (`--json`): Output logs in JSON format for easier programmatic parsing
- Standard format: `[2025-08-16 00:52:45] - DEBUG: Generated Python code: def select_best_move():\n    return "24/23"`
- JSON format: `{"timestamp": "2025-08-16 00:52:45", "level": "DEBUG", "message": "Generated Python code: def select_best_move():\n    return \"24/23\""}`

JSON logs preserve original formatting including newlines and make it easier to parse log data programmatically.

## Available Agent Types

### 1. RandomAgent
- Simple agent that selects random valid moves from available options
- Good for testing and baseline comparison

### 2. BestMoveAgent  
- Agent that always selects the gnubg engine's best move
- Represents optimal play according to GNU Backgammon

### 3. LLMAgent
- AI agent that uses external LLM APIs to analyze positions and select moves
- Supports custom prompts and response schemas for structured output
- Requires `.env` file with LLM provider credentials

### 4. LiveCodeAgent
- Experimental agent that asks an LLM to generate Python code for move selection
- Executes the generated code dynamically
- Useful for research into code-generation approaches

## Agent Input Types

Agents can receive different levels of information based on configuration:

1. **Only the board** - Basic board state (ensures no invalid moves happen)
2. **Board and all possible moves** - Board state plus list of valid moves
3. **Board + hints** - Board state plus move quality evaluations
4. **Board + best possible move** - Board state plus the engine's recommended move

The agent will decide what to do with the above input plus additional text (prompt), and will output a move accordingly.

## Game Run Evaluation Script

This script (`evaluate_runs.py`) evaluates backgammon games based on files inside `run_timestamp` folders, using the `game_stats.json` files to create comprehensive analysis similar to the `game_results` functionality in [`main.py`](main.py).

### Basic Usage

```bash
# Analyze all runs with detailed output
python3 evaluate_runs.py

# Analyze specific run folder
python3 evaluate_runs.py --run run_20250907_185349

# Analyze all runs with comparison and quiet output
python3 evaluate_runs.py --compare --quiet
```


### Command Line Options

- `--output_dir DIR` or `--dir DIR`: Directory containing run folders (default: `output`)
- `--run_folder RUN` or `--run RUN`: Analyze specific run folder
- `--compare` or `--comp`: Compare performance across runs
- `--quiet` or `--q`: Suppress detailed output, show summary only

### Game-by-Game Results
Similar to [`main.py`](main.py:156-181) format:
- Game ID, Winner, Loser
- Duration, Turns
- Invalid moves (P1/P2)
- Checkers remaining for loser
- Game type (normal/gammon/backgammon)

### Aggregate Statistics
- Average game duration and turns
- Total and rate of invalid moves per agent
- Game type distribution

### Run Comparison (with `--compare`)
- Performance comparison across multiple runs
- Best performers identification
- Average game speed analysis
