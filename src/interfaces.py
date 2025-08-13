from typing import TypedDict, List, Union, Optional

class Hint(TypedDict):
    move: str
    equity: int

class AgentInputConfig(TypedDict):
    possible_moves: bool
    hints: bool
    best_move: bool

class AgentInput(TypedDict):
    possible_moves: Optional[List[str]]
    hints: Optional[List[Hint]]
    best_move: Optional[str]
