import re

from ..logger import logger


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