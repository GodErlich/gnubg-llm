import gnubg
import time
import os
import requests
import json
import dotenv

dotenv.load_dotenv()

# Set up logging
LOG_FILE = os.path.join(os.getcwd(), "llm_log.log")

# LLM API configuration
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")


def log_message(message):
    """Write a message to the log file"""
    with open(LOG_FILE, "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
    print(message)  # Also print to stdout/stderr


def get_board_representation():
    """Get a human-readable representation of the board"""
    try:
        board = gnubg.board()
        # Format board for better LLM understanding
        board_repr = {"player": [], "opponent": []}

        # Process board data
        # gnubg board format is typically:
        # board[0] = player checkers (positive values on points 0-23, negative for checkers on bar)
        # board[1] = opponent checkers

        for i in range(24):
            if board[0][i] > 0:
                board_repr["player"].append({"point": i + 1, "checkers": board[0][i]})
            if board[1][i] > 0:
                board_repr["opponent"].append(
                    {"point": 24 - i, "checkers": board[1][i]}
                )

        # Add bar checkers if any
        if board[0][24] > 0:
            board_repr["player"].append({"point": "bar", "checkers": board[0][24]})
        if board[1][24] > 0:
            board_repr["opponent"].append({"point": "bar", "checkers": board[1][24]})

        return board_repr
    except Exception as e:
        log_message(f"Error getting board representation: {e}")
        return None


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


def call_openai_api(prompt):
    """Call the OpenAI API"""
    try:
        base_url = os.getenv("LLM_API_URL")
        deployment = "gpt-4o"
        api_version = "2024-02-15-preview"

        url = f"{base_url}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

        headers = {
            "Content-Type": "application/json",
            "api-key": os.getenv("LLM_API_KEY"),
        }

        data = {
            "model": "gpt-4o",
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


def format_board_for_llm(board_tuple, dice, turn):
    board_state = []
    o = board_tuple[0]
    x = board_tuple[1]
    for i in range(0, 24):
        pos = i + 1
        if x[i] > 0:
            board_state.append(f"{pos}: X has {x[i]}")
        elif o[23 - i] > 0:
            board_state.append(f"{pos}: O has {o[23-i]}")
        else:
            board_state.append(f"{pos}: empty")

    # bar are in pos 24(i think)

    bar_X = x[24]
    bar_O = o[24]

    on_bar = f"Bar: X has {bar_X}, O has {bar_O}"
    dice_str = f"Dice rolled: {dice[0]} and {dice[1]}"
    player = "X" if turn == 1 else "O"

    return f"""Backgammon board state:
            {chr(10).join(board_state)}
            {on_bar}
            {dice_str}
            It's {player}'s turn."""


def consult_llm(board_repr, game_context, possible_moves):
    """Send game state to LLM and get move recommendation"""
    try:
        # Format dice for better readability
        dice_str = "Unknown"
        if game_context.get("dice"):
            dice = game_context.get("dice")
            if isinstance(dice, list) and len(dice) == 2:
                dice_str = f"{dice[0]},{dice[1]}"

        # Prepare a structured prompt
        prompt = f"""
            You are an expert backgammon AI assistant. Analyze the current board position and recommend the best move.

            CURRENT BOARD:
            {board_repr.get('visual', 'No visual representation')}

            GAME CONTEXT:
            - Dice: {dice_str}
            - Current player: {game_context.get('player', 'Unknown')}
            - Pip count: {json.dumps(game_context.get('pip_count', 'Unknown'))}
            - Position evaluation: {json.dumps(game_context.get('evaluation', 'Unknown'))}

            AVAILABLE MOVES:
            """

        # Add move options with clear numbering
        for i, move in enumerate(possible_moves):
            prompt += f"{i+1}. Move: {move['move']}\n"

        prompt += """
            Based on this position, analyze the strategic implications of each move, considering:
            1. Checker safety
            2. Board development
            3. Blocking strategy
            4. Race considerations
            5. Hit opportunities
            6. Long-term position strength

            Then recommend the BEST move using this exact format:
            RECOMMENDED MOVE: [write the exact move notation]

            Provide your reasoning after the recommendation.
        """
        log_message(f"Prompt: {prompt}")
        # Call the LLM API
        llm_response = call_openai_api(prompt)

        # Extract the recommended move
        move_choice = extract_move_from_llm_response(llm_response, possible_moves)

        if move_choice:
            log_message(f"LLM recommended move: {move_choice['move']}")
            return move_choice

        # If no move was recommended, return the highest equity move
        log_message("Falling back to highest equity move")
        if possible_moves:
            return max(possible_moves, key=lambda x: x.get("equity", -999))
        return None

    except Exception as e:
        log_message(f"Error consulting LLM: {e}")
        import traceback

        log_message(traceback.format_exc())

        # Fallback to highest equity move
        if possible_moves:
            return max(possible_moves, key=lambda x: x.get("equity", -999))
        return None


def play_llm_move():
    """Play a move suggested by the LLM"""
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

        # Get the board representation and game context
        board_repr = get_board_representation()
        game_context = get_game_context()

        # Consult the LLM for a move recommendation
        chosen_move_data = consult_llm(board_repr, game_context, all_moves)

        if chosen_move_data:
            chosen_move = chosen_move_data["move"]
            log_message(f"Playing LLM-recommended move: {chosen_move}")
        elif len(all_moves) > 0:
            # Fallback to best move if LLM didn't recommend one
            chosen_move = max(all_moves, key=lambda x: x.get("equity", -999))["move"]
            log_message(f"Falling back to best move: {chosen_move}")
        else:
            log_message("No moves available")
            # Make sure we don't get stuck in an infinite loop
            gnubg.command("play")
            return False

        # Play the move
        log_message(f"Executing move: {chosen_move}")
        gnubg.command(f"move {chosen_move}")
        return True

    except Exception as e:
        log_message(f"Error in play_llm_move: {e}")
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
    """Play a full game with our LLM-enhanced logic"""
    # Clear or create log file
    try:

        log_message("Starting a new game")

        # Start a new game
        gnubg.command("new game")

        # Set up player 0 as human and player 1 as human (computer vs computer)
        gnubg.command("set player 0 human")
        gnubg.command("set player 1 human")
        log_message("Set up player 0 and player 1 as human (LLM vs human)")

        # Main game loop - limited to 200 turns to prevent infinite loops
        max_turns = 200
        turn_count = 0

        while turn_count < max_turns and not is_game_over():
            turn_count += 1
            log_message(f"\n--- Turn {turn_count} ---")

            log_message("Rolling dice")
            gnubg.command("roll")

            log_message("Using LLM-enhanced move selection")
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

                # Play our LLM-recommended move
                play_llm_move()
            except Exception as e:
                log_message(f"Error during LLM-enhanced turn: {e}")
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
    except Exception as e:
        log_message(f"Error in play_full_game: {e}")
        import traceback

        log_message(traceback.format_exc())


# Start the game
try:
    play_full_game()
except Exception as e:
    log_message(f"Error in main: {e}")
    import traceback

    log_message(traceback.format_exc())
