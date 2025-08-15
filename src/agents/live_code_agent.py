from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..utils import consult_llm
from ..utils.gnubg_utils import random_valid_move, get_best_move
from ..logger import logger
import re


class LiveCodeAgent(Agent):
    """Agent that uses llm to write code, then executes it to select a move."""

    def __init__(self, inputs: AgentInputConfig = {}, prompt=None, system_prompt=None):
        self.defaultPrompt = prompt
        self.system_prompt = system_prompt or "You are an expert backgammon AI that writes Python code."
        super().__init__(inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """Use live code to select a move."""
        try:
            possible_moves = extra_input.get("possible_moves", []) if extra_input else []
            hints = extra_input.get("hints", []) if extra_input else []
            best_move = extra_input.get("best_move", None) if extra_input else None
            
            # Create a comprehensive prompt for code generation
            create_code_prompt = f"""
You are an expert backgammon player. Write Python code to analyze the board and select the best move.

Current board state: {board}
Available moves: {possible_moves}
Move hints with equity: {hints}
Engine's best move: {best_move}

Write a Python function that analyzes this information and returns the best move as a string.
The function must be named 'select_best_move' and should:
1. Take no parameters 
2. Return a move string in gnubg format (e.g., "24/22" or "13/9 24/22")
3. Choose from the available moves list if provided
4. Include your reasoning as comments

Example format:
```python
def select_best_move():
    # Analysis of the position
    available = {possible_moves}
    hints = {hints}
    best = "{best_move}"
    
    # Your strategic reasoning here
    if available:
        # Choose from available moves based on strategy
        return available[0]  # or your chosen move
    return best if best else None
```

Only return the Python code, no explanations outside the code.
"""

            answer_schema = {
                "python_code": "str"
            }
            
            llm_response = consult_llm(
                board, 
                prompt=create_code_prompt, 
                system_prompt=self.system_prompt,
                possible_moves=possible_moves, 
                hints=hints, 
                best_move=best_move,
                schema=answer_schema
            )
            logger.debug(f"LLM response: {llm_response}")

            if not llm_response or "python_code" not in llm_response:
                logger.warning("No valid code returned by LLM")
                return None
            
            python_code = llm_response["python_code"]
            logger.debug(f"Generated Python code: {python_code}")
            
            # Execute the generated code safely
            chosen_move = self._execute_code_safely(python_code, possible_moves, best_move)
            
            if chosen_move:
                logger.debug(f"LiveCodeAgent selected move: {chosen_move}")
                return chosen_move
            else:
                logger.warning("Code execution did not return a valid move")
                return None

        except Exception as e:
            logger.error(f"Error in LiveCodeAgent choose_move: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _execute_code_safely(self, python_code: str, possible_moves: list, best_move: str) -> str:
        """Safely execute the generated Python code and extract the move."""
        try:
            # Create a restricted execution environment
            safe_globals = {
                '__builtins__': {
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'max': max,
                    'min': min,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'range': range,
                }
            }
            
            # Execute the code in the safe environment
            exec(python_code, safe_globals)
            
            # Call the function if it exists
            if 'select_best_move' in safe_globals:
                result = safe_globals['select_best_move']()
                if isinstance(result, str) and result.strip():
                    return result.strip()
            
            logger.warning("Function 'select_best_move' not found or returned invalid result")
            return None
            
        except Exception as e:
            logger.error(f"Error executing generated code: {e}")
            return None

    def handle_invalid_move(self, invalid_move: str) -> str:
        """Handle invalid moves by trying best move, then random move."""
        logger.info(f"LiveCodeAgent handling invalid move: '{invalid_move}'")

        # Try random move
        try:
            random_move = random_valid_move()
            if random_move:
                logger.debug(f"LiveCodeAgent falling back to random move: {random_move}")
                return random_move
        except Exception as e:
            logger.warning(f"Failed to get random move: {e}")
        
        return None