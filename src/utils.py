import gnubg
import os
from typing import List, Optional, Tuple
import re
import random

import requests
import dotenv

from .interfaces import Hint
from .logger import logger
dotenv.load_dotenv()

# LLM API configuration
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

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
        logger.error(f"Error getting game context: {e}")
        return {}

def get_player_name() -> str:
    """Get the name of the current player."""
    posinfo = gnubg.posinfo()
    turn = posinfo["turn"]
    return "X" if turn == 1 else "O"

def get_dice() -> Tuple[int, int]:
    """Get the current dice rolled."""
    posinfo = gnubg.posinfo()
    dice = posinfo["dice"]
    if dice is None or len(dice) < 2:
        logger.warning("No dice rolled yet.")
        return None

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

    return f"Backgammon board state:\t{' ;'.join(board_state)}\t{on_bar}"


def default_board_representation() -> str:
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

    return f"Backgammon board state:\t{'\t'.join(board_state)}\t{on_bar}"

def is_valid_move(move: str) -> bool:
    """Check if a move is valid."""
    if not move or not isinstance(move, str):
        logger.warning("Invalid move format. Move must be a non-empty string.")
        return False
    # check if move is in the correct format: examples: 13/6**, 13/11 8/3, 24/22 8/3, 13/7*/5
    valid_move_pattern = r"^\d{1,2}/\d{1,2}(\s\d{1,2}/\d{1,2})*(\s\*\*)?$"
    if not re.match(valid_move_pattern, move):
        logger.warning(f"Invalid move format: {move}")
        return False
    
def move_piece(move: str):
    """Move a piece according to the move string."""
    if not move:
        gnubg.command("play")
        return False
    # TODO: fix is valid move and then uncomment this
    # if not is_valid_move(move):
    #     logger.warning("Invalid move format. Move must be a non-empty string.")
    #     return False
    try:
        gnubg.command(f"move {move}")
    except Exception as e:
        logger.error(f"Error moving piece, forcing gnubg to play: {e}")
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
        logger.error(f"Error with findbestmove: {e}")
        return None

def random_move():
    """ makes a valid random move"""
    all_moves =  get_possible_moves()
    if not all_moves or len(all_moves) == 0:
        logger.info("No possible moves found")
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
        logger.error(f"Error getting game context: {e}")
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
    # TODO: make sure extract move from llm transform the reposnse to a move that gnubg can understand.
    # if not pass it to openai api again, with instructions to return a move that gnubg can understand.

    try:
        if not response or "choices" not in response:
            return None

        content = response["choices"][0]["message"]["content"]
        logger.debug(f"LLM response: {content}")

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
                    logger.debug(f"Extracted move: '{recommendation}'")

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
                logger.debug(f"Found move match in content: {move['move']}")
                return move

        # No clear recommendation found
        logger.warning("No clear move recommendation found in response")
        return None
    except Exception as e:
        logger.error(f"Error extracting move from response: {e}")
        return None

def consult_llm(board_repr:str, prompt: str =None, system_prompt: str =None,
                possible_moves: Optional[List[str]] = None, hints: Optional[List[Hint]] = None,
                best_move: Optional[str] = None, **prompt_params):
    """Send game state to LLM and get move recommendation
        **prompt_params: Additional parameters to inject into the prompt
    """
    try:
        if not prompt:
            prompt = default_prompt(board_repr)

        prompt_params = {
            "board_repr": board_repr,
            "possible_moves": possible_moves if possible_moves else [],
            "hints": hints if hints else [],
            "best_move": best_move if best_move else None,
            **prompt_params
        }
        
        prompt = prompt.format(**prompt_params)
        
        llm_response = call_openai_api(prompt, system_prompt=system_prompt)

        # TODO: validate the response using schema

        move_choice = extract_move_from_llm_response(llm_response, possible_moves)

        if move_choice:
            logger.debug(f"LLM recommended move: {move_choice['move']}")
            return move_choice

        return random_move()
    except Exception as e:
        logger.error(f"Error consulting LLM: {e}")
        import traceback

        logger.error(traceback.format_exc())

        return random_move()


def call_openai_api(prompt, system_prompt=None):
    """Call the OpenAI API"""
    if not system_prompt:
        system_prompt = "You are an expert backgammon assistant."
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
                    "content": system_prompt,
                },
                {"role": "user", "content": prompt},
            ],
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
        logger.error(f"Error calling API: {e}")
        return None

def roll_dice():
    """Roll the dice using gnubg."""
    try:
        gnubg.command("roll")
    except Exception as e:
        logger.error(f"Error rolling dice: {e}")
        return None
