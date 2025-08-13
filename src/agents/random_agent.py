import random
from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
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
