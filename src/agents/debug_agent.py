from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..utils import random_move
from ..logger import logger


class BestMoveAgent(Agent):
    """Agent that always picks the "best move" according to gnubg engine"""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}):
        super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """ choose a random move from the possible moves """
        best_move = extra_input.get("best_move", None)
        logger.debug(f"Best Move: {best_move}")
        return best_move