import gnubg
from typing import List, Optional, Tuple
import random


from ..agents import Agent
from .game_utils import is_valid_move
from ..interfaces import Hint, PlayerStatistics
from ..logger import logger


MAX_RETRIES = 3

def get_dice() -> Tuple[int, int]:
    """Get the current dice rolled."""
    posinfo = gnubg.posinfo()
    dice = posinfo["dice"]
    if dice is None or len(dice) < 2:
        logger.warning("No dice rolled yet.")
        return None
    return dice

def reverse_board(board: Tuple[int, int]) -> Tuple[int, int]:
    """Reverse the board tuple to match the player's perspective. only reverses the first 24 positions, bar is not reversed."""
    reversed_board = []
    for i in range(24):
        reversed_board.append(board[23 - i])
    # Append the bar positions
    reversed_board.append(board[24])  # Bar for X
    return tuple(reversed_board)


def get_simple_board() -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """
        returns the board as a tuple. first tuple represents current player, second represents other player.
    """
    return gnubg.board()

def get_board() -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """Get the current board state, O is always on 0 and X always on 1."""
    board_tuple = get_simple_board()
    posinfo = gnubg.posinfo()
    turn = posinfo["turn"]
    if turn == 1: # means it's O's turn.
        # O's board on 0 , X's board on 1
        reverse_o = reverse_board(board_tuple[0])
        return reverse_o, board_tuple[1] 
    else: # means it's X's turn
        # X's board on 0, O's board on 1
        reverse_x = reverse_board(board_tuple[0])
        return board_tuple[1], reverse_x

def default_board_representation() -> str:
    """ create a human readable board, that is easy to understand and good for llm"""
    board = get_board()
    board_state = []
    for i in range(0, 24):
        pos = i + 1
        if board[1][i] > 0:
            board_state.append(f"{pos}: X has {board[1][i]}")
        elif board[0][i] > 0:
            board_state.append(f"{pos}: O has {board[0][i]}")
        else:
            board_state.append(f"{pos}: empty")

    bar_X = board[1][24]
    bar_O = board[0][24]

    on_bar = f"Bar: X has {bar_X}, O has {bar_O}"

    return f"Backgammon board state:\t{chr(9).join(board_state)}\t{on_bar}"

def move_piece(curr_player: Agent, move: Optional[str] = None) -> bool:
    """Move a piece according to the move string with retry logic."""
    current_move = move
    
    for attempt in range(MAX_RETRIES):        
        try:
            if is_valid_move(current_move):
                gnubg.command(f"move {current_move}")
                return True
            else:
                logger.warning(f"Invalid move format: '{current_move}' (attempt {attempt + 1})")
                current_move = curr_player.handle_invalid_move(current_move)
        except Exception as e:
            logger.warning(f"Error at move_piece '{current_move}': {e} (attempt {attempt + 1})")
            try:
                current_move = curr_player.handle_invalid_move(current_move)
            except Exception as agent_error:
                logger.error(f"Error in agent's handle_invalid_move: {agent_error}")
                force_move()
                return False

    # after all retries or if handle_invalid_move failed, force gnubg to play
    logger.error(f"Agent {curr_player} failed to provide a valid move after {MAX_RETRIES} attempts.")
    force_move()
    return False


def get_possible_moves() -> List[str]:
    try:
        hints = gnubg.hint()
        hint_moves = hints.get("hint", [])
        if hint_moves:
            moves = [ m["move"] for m in hint_moves]
            # reorder moves to randomize the order
            random.shuffle(moves)
            return moves
        else:
            return []
    except Exception:
        return []
        
def get_hints() -> List[Hint]:
    top_hints = 10
    try:
        hints = gnubg.hint()
        hint_moves = hints.get("hint", [])
        if hint_moves:
            moves = [
                {"move": m["move"], "equity": m.get("equity", 0)} for m in hint_moves
            ]
            return moves[:top_hints]
        else:
            return []
    except Exception:
        return []
    
