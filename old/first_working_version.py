import gnubg
import time
import sys
import os

# Set up logging
LOG_FILE = os.path.join(os.getcwd(), "gnubg_game.log")


def log_message(message):
    """Write a message to the log file"""
    with open(LOG_FILE, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
    print(message)  # Also print to stdout/stderr


def get_moves_with_fallbacks():
    """Try multiple methods to get possible moves"""
    moves = []

    # Method 1: Try using hint()
    try:
        log_message("Trying to get moves using hint()")
        hints = gnubg.hint()
        hint_moves = hints.get("hint", [])
        if hint_moves:
            # Format: [{'movenum': 1, 'move': '24/20 21/20', 'equity': -0.07...}, ...]
            moves = [
                {"move": m["move"], "equity": m.get("equity", 0)} for m in hint_moves
            ]
            log_message(f"Got {len(moves)} moves from hint()")
            return moves
    except Exception as e:
        log_message(f"Error getting hints: {e}")

    # Method 2: Try using current match/game info
    try:
        log_message("Trying to get moves from match info")
        match_info = gnubg.match()
        games = match_info.get("games", [])
        if games and len(games) > 0:
            latest_game = games[-1]
            game_actions = latest_game.get("game", [])
            if game_actions and len(game_actions) > 0:
                latest_action = game_actions[-1]
                if "analysis" in latest_action and "moves" in latest_action["analysis"]:
                    move_analysis = latest_action["analysis"]["moves"]
                    moves = [
                        {"move": str(m.get("move")), "equity": m.get("score", 0)}
                        for m in move_analysis
                        if "move" in m
                    ]
                    log_message(f"Got {len(moves)} moves from match analysis")
                    return moves
    except Exception as e:
        log_message(f"Error getting moves from match: {e}")

    # Method 3: Try using findbestmove
    try:
        log_message("Trying to get moves with findbestmove()")
        # Get current dice
        dice = None
        try:
            match_info = gnubg.match()
            games = match_info.get("games", [])
            if games and len(games) > 0:
                latest_game = games[-1]
                game_actions = latest_game.get("game", [])
                if game_actions and len(game_actions) > 0:
                    latest_action = game_actions[-1]
                    dice = latest_action.get("dice", None)
                    log_message(f"Found dice: {dice}")
        except Exception as e:
            log_message(f"Error getting dice: {e}")

        if dice:
            # Get current board
            board = gnubg.board()

            # Try findbestmove with different parameter patterns
            try:
                # Try pattern 1: findbestmove(dice, board)
                best_move = gnubg.findbestmove(dice, board)
                if best_move:
                    log_message(f"Found move with findbestmove: {best_move}")
                    # Convert to our standard format
                    move_str = gnubg.movetupletostring(best_move)
                    moves = [{"move": move_str, "equity": 0}]
                    return moves
            except Exception as e:
                log_message(f"Error with findbestmove pattern 1: {e}")

                # Try pattern 2: other variations of parameters
                try:
                    # This is a guess - try without parameters
                    best_move = gnubg.findbestmove()
                    if best_move:
                        log_message(
                            f"Found move with findbestmove (no params): {best_move}"
                        )
                        move_str = gnubg.movetupletostring(best_move)
                        moves = [{"move": move_str, "equity": 0}]
                        return moves
                except Exception as e:
                    log_message(f"Error with findbestmove pattern 2: {e}")
    except Exception as e:
        log_message(f"Error with findbestmove approach: {e}")

    # Return whatever we have (might be empty)
    return moves


def is_computer_turn():
    """Check if it's the computer's turn to play"""
    try:
        match_info = gnubg.match()
        if "games" in match_info and match_info["games"]:
            latest_game = match_info["games"][-1]
            if "game" in latest_game and latest_game["game"]:
                latest_action = latest_game["game"][-1]
                current_player = latest_action.get("player", None)
                log_message(f"Current player: {current_player}")
                # Player 'X' is the computer (gnubg)
                return current_player == "X"
    except Exception as e:
        log_message(f"Error checking whose turn: {e}")
    return False


def play_modified_move():
    """Play a modified move using the most reliable method available"""
    try:

        # Get current position information
        position_id = gnubg.positionid()
        log_message(f"Current position: {position_id}")

        # Check if we need to roll dice
        try:
            posinfo = gnubg.posinfo()
            if not posinfo or "dice" not in posinfo or not posinfo["dice"]:
                log_message("Rolling dice")
                gnubg.command("roll")
                # Give a small delay for the roll to complete
                time.sleep(0.5)
        except Exception as e:
            log_message(f"Error checking/rolling dice: {e}")
            return False

        # Get all possible moves with fallbacks
        all_moves = get_moves_with_fallbacks()

        if not all_moves:
            log_message("No moves could be found with any method")
            # Let GnuBG play normally
            gnubg.command("play")
            return True

        # Display the available moves
        for i, move_data in enumerate(all_moves[:5]):  # Show top 5 moves
            move_str = move_data.get("move", "Unknown")
            equity = move_data.get("equity", 0)
            log_message(f"Move {i+1}: {move_str} (Equity: {equity})")

        # Choose the second-best move if available
        if len(all_moves) > 1:
            chosen_move = all_moves[0]["move"]
            log_message(f"Playing worst move: {chosen_move}")
        elif len(all_moves) == 1:
            chosen_move = all_moves[0]["move"]
            log_message(f"Only one move available: {chosen_move}")
        else:
            log_message("No moves available")
            # make sure we don't get stuck in an infinite loop.
            gnubg.command("play")
            return False

        # Play the move
        log_message(f"Executing move: {chosen_move}")
        gnubg.command(f"move {chosen_move}")
        return True

    except Exception as e:
        log_message(f"Error in play_modified_move: {e}")
        import traceback

        log_message(traceback.format_exc())
        return False


def is_game_over():
    """Check if the current game is over"""
    try:
        # Try to detect game end
        board = gnubg.board()
        player1_checkers = sum(board[0])
        player2_checkers = sum(board[1])

        if player1_checkers == 0 or player2_checkers == 0:
            log_message(
                f"Game over detected: Player 1 has {player1_checkers} checkers, Player 2 has {player2_checkers} checkers"
            )
            return True

        # Also check match info
        match_info = gnubg.match()
        if "games" in match_info and match_info["games"]:
            latest_game = match_info["games"][-1]
            if "info" in latest_game and "winner" in latest_game["info"]:
                if latest_game["info"]["winner"] is not None:
                    log_message(
                        f"Game over detected: Winner is {latest_game['info']['winner']}"
                    )
                    return True

        return False

    except Exception as e:
        log_message(f"Error checking if game is over: {e}")
        return False


def play_full_game():
    """Play a full game with our modified logic"""
    # Clear or create log file
    with open(LOG_FILE, "w") as f:
        f.write("Starting GnuBG Modified Game\n")
        f.write("---------------------------\n")

    log_message("Starting a new game")

    # Start a new game
    gnubg.command("new game")

    # Set up player 0 as gnubg and player 1 as human (computer vs computer)
    gnubg.command("set player 0 human")
    gnubg.command("set player 1 human")
    log_message("Set up player 0 and player 1 as gnubg (computer vs human)")

    # Main game loop - limited to 200 turns to prevent infinite loops
    max_turns = 200
    turn_count = 0

    while turn_count < max_turns and not is_game_over():
        turn_count += 1
        log_message(f"\n--- Turn {turn_count} ---")
        # Start the game
        log_message("Rolling dice")
        gnubg.command("roll")

        log_message("Using modified move selection")
        # Try to roll if needed
        try:
            # Check if we need to roll dice
            posinfo = None
            try:
                posinfo = gnubg.posinfo()
            except:
                log_message("Could not get posinfo, might need to roll")

            # If we couldn't get posinfo or if there are no dice, roll
            if not posinfo or "dice" not in posinfo or not posinfo["dice"]:
                log_message("Rolling dice")
                try:
                    gnubg.command("roll")
                except:
                    log_message("Error rolling dice")

            # Play our modified move
            play_modified_move()
        except Exception as e:
            log_message(f"Error during modified turn: {e}")
            # Fallback to regular play
            try:
                gnubg.command("play")
            except:
                log_message("Error with fallback play command")

        # Short pause between turns for stability
        time.sleep(0.8)

    if turn_count >= max_turns:
        log_message("Maximum turn count reached, ending game")

    # Get final game information
    try:
        match_info = gnubg.match()
        if "games" in match_info and match_info["games"]:
            latest_game = match_info["games"][-1]
            log_message(f"Final game info: {latest_game.get('info', {})}")
    except Exception as e:
        log_message(f"Error getting final match info: {e}")

    log_message("Game completed")


# Start the game
play_full_game()
