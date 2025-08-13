import gnubg
import os
from typing import List, Optional, Tuple
import re
import random

import requests
from dotenv import load_dotenv

from .interfaces import Hint
from .logger import logger
load_dotenv()

# LLM API configuration
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

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


def is_valid_move(move: str) -> bool:
    """Check if a move is valid according to gnubg move format."""
    if not move or not isinstance(move, str):
        logger.warning("Invalid move format. Move must be a non-empty string.")
        return False
    
    # Strip whitespace
    move = move.strip()
    if not move:
        return False
    
    # Split move into individual moves (space-separated)
    individual_moves = move.split()
    
    for single_move in individual_moves:
        # More comprehensive pattern to handle complex moves:
        # Examples: "24/18*/17*", "bar/20*/19*", "10/4(2)", "8/2*(2)"
        
        # Break down the move into segments separated by '/'
        if not _validate_complex_move(single_move):
            logger.warning(f"Invalid move format: '{single_move}' in move '{move}'")
            return False
    
    return True

def _validate_complex_move(move: str) -> bool:
    """Validate a single complex move that may have multiple segments."""
    # Split by '/' to get all segments
    segments = move.split('/')
    
    if len(segments) < 2:
        return False
    
    # First segment: starting position (bar or number)
    start_pos = segments[0].lower()
    if start_pos != 'bar':
        try:
            start_num = int(start_pos)
            if start_num < 1 or start_num > 24:
                return False
        except ValueError:
            return False
    
    # Process remaining segments (destinations)
    for i, segment in enumerate(segments[1:], 1):
        if not _validate_move_segment(segment, is_last=(i == len(segments) - 1)):
            return False
    
    return True

def _validate_move_segment(segment: str, is_last: bool = True) -> bool:
    """Validate a single move segment (destination)."""
    # Segment can be:
    # - "22" (simple move)
    # - "22*" (hit)
    # - "22*(2)" (hit with parenthetical)
    # - "4(2)" (multiple checkers)
    # - "2*(2)" (hit multiple checkers)
    # - "off" (bear off)
    # - "off(2)" (bear off multiple)
    
    # Pattern for a destination segment:
    # - destination: number(1-24) or "off"
    # - optional asterisk for hit
    # - optional parenthetical for multiple checkers
    pattern = r'^(\d{1,2}|off)(\*)?(\(\d+\))?$'
    
    match = re.match(pattern, segment, re.IGNORECASE)
    if not match:
        return False
    
    destination, hit, count = match.groups()
    
    # Validate destination
    if destination.lower() != 'off':
        try:
            dest_num = int(destination)
            if dest_num < 1 or dest_num > 24:
                return False
        except ValueError:
            return False
    
    # Validate parenthetical count if present
    if count:
        try:
            num_checkers = int(count[1:-1])  # Remove parentheses
            if num_checkers < 1 or num_checkers > 15:
                return False
        except ValueError:
            return False
    
    return True

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

def consult_llm(board_repr:str, prompt: str, system_prompt: str =None,
                possible_moves: List[str] = [], hints: List[Hint] = [],
                best_move: str = '', **prompt_params):
    """Send game state to LLM and get move recommendation
        **prompt_params: Additional parameters to inject into the prompt
    """
    try:
        if not prompt:
            logger.error("Prompt is required for LLM consultation.")
            return None

        prompt_params = {
            "board_repr": board_repr,
            "possible_moves": possible_moves,
            "hints": hints,
            "best_move": best_move,
            **prompt_params
        }
        
        prompt = prompt.format(**prompt_params)
        
        llm_response = call_openai_api(prompt, system_prompt=system_prompt)

        # TODO: validate the response using schema

        move_choice = extract_move_from_llm_response(llm_response, possible_moves)

        if move_choice:
            logger.debug(f"LLM recommended move: {move_choice['move']}")
            return move_choice

        logger.warning("LLM did not recommend a valid move.")
        return None
    except Exception as e:
        logger.error(f"Error consulting LLM: {e}")
        import traceback

        logger.error(traceback.format_exc())
        logger.warning("LLM did not recommend a valid move.")
        return None


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

def map_winner(game_result):
    """Map the game result to a winner.
        0 is always associated with X which is agent1
        1 is always associated with O which is agent2
    """
    if game_result == 'X':
        logger.debug(f"Game ended with agent1 winning.")
        return 0
    elif game_result == 'O':
        logger.debug(f"Game ended with agent2 winning.")
        return 1
    else:
        logger.warning(f"Unknown game result: {game_result}")
        return "Unknown"