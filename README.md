This code uses [gnubg module](https://www.gnu.org/software/gnubg/) to create backgamon "agents".

It will be used by other developers to research different agents by themselves and let them play
against each other.
This code is an infrastructure for research.


## Prequisites:
## Windows OS
1. Install WSL2 + Ubuntu 22.04
2. Follow linux quick start

## Linux(Ubunto) OS


## Quick start
Open bash where you want to clone the project. (Windows users open WSL). Then run the following commands:
1. git clone https://github.com/GodErlich/gnubg-llm.git
2. cd gnubg-llm  
3. chmod +x setup.sh && ./setup.sh # might take some time

Now to open in vscode write: `code .` or open the gnubg-llm folder with your favorite IDE

## How to run?
1. Make sure you are inside the root folder of the project (gnubg-llm)
2. Make sure you ran the setup.sh file. If not run: `chmod +x setup.sh && ./setup.sh`
3. In the terminal write: `python3 main.py`

# How to debug?
Debugging the code is not simple because gnubg engine uses compiled binary files.
The solution for it is using ([pdb.](https://docs.python.org/3/library/pdb.html)).
Works only when running gnubg directly by writing ( gnubg -p main.py )
1. In the line you want to break write: breakpoint()
2. The program will break there in the console.


## What is the board?
also the user could write a function with input the board state (2 25 long tuples) 
and output text that is the board.( use my function for default)

## What is an agent?
Agent will get as input these parameters:
1. only the board ( make sure no invalid move happen)
2. board and all possible moves
3. board + hints
4. board + best possible move


the agent will decide what to do with the above input + additional text(prompt), and will output a valid move
1. use gnubg engine only ( it will ignore the prompt)
2. use llm to decide
3. let an llm write code to solve the problem at hand


## Create new agents
If you want to add a new agent with different behavior, add a new file called "your_agent_name.py" to the agents folder under src, then add the import in the __init__.py file inside the agents folder.
In this file create an Agent class (for reference look into random_agent.py), lastly customize the
function choose_move as you wish.

## Run the game in batches
We could run the game loop more than once to get statistics on the ability of our agents.


## Additional customization ( proceed with caution )
To change the code that runs, create a yourfile.py file in the src folder with a main function, you can check example.py for reference.
use game class to create a game, add agents and their configurations.
When you are done, change the import in the main.py file to your file.
In line 26 in main.py file: "from src.example import main" change to "from src.yourfile import main"

You can also change directly the code in example.py file.
