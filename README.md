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

## Important Files Explainations
1. setup.sh
This script does ...
because ...

2. requirments.txt
Please notice this is not a classic requirements.txt file. This file will install additional requirements to the
gnubg environment, This is needed because gnubg runs on its own seperated environment. This is why there is no
`gnubg` package in the requirements.txt file.

3. .env
This file will store url and secret key, that will allow it to ask the llm provider questions.
You have to create this file by yourself. Just duplicate `example.env` file change the name to .env
and put the real values in there.

# gnubg documentation

## all available commands + explain each one
    board(): Returns the current board state.
    command(cmd): Executes a gnubg command-line command.
    evaluate(): Evaluates the current position.
    match(): Returns information about the current match.

### gnubg.board() 
Returns 2 tuples of size 25. Each index represents the number of "pawns" in the position. The last index represents the Bar(When pawn gets eaten he is sent to the middle, which is called Bar)

The user could write a function that gets the board from gnubg, 
and output a text representation of the board.( there is imlemented default function for it called `default_board_representation`)

### gnubg.commnad('cmd')

### gnubg.move('move')

### 



## What is an agent?
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

## Run the game in batches
We could run the game loop more than once to get statistics on the ability of our agents.

# Debugging
Debugging the code is not simple because gnubg engine uses compiled binary files.
The solution for it is using ([pdb.](https://docs.python.org/3/library/pdb.html)).
Works only when running gnubg directly by writing ( gnubg -p main.py )
1. In the line you want to break write: breakpoint()
2. The program will break there in the console.


## Additional customization ( proceed with caution )
To change the code that runs, create a yourfile.py file in the src folder with a main function, you can check example.py for reference.
use game class to create a game, add agents and their configurations.
When you are done, change the import in the main.py file to your file.
In line 26 in main.py file: "from src.example import main" change to "from src.yourfile import main"

You can also change directly the code in example.py file.

## Additional links
[gnubg offical python docs](https://www.gnu.org/software/gnubg/manual/html_node/Python-scripting.html)
