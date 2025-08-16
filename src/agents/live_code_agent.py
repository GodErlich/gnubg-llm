from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..utils import consult_llm
from ..utils.gnubg_utils import get_board, random_valid_move
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
            tuple_board = get_board()
            possible_moves = extra_input.get("possible_moves", []) if extra_input else []
            hints = extra_input.get("hints", []) if extra_input else []
            best_move = extra_input.get("best_move", None) if extra_input else None
            
            # Create a comprehensive prompt for code generation
            create_code_prompt = f"""
                You are an expert backgammon player. Write Python code to analyze the board and select the best move.

                Current board state: {board}
                Available moves: {possible_moves}

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
                    tuple_board = {tuple_board}
                    available = {possible_moves}
                    move = None

                    # Your strategic reasoning here
                    if available:
                        # Calculate the best move from available and tuple_board
                        return available[0]  # or your chosen move
                    return move
                ```

                Only return the Python code, no explanations outside the code.
                """
            
            llm_response = consult_llm(
                board, 
                prompt=create_code_prompt, 
                system_prompt=self.system_prompt,
                possible_moves=possible_moves, 
                hints=hints,
                best_move=best_move,
                tuple_board=tuple_board
            )
            logger.debug(f"LLM response: {llm_response}")

            if not llm_response:
                logger.warning("No valid code returned by LLM")
                return None
            
            # Extract Python code from markdown if present
            python_code = self._extract_python_code(llm_response)
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

    def _extract_python_code(self, response: str) -> str:
        """Extract Python code from markdown code blocks or plain text."""
        if not response:
            return ""
        
        # Check if response contains markdown code blocks
        python_block_pattern = r'```python\s*\n(.*?)```'
        code_block_pattern = r'```\s*\n(.*?)```'
        
        # Try to find Python-specific code block first
        python_match = re.search(python_block_pattern, response, re.DOTALL)
        if python_match:
            extracted = python_match.group(1).strip()
            logger.debug(f"Extracted Python code from ```python block: {extracted[:100]}...")
            return extracted
        
        # Try to find any code block
        code_match = re.search(code_block_pattern, response, re.DOTALL)
        if code_match:
            extracted = code_match.group(1).strip()
            logger.debug(f"Extracted code from ``` block: {extracted[:100]}...")
            return extracted
        
        # If no code blocks found, return the response as-is (might be plain code)
        logger.debug(f"No code blocks found, using response as-is: {response[:100]}...")
        return response.strip()

    def _execute_code_safely(self, python_code: str, possible_moves: list, best_move: str) -> str:
        """Safely execute the generated Python code and extract the move."""
        try:
            if not python_code or not python_code.strip():
                logger.warning("Empty Python code provided")
                return None
            
            logger.debug(f"About to execute code: {python_code[:200]}...")
            
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
                    'print': print,  # Allow print for debugging
                }
            }
            
            # Execute the code in the safe environment
            exec(python_code, safe_globals)
            logger.debug(f"Code executed successfully. Available functions: {[k for k in safe_globals.keys() if callable(safe_globals.get(k))]}")
            
            # Call the function if it exists
            if 'select_best_move' in safe_globals:
                logger.debug("Found select_best_move function, calling it...")
                result = safe_globals['select_best_move']()
                logger.debug(f"Function returned: {result} (type: {type(result)})")
                
                if isinstance(result, str) and result.strip():
                    final_move = result.strip()
                    logger.debug(f"Returning valid move: {final_move}")
                    return final_move
                else:
                    logger.warning(f"Function returned invalid result: {result}")
            else:
                available_funcs = [k for k in safe_globals.keys() if callable(safe_globals.get(k))]
                logger.warning(f"Function 'select_best_move' not found. Available functions: {available_funcs}")
            
            return None
            
        except SyntaxError as e:
            logger.error(f"Syntax error in generated code: {e}")
            logger.error(f"Problematic code:\n{python_code}")
            return None
        except Exception as e:
            logger.error(f"Error executing generated code: {e}")
            logger.error(f"Code that failed:\n{python_code}")
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