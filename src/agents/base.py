from abc import ABC, abstractmethod
from ..interfaces import AgentInputConfig, AgentInput
from ..utils import default_board_representation


class Agent(ABC):
    """Abstract class for all agents."""

    def __init__(self, board_representation=None, inputs: AgentInputConfig = {}):
        if board_representation is None:
            board_representation = default_board_representation
        self.board_representation = board_representation
        if inputs is not None:
            self.inputs = inputs

    def __str__(self):
        return self.__class__.__name__
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @abstractmethod
    def choose_move(self, board, possible_moves=None, hints=None, prompt=None):
        pass

    def choose_cube_action(self, board, cube_decision):
        """Choose cube action (double, accept, decline). Default: conservative approach."""
        decision_type = cube_decision.get("decision_type", "unknown")
        
        if decision_type == "take_decision":
            # Someone offered us a double - decline it (conservative)
            return "decline"
        elif decision_type == "double_decision":
            # We can offer a double - don't offer it (conservative)
            return "no_double"
        else:
            # Unknown decision - be conservative
            return "decline"

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