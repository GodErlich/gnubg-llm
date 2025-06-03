this code uses gnubg module to create "agents" that each agent can play differently against gnubg.

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