def get_best_move() -> str:
    try:
        hints = gnubg.hint()
        hint_moves = hints.get("hint", [])
        if hint_moves:
            best_move = max(hint_moves, key=lambda x: x.get("equity", 0))
            move = best_move["move"]            
            return move

    except Exception as e:
        logger.error(f"Error with findbestmove: {e}")
        return None

def random_valid_move():
    """ makes a valid random move"""
    all_moves =  get_possible_moves()
    if not all_moves or len(all_moves) == 0:
        logger.info("No possible moves found")
        return None
    
    return all_moves[0]

def force_move():
    """Force gnubg to play an automatic move. used when all other methods fail"""
    try:
        logger.warning("Force automatic play. This is not supposed to happen.")
        gnubg.command("play")
    except Exception as e:
        logger.error(f"Error forcing gnubg to play: {e}")
        raise RuntimeError(f"Failed to execute move and gnubg auto play also failed. {e}")


def is_cube_decision() -> bool:
    """Check if current position requires a cube decision."""
    dice = get_dice()
    return dice == (0, 0)

def handle_cube_decision() -> bool:
    """Handle cube decisions through agent or automatically."""
    try:
        logger.debug("Not offering double, continuing with normal play")
        gnubg.command("roll")  # Continue to normal dice roll
        return True
            
    except Exception as e:
        logger.error(f"Error handling cube decision: {e}")
        try:
            force_move()
            return True
        except:
            return False

def roll_dice():
    """Roll the dice using gnubg."""
    try:
        gnubg.command("roll")
    except Exception as e:
        logger.error(f"Error rolling dice: {e}")
        return None

def get_pip_count() -> Tuple[int, int]:
    """Get pip count for both players."""
    try:
        # Try to get pip count from gnubg
        pip_info = gnubg.pip()
        if pip_info and len(pip_info) >= 2:
            return pip_info[0], pip_info[1]
    except:
        pass
    
    # Fallback: calculate pip count manually from board
    board = get_simple_board()
    pip1 = calculate_pip_count_from_board(board[0])
    pip2 = calculate_pip_count_from_board(board[1])
    return pip1, pip2

def calculate_pip_count_from_board(player_board: Tuple[int, ...]) -> int:
    """Calculate pip count from a player's board position."""
    pip_count = 0
    # Points 1-24
    for i in range(24):
        checkers = player_board[i]
        distance = 24 - i  # Distance to bear off
        pip_count += checkers * distance
    
    # Add checkers on bar (distance 25)
    if len(player_board) > 24:
        pip_count += player_board[24] * 25
        
    return pip_count

def get_checkers_count() -> Tuple[int, int]:
    """Get total checkers remaining for both players."""
    board = get_simple_board()
    player1_checkers = sum(board[0])
    player2_checkers = sum(board[1])
    return player1_checkers, player2_checkers

def get_checkers_on_bar() -> Tuple[int, int]:
    """Get checkers on bar for both players."""
    board = get_simple_board()
    player1_bar = board[0][24] if len(board[0]) > 24 else 0
    player2_bar = board[1][24] if len(board[1]) > 24 else 0
    return player1_bar, player2_bar

def determine_game_type(winner_checkers: int, loser_checkers: int, loser_in_home: bool = False) -> str:
    """Determine if the game was normal, gammon, or backgammon."""
    if loser_checkers == 15:  # Loser hasn't borne off any checkers
        if not loser_in_home:  # Loser has checkers in winner's home board or on bar
            return "backgammon"
        else:
            return "gammon"
    else:
        return "normal"

def create_player_statistics(agent_name: str) -> PlayerStatistics:
    """Create initial player statistics."""
    return PlayerStatistics(
        name=agent_name,
        invalid_moves=0,
        total_moves=0,
        checkers_remaining=0,
        checkers_on_bar=0,
        pip_count=0,
        cube_decisions=0,
        cube_accepts=0,
        cube_rejects=0
    )

