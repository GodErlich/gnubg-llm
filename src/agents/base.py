from abc import ABC, abstractmethod
from ..interfaces import AgentInputConfig


class Agent(ABC):
    """Abstract class for all agents."""

    def __init__(self, inputs: AgentInputConfig = {}):
        self.inputs = inputs

    def __str__(self):
        return self.__class__.__name__
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @abstractmethod
    def choose_move(self, board, possible_moves=None, hints=None, prompt=None):
        raise NotImplementedError("Subclasses must implement choose_move method")

    @abstractmethod
    def handle_invalid_move(self, invalid_move: str) -> str:
        raise NotImplementedError("Subclasses must implement handle_invalid_move method")

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