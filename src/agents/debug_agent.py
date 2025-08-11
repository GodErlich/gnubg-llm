from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..utils import random_move
from ..logger import logger


class DebugAgent(Agent):
    """Agent for debugging purposes, does not select moves but logs information."""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}):
        super().__init__(board_representation, inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        """ choose a random move from the possible moves """
        possible_moves = extra_input.get("possible_moves", [])
        hints = extra_input.get("hints", [])
        best_move = extra_input.get("best_move", None)
        logger.debug(f"{self.board_representation()}")
        logger.debug(f"Possible Moves: {possible_moves}")
        logger.debug(f"Hints: {hints}")
        logger.debug(f"Best Move: {best_move}")
        move = random_move()
        return move