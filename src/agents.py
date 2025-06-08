from abc import ABC, abstractmethod
from .utils import default_board_representation, log_message, default_move, move_piece, consult_llm

class Agent(ABC):
    """Abstract class for all agents."""

    def __init__(self, board_representation=None):
        if board_representation is None:
            board_representation = default_board_representation
        self.board_representation = board_representation

    @abstractmethod
    def choose_move(self, board=None, possible_moves=None, hints=None, prompt=None):
        pass

# costum agents
class GnuBGAgent(Agent):
    """Agent that uses gnubg to select moves"""

    def __init__(self, board_representation=None):
            super().__init__(board_representation)

    def choose_move(self, board=None, possible_moves=None):
        """Use gnubg to select a move."""
        move = default_move()
        return move

class LLMAgent(Agent):
    """Agent that uses an LLM to select moves (uses prompt if provided)."""
    def __init__(self, board_representation=None, prompt=None):
        self.defaultPrompt = prompt
        super().__init__(board_representation)

    def choose_move(self, board, possible_moves, hints=None):
        try:

            if not possible_moves:
                log_message("No moves could be found with any method")
                move = default_move()
                return move

            board_repr = self.board_representation(board)

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
