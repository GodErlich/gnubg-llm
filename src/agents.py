from abc import ABC, abstractmethod
import time
from .interfaces import AgentInputConfig, AgentInput
from .utils import default_board_representation, log_message, default_move, consult_llm

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
        """Filter inputs based on the agent's configuration. do not use this method"""
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

# costum agents
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
    def __init__(self, board_representation=None, inputs: AgentInputConfig = {},prompt=None):
        self.defaultPrompt = prompt
        super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        try:
            board_repr = self.board_representation(board)
            possible_moves = extra_input.get("possible_moves", [])

            chosen_move_data = consult_llm(board_repr, possible_moves)

            if chosen_move_data:
                chosen_move = chosen_move_data["move"]
                log_message(f"Playing LLM-recommended move: {chosen_move}")
                return chosen_move

            else:
                log_message("No moves available")
                return None

        except Exception as e:
            log_message(f"Error in play_llm_move: {e}")
            import traceback

            log_message(traceback.format_exc())
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
        log_message(f"DebugAgent: Board Representation: {self.board_representation(board)}")
        log_message(f"DebugAgent: Possible Moves: {possible_moves}")
        log_message(f"DebugAgent: Hints: {hints}")
        log_message(f"DebugAgent: Best Move: {best_move}")
        time.sleep(10)  # Simulate processing time
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
            log_message("No moves could be found with any method")
            move = default_move()
            return move

        move = possible_moves[0] # possible moves is a list of random moves
        return move


class LiveCodeAgent(Agent):
    """Agent that uses llm to write code, then executes it to select a move."""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}, prompt=None):
        self.defaultPrompt = prompt
        super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """Use live code to select a move."""
        try:
            board_repr = self.board_representation(board)
            possible_moves = extra_input.get("possible_moves", [])
            hints = extra_input.get("hints", [])
            best_move = extra_input.get("best_move", None)

            chosen_move_data = consult_llm(board_repr, possible_moves, )

            if chosen_move_data:
                chosen_move = chosen_move_data["move"]
                log_message(f"Playing LiveCode-recommended move: {chosen_move}")
                return chosen_move

            else:
                log_message("No moves available")
                return None

        except Exception as e:
            log_message(f"Error in play_live_code_move: {e}")
            import traceback

            log_message(traceback.format_exc())
            return None
        