from typing import TypedDict, List, Optional
import time

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

class PlayerStatistics(TypedDict):
    name: str
    invalid_moves: int
    total_moves: int
    checkers_remaining: int
    checkers_on_bar: int
    pip_count: int
    cube_decisions: int
    cube_accepts: int
    cube_rejects: int

class GameStatistics(TypedDict):
    game_id: int
    winner: int
    loser: int
    winner_name: str
    loser_name: str
    total_turns: int
    game_duration: float
    player1_stats: PlayerStatistics
    player2_stats: PlayerStatistics
    final_score_difference: int
    game_type: str  # "normal", "gammon", "backgammon"
