from typing import TypedDict, List, Optional

class Hint(TypedDict):
    move: str
    equity: int

class CubeDecision(TypedDict):
    decision_type: str  # "double_decision" or "take_decision"
    can_double: bool
    cube_value: int
    cube_owner: Optional[str]

class AgentInputConfig(TypedDict):
    possible_moves: bool
    hints: bool
    best_move: bool

class AgentInput(TypedDict):
    possible_moves: Optional[List[str]]
    hints: Optional[List[Hint]]
    best_move: Optional[str]
