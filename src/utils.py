import gnubg
import time
import os
from typing import List, Tuple
import re
import random

import requests
import dotenv

from .interfaces import Hint

dotenv.load_dotenv()

# LLM API configuration
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")


output_dir = "/app/output" if os.path.exists("/app/output") else os.getcwd()
log_file_name = f"game_log_{time.strftime('%Y%m%d_%H%M%S')}.txt"
LOG_FILE = os.path.join(output_dir, log_file_name)


def log_message(message):
    """Write a message to the log file"""
    with open(LOG_FILE, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
    print(message)


def get_game_context():
    """Get the current game context including position evaluation"""
    context = {}

    try:
        # Get current dice
        match_info = gnubg.match()
        games = match_info.get("games", [])
        if games and len(games) > 0:
            latest_game = games[-1]
            game_actions = latest_game.get("game", [])
            if game_actions and len(game_actions) > 0:
                latest_action = game_actions[-1]
                context["dice"] = latest_action.get("dice", None)
                context["player"] = latest_action.get("player", None)

        # Get position evaluation if available
        try:
            evaluation = gnubg.evaluate()
            context["evaluation"] = evaluation
        except:
            pass

        # Get pip count (distance to finish)
        try:
            pip_count = gnubg.pip()
            context["pip_count"] = pip_count
        except:
            pass

        # Get position ID for reference
        try:
            context["position_id"] = gnubg.positionid()
        except:
            pass

        return context
    except Exception as e:
        log_message(f"Error getting game context: {e}")
        return {}

def get_player_name() -> str:
    """Get the name of the current player."""
    posinfo = gnubg.posinfo()
    turn = posinfo["turn"]
    return "X" if turn == 1 else "O"

def get_dice() -> tuple:
    """Get the current dice rolled."""
    posinfo = gnubg.posinfo()
    dice = posinfo["dice"]
    if dice is None or len(dice) < 2:
        log_message("No dice rolled yet.")
        return None

def reverse_board(board: tuple) -> tuple:
    """Reverse the board tuple to match the player's perspective. only reverses the first 24 positions, bar is not reversed."""
    reversed_board = []
    for i in range(24):
        reversed_board.append(board[23 - i])
    # Append the bar positions
    reversed_board.append(board[24])  # Bar for X
    return tuple(reversed_board)

def get_simple_board() -> tuple:
    return gnubg.board()

def get_board() -> tuple:
    """Get the current board state, O is always on 0 and X always on 1."""
    board_tuple = get_simple_board()
    posinfo = gnubg.posinfo()
    turn = posinfo["turn"]
    if turn == 1:
        # O's board on 0 , x's board on 1
        reverse_o = reverse_board(board_tuple[0])
        return reverse_o, board_tuple[1] 
    else:
        # X's board on 0, O's board on 1
        reverse_x = reverse_board(board_tuple[0])
        return board_tuple[1], reverse_x

def new_default_board_representation() -> str:
    """ use get_board to create a new default board representation."""
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

    return f"""Backgammon board state:
            {chr(10).join(board_state)}
            {on_bar}"""


def default_board_representation(board: Tuple[int, int] = None) -> str:
    board_tuple = get_simple_board()
    posinfo = gnubg.posinfo()
    turn = posinfo["turn"]
    board_state = []

    o = board_tuple[0 if turn == 1 else 1]
    x = board_tuple[1 if turn == 1 else 0]
    for i in range(0, 24):
        x_pos = i if turn == 1 else 23 - i
        o_pos = 23 - i if turn == 1 else i

        pos = i + 1
        if x[x_pos] > 0:
            board_state.append(f"{pos}: X has {x[x_pos]}")
        elif o[o_pos] > 0:
            board_state.append(f"{pos}: O has {o[o_pos]}")
        else:
            board_state.append(f"{pos}: empty")

    bar_X = x[24]
    bar_O = o[24]

    on_bar = f"Bar: X has {bar_X}, O has {bar_O}"

    return f"""Backgammon board state:
            {chr(10).join(board_state)}
            {on_bar}"""

def is_valid_move(move: str) -> bool:
    """Check if a move is valid."""
    if not move or not isinstance(move, str):
        log_message("Invalid move format. Move must be a non-empty string.")
        return False
    # check if move is in the correct format: examples: 13/6**, 13/11 8/3, 24/22 8/3, 13/7*/5
    valid_move_pattern = r"^\d{1,2}/\d{1,2}(\s\d{1,2}/\d{1,2})*(\s\*\*)?$"
    if not re.match(valid_move_pattern, move):
        log_message(f"Invalid move format: {move}")
        return False
    
def move_piece(move: str):
    """Move a piece according to the move string."""
    if not move:
        gnubg.command("play")
        return False
    # TODO: fix is valid move and then uncomment this
    # if not is_valid_move(move):
    #     log_message("Invalid move format. Move must be a non-empty string.")
    #     return False
    try:
        gnubg.command(f"move {move}")
    except Exception as e:
        log_message(f"Error moving piece, forcing gnubg to play: {e}")
        gnubg.command("play")
        return False
    return True
   

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
    try:
        hints = gnubg.hint()
        hint_moves = hints.get("hint", [])
        if hint_moves:
            moves = [
                {"move": m["move"], "equity": m.get("equity", 0)} for m in hint_moves
            ]
            return moves
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
        log_message(f"Error with findbestmove pattern 1: {e}")
        return None

def default_move():
    """ makes gnubg play the best move according to him."""
    all_moves =  get_possible_moves()
    # take random move
    if not all_moves or len(all_moves) == 0:
        log_message("No possible moves found")
        return None
    
    return all_moves[0]

def get_game_context():
    """Get the current game context including position evaluation"""
    context = {}

    try:
        # Get current dice
        match_info = gnubg.match()
        games = match_info.get("games", [])
        if games and len(games) > 0:
            latest_game = games[-1]
            game_actions = latest_game.get("game", [])
            if game_actions and len(game_actions) > 0:
                latest_action = game_actions[-1]
                context["dice"] = latest_action.get("dice", None)
                context["player"] = latest_action.get("player", None)

        # Get position evaluation if available
        try:
            evaluation = gnubg.evaluate()
            context["evaluation"] = evaluation
        except:
            pass

        # Get pip count (distance to finish)
        try:
            pip_count = gnubg.pip()
            context["pip_count"] = pip_count
        except:
            pass

        # Get position ID for reference
        try:
            context["position_id"] = gnubg.positionid()
        except:
            pass

        return context
    except Exception as e:
        log_message(f"Error getting game context: {e}")
        return {}


def default_prompt(board_repr=None):
    # Extract the list of moves from the hint data
    if not board_repr:
        board_repr = default_board_representation()
    hint_data = gnubg.hint()
    moves = hint_data["hint"]

    formatted_moves = []
    for move_info in moves:
        move_desc = f"Move {move_info['movenum']}: {move_info['move']}"

        probs = move_info["details"]["probs"]
        win_prob = probs[0] * 100
        gammon_win = probs[1] * 100

        eval_desc = (
            f"Win: {win_prob:.1f}%, Gammon win: {gammon_win:.1f}%, "
        )

        formatted_moves.append(f"{move_desc}\n{eval_desc}")

    moves_text = "\n\n".join(formatted_moves)

    prompt = f"""
    You are an expert backgammon player choosing the best move in this position.
    You have never lost against gnubg because of your superior strategy.
    
    # Current Board Position
    {board_repr}
    
    # Possible Moves (with gnubg evaluations)
    {moves_text}
    
    # Instructions
    Choose the best move for this position, drawing on both:
    1. Your knowledge of backgammon strategy and tactical patterns
    2. The statistical evaluations from gnubg (shown above)
    
    Consider these factors that might not be fully captured in gnubg's evaluation:
    - Position type (racing, priming, back game, holding game)
    - Tactical patterns (slots, hits, anchors, builders)
    - Checker distribution and flexibility
    - Safety vs. aggression balance
    - Future roll equity
    
    Your analysis should:
    1. Discuss the best move according to your superior knowledge of backgammon.
    2. Identify any strategic patterns or special features of this position
    3. Explain whether you agree or disagree with gnubg's evaluation and why
    
    Remember that negative equity values mean the position is disadvantageous for the player.
    Lower (more negative) values indicate worse moves in this context.
    
    Begin with a brief assessment of the position and what key objectives you see.
    
    Conclude with your recommended move in this exact format:
    RECOMMENDED MOVE: [move notation as shown in the options]
    """

    return prompt


def extract_move_from_llm_response(response, possible_moves):
    """Extract the recommended move from the LLM response"""
    try:
        if not response or "choices" not in response:
            return None

        content = response["choices"][0]["message"]["content"]
        log_message(f"LLM response: {content}")

        # Look for a section that might contain the recommended move
        # This is a simple extraction approach - can be refined based on actual responses

        # Look for specific markers
        markers = [
            "RECOMMENDED MOVE:",
            "RECOMMENDED_MOVE:",
            "I recommend:",
            "Best move:",
            "Optimal move:",
            "My recommendation:",
        ]

        for marker in markers:
            if marker in content:
                # Split by the marker and take the text immediately after
                parts = content.split(marker)
                if len(parts) > 1:
                    # Take the first line after the marker
                    recommendation = parts[1].strip().split("\n")[0].strip()

                    # Clean up the recommendation (remove punctuation, etc.)
                    for char in [".", ",", ":", ";", '"', "'"]:
                        recommendation = recommendation.replace(char, "")

                    recommendation = recommendation.strip()
                    log_message(f"Extracted move: '{recommendation}'")

                    # Try to match with available moves
                    for move in possible_moves:
                        if move["move"] == recommendation:
                            return move

                    # Try partial matching
                    for move in possible_moves:
                        if (
                            recommendation in move["move"]
                            or move["move"] in recommendation
                        ):
                            return move

        # If we couldn't find a clear recommendation, try to find any move notation in the text
        for move in possible_moves:
            if move["move"] in content:
                log_message(f"Found move match in content: {move['move']}")
                return move

        # No clear recommendation found
        log_message("No clear move recommendation found in response")
        return None
    except Exception as e:
        log_message(f"Error extracting move from response: {e}")
        return None

def consult_llm(board_repr, possible_moves, prompt=None):
    """Send game state to LLM and get move recommendation"""
    try:
        if not prompt:
            prompt = default_prompt(board_repr)

        llm_response = call_openai_api(prompt)

        move_choice = extract_move_from_llm_response(llm_response, possible_moves)

        if move_choice:
            log_message(f"LLM recommended move: {move_choice['move']}")
            return move_choice

        return default_move()
    except Exception as e:
        log_message(f"Error consulting LLM: {e}")
        import traceback

        log_message(traceback.format_exc())
        
        return default_move()


def call_openai_api(prompt):
    """Call the OpenAI API"""
    try:
        base_url = os.getenv("LLM_API_URL")
        deployment = "gpt-4o"
        api_key = os.getenv("LLM_API_KEY")
        url = f"{base_url}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        data = {
            "model": deployment,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert backgammon assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 8000,
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            return None

    except Exception as e:
        log_message(f"Error calling API: {e}")
        return None

def roll_dice():
    """Roll the dice using gnubg."""
    try:
        gnubg.command("roll")
    except Exception as e:
        return None
