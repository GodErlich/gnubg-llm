import gnubg
from typing import List, Optional, Tuple
import random


from .game_utils import is_valid_move
from ..interfaces import Hint
from ..logger import logger

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



"""
    returns the board as a tuple. first tuple represents current player, second represents other player.
"""
def get_simple_board() -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
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

def move_piece(curr_player, move: Optional[str] = None) -> bool:
    """Move a piece according to the move string."""
    if not move:
        logger.warning(f"Agent {curr_player} did not choose a valid move. an automatic move will be played.")
        move = random_valid_move()
        if not move:
            logger.warning("No valid move found, forcing gnubg to play.")
            gnubg.command("play")
            return False
    # Validate move format before attempting to execute
    if not is_valid_move(move):
        logger.warning(f"Invalid move format: '{move}', forcing gnubg to play.")
        gnubg.command(f"move {move}")
        return False
    try:
        gnubg.command(f"move {move}")
        return True
    except Exception as e:
        logger.error(f"Error moving piece, forcing gnubg to play: {e}")
        gnubg.command("play")
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
        # Fallback - let gnubg decide
        try:
            gnubg.command("play")
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

