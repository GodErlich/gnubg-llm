from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..utils import consult_llm
from ..logger import logger


class LiveCodeAgent(Agent):
    """Agent that uses llm to write code, then executes it to select a move."""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}, prompt=None, system_prompt=None):
        self.defaultPrompt = prompt
        self.system_prompt = system_prompt
        super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """Use live code to select a move."""
        try:
            board_repr = self.board_representation()
            possible_moves = extra_input.get("possible_moves", [])
            hints = extra_input.get("hints", [])
            best_move = extra_input.get("best_move", None)
            
            create_code_prompt = """
            You are an expert backgammon player. Given the current board state, write a Python function that selects the best move.
            The function should take the board state as input and return the chosen move.
            The code should be well-structured and include error handling.
            The function should be named `choose_move` and should return a move in the format of a string.
            format should be like gnubg format, e.g. "24/22" or "13/9 24/22" for two moves.
            board_repr = {board_repr}
            """
            python_code = consult_llm(board_repr, prompt=create_code_prompt, system_prompt=self.system_prompt, possible_moves=possible_moves, hints=hints, best_move=best_move)
            logger.debug(f"Generated Python code: {python_code}")
            # Execute the generated code to get the move
            if python_code:
                next_move = exec(python_code)
                if next_move:
                    logger.debug(f"Playing LiveCode-recommended move: {next_move}")
                    return next_move
                else:
                    logger.warning("No move returned by LiveCode.")
                    return None

            logger.warning("python_code is empty or None.")
            return None

        except Exception as e:
            logger.error(f"Error in play_live_code_move: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None