this code/library uses gnubg module to create "agents" that each agent can play differently against gnubg.
it will be used by other developers to research 
different agents by themselves and let them play with each other
this is just an infrastructure for research.

we want the ability to initialize an agent.
agent will get as input this:
1. only the board ( make sure no invalid move happen)
2. board and all possible moves
3. board + hints
4. board + best possible move

also the user could write a function with input the board state (2 25 long tuples) 
and output text that is the board.( use my function for default)

the agent will decide what to do with the above input + additional text(prompt), and will output a valid move
1. use gnubg engine only ( it will ignore the prompt)
2. use llm to decide
3. let an llm write code to solve the problem at hand

also an ability to create a game with different agents
1. gnubg agent
2. any custom agent

also we could run the game loop few time by configuration in order to 
get statistics on the ability of our agents.

How to run?
prequisites:
docker desktop(installed and opened)
python3

open a terminal of the root folder of the project.
windows:
run build_and_run.bat
script starts running!

to change the code, just create your own file, you can check example.py for reference.
use game class to create a game, add agents, and when  you done change the import in main.py file to your file instead.