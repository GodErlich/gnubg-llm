import gnubg
import time
from typing import Callable

from .agents import Agent
from .utils import default_board_representation, get_dice, get_simple_board, get_possible_moves, move_piece, roll_dice, get_hints, get_best_move, map_winner, is_cube_decision, handle_cube_decision
from .logger import logger

class Game:
    """Manages a backgammon game between two agents."""
    def __init__(self, agent1: Agent, agent2: Agent, max_turns: int = 200, board_representation: Callable[[], str] = None):
        self.agent1 = agent1
        self.agent2 = agent2
        self.max_turns = max_turns
        self.turn_count = 0
        if board_representation is None:
            self.board_representation = default_board_representation

    def __is_game_over(self):
        board = get_simple_board()
        player1_checkers = sum(board[0])
        player2_checkers = sum(board[1])
        
        # Check if someone bore off all pieces
        if player1_checkers == 0 or player2_checkers == 0:
            return True
        
        match_info = gnubg.match()
        
        # Check match-level result (more reliable)
        match_result = match_info.get("match-info", {}).get("result", 0)
        if match_result != 0:  # -1 or 1 indicates someone won
            return True
        
        # Also check game-level winner as backup
        if "games" in match_info and match_info["games"]:
            latest_game = match_info["games"][-1]
            if "info" in latest_game and "winner" in latest_game["info"]:
                if latest_game["info"]["winner"] is not None:
                    return True
                    
        return False
    
    def __find_winner(self):
        """Find and return the winner of the completed game."""
        match_info = gnubg.match()
        logger.info(f"Game ended after {self.turn_count} turns.")
        logger.debug(f"Match info: {match_info}")
        
        # Check match-level result first (more reliable)
        game_result = match_info.get("games", {})[0] if match_info.get("games") else {}
        winner = game_result.get("info")
        winner_str = winner.get("winner") if winner else None
        if winner_str is not None:
            winner_index = map_winner(winner_str)
            winner_agent = self.agent1 if winner_index == 0 else self.agent2
            logger.info(f"Game finished. Winner: {winner_agent} (Player {winner_str})")
            return winner_index
                
        logger.warning("No winner found in match info.")
        return None

    def __init_game(self):
        gnubg.command("new game")
        gnubg.command("set player 0 human")
        gnubg.command("set player 1 human")

        logger.debug(f"starting new game with agents: {self.agent1} vs {self.agent2}")
    def play(self):
        self.__init_game()
        self.turn_count = 0
        while self.turn_count < self.max_turns and not self.__is_game_over():
            self.turn_count += 1
            logger.debug(f"Turn {self.turn_count} starting...")
            posinfo = gnubg.posinfo()
            board = self.board_representation()
            turn = posinfo["turn"]
            curr_player = self.agent1 if turn == 0 else self.agent2

            logger.debug(f"Turn {self.turn_count}, Player {curr_player} - Board: {board}")
            roll_dice()
            dice = get_dice()
            logger.debug(f"Player {curr_player} rolled dice: {dice}")
            
            # Handle cube decisions
            if is_cube_decision():
                logger.debug(f"Player {curr_player} has a cube decision")
                cube_handled = handle_cube_decision()
                if cube_handled:
                    # After handling cube decision, check if we need to roll again
                    dice = get_dice()
                    logger.debug(f"After cube decision, dice: {dice}")
                    if dice == (0, 0):
                        # Still a cube situation, continue to next turn
                        continue
                else:
                    logger.warning(f"Failed to handle cube decision for {curr_player}")
                    continue

            possible_moves = get_possible_moves()
            hints = get_hints()
            best_move = get_best_move()
            logger.debug(f"Possible moves: {possible_moves}, Hints: {hints}, Best move: {best_move}")
            if turn == 0:
                extra_input = self.agent1.filter_inputs(possible_moves, hints, best_move)
                move = self.agent1.choose_move(board, extra_input)
            else:
                extra_input = self.agent2.filter_inputs(possible_moves, hints, best_move)
                move = self.agent2.choose_move(board, extra_input)
            move_piece(curr_player, move)
            time.sleep(0.2)

        return self.__find_winner()