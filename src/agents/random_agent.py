import random
from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..utils.gnubg_utils import random_valid_move
from ..logger import logger


class RandomAgent(Agent):
    """Agent that uses gnubg to select moves"""

    def __init__(self, inputs: AgentInputConfig = {}):
            super().__init__(inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """ choose a random move from the possible moves """
        possible_moves = extra_input.get("possible_moves", [])
        move = self.random_move(possible_moves)
        logger.debug(f"Random Move: {move}")
        return move

    def random_move(self, possible_moves):
        """ makes a random move based on possible moves"""
        if not possible_moves or len(possible_moves) == 0:
            logger.info("No possible moves found")
            return None

        random_index = random.randint(0, len(possible_moves) - 1)

        return possible_moves[random_index]

    def handle_invalid_move(self, invalid_move: str) -> str:
        """RandomAgent tries another random move."""
        logger.debug(f"RandomAgent handling invalid move: '{invalid_move}'")

        try:
            new_random_move = random_valid_move()
            if new_random_move:
                logger.debug(f"RandomAgent falling back to a random move: {new_random_move}")
                return new_random_move
        except Exception as e:
            logger.warning(f"Failed to get new random move: {e}")

        logger.warning("RandomAgent could not handle invalid move")
        return None
