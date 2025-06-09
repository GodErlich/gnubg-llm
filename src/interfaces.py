from typing import TypedDict, List

class Hint(TypedDict):
    move: str
    equity: int

class AgentInputConfig(TypedDict):
    possible_moves: bool
    hints: bool
    best_move: bool

class AgentInput(TypedDict):
    possible_moves: List[str] | None
    hints: List[Hint] | None
    best_move: str | None
