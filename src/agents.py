from abc import ABC, abstractmethod
from .interfaces import AgentInputConfig, AgentInput
from .utils import default_board_representation, default_move, consult_llm
from .logger import logger

class Agent(ABC):
    """Abstract class for all agents."""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}):
        if board_representation is None:
            board_representation = default_board_representation
        self.board_representation = board_representation
        if inputs is not None:
            self.inputs = inputs


    @abstractmethod
    def choose_move(self, board, possible_moves=None, hints=None, prompt=None):
        pass

    def filter_inputs(self, possible_moves, hints, best_move):
        """Filter inputs based on the agent's configuration. DO NOTs use this method"""
        inputs = {"possible_moves": None, "hints": None, "best_move": None}
        if self.inputs is None:
            return inputs
        if self.inputs.get("possible_moves", False):
            inputs["possible_moves"] = possible_moves
        if self.inputs.get("hints", False):
            inputs["hints"] = hints
        if self.inputs.get("best_move", False):
            inputs["best_move"] = best_move
        
        return inputs

# custom agents
class GnuBGAgent(Agent):
    """Agent that uses gnubg to select moves"""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}):
        super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """Use gnubg to select a move."""
        move = default_move()
        return move

class LLMAgent(Agent):
    """Agent that uses an LLM to select moves (uses prompt if provided)."""
    def __init__(self, board_representation=None, inputs: AgentInputConfig = {},prompt=None, system_prompt=None):
        self.defaultPrompt = prompt
        self.system_prompt = system_prompt
        super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        try:
            board_repr = self.board_representation(board)
            possible_moves = extra_input.get("possible_moves", [])

            chosen_move_data = consult_llm(board_repr, prompt=self.defaultPrompt, system_prompt=self.system_prompt, possible_moves=possible_moves)

            if chosen_move_data:
                chosen_move = chosen_move_data["move"]
                logger.debug(f"Playing LLM-recommended move: {chosen_move}")
                return chosen_move

            else:
                logger.warning("No moves available")
                return None

        except Exception as e:
            logger.error(f"Error in play_llm_move: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None


class DebugAgent(Agent):
    """Agent for debugging purposes, does not select moves but logs information."""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}):
        super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """ choose a random move from the possible moves """
        possible_moves = extra_input.get("possible_moves", [])
        hints = extra_input.get("hints", [])
        best_move = extra_input.get("best_move", None)
        logger.debug(f"DebugAgent: {self.board_representation(board)}")
        logger.debug(f"DebugAgent: Possible Moves: {possible_moves}")
        logger.debug(f"DebugAgent: Hints: {hints}")
        logger.debug(f"DebugAgent: Best Move: {best_move}")
        move = default_move()
        return move

class RandomAgent(Agent):
    """Agent that uses gnubg to select moves"""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}):
            inputs["possible_moves"] = True # Random agent needs possible moves
            super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """ choose a random move from the possible moves """
        possible_moves = extra_input.get("possible_moves", [])
        if not possible_moves:
            logger.warning("No possible moves available for RandomAgent.")
            return None

        move = possible_moves[0] # possible moves is a list of random moves with no specific order
        return move


class LiveCodeAgent(Agent):
    """Agent that uses llm to write code, then executes it to select a move."""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}, prompt=None, system_prompt=None):
        self.defaultPrompt = prompt
        self.system_prompt = system_prompt
        super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """Use live code to select a move."""
        try:
            board_repr = self.board_representation(board)
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
        