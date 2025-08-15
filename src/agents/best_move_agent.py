from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..utils.gnubg_utils import random_valid_move
from ..logger import logger


class BestMoveAgent(Agent):
    """Agent that always picks the "best move" according to gnubg engine"""

    def __init__(self, inputs: AgentInputConfig = {}):
        super().__init__(inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """ choose a random move from the possible moves """
        best_move = extra_input.get("best_move", None)
        logger.debug(f"Best Move: {best_move}")
        return best_move

    def handle_invalid_move(self, invalid_move: str) -> str:
        """BestMoveAgent tries random move, then gives up for gnubg auto play."""
        # Try a random valid move as fallback
        logger.debug(f"BestMoveAgent handling invalid move: '{invalid_move}'")
        try:
            random_move = random_valid_move()
            if random_move:
                logger.debug(f"BestMoveAgent falling back to a random move: {random_move}")
                return random_move
        except Exception as e:
            logger.warning(f"Failed to get random move: {e}")
        
        # If random move fails, return None to trigger gnubg auto play
        logger.info("BestMoveAgent could not handle invalid move")
        return None