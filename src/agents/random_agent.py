from ..utils import random_move
from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..logger import logger


class RandomAgent(Agent):
    """Agent that uses gnubg to select moves"""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}):
            inputs["possible_moves"] = True # Random agent needs possible moves
            super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """ choose a random move from the possible moves """
        move = random_move()
        return move