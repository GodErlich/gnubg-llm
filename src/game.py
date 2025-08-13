import gnubg
from typing import Callable
import time

from .agents import Agent
from .utils import (default_board_representation, get_dice, get_simple_board, get_possible_moves, 
                   move_piece, roll_dice, get_hints, get_best_move, map_winner, is_cube_decision, 
                   handle_cube_decision, get_pip_count, get_checkers_count, get_checkers_on_bar, 
                   determine_game_type, create_player_statistics)
from .interfaces import GameStatistics, PlayerStatistics
from .logger import logger

class Game:
    """Manages a backgammon game between two agents."""
    def __init__(self, agent1: Agent, agent2: Agent, max_turns: int = 200, board_representation: Callable[[], str] = None, game_id: int = 0):
        self.agent1 = agent1
        self.agent2 = agent2
        self.max_turns = max_turns
        self.turn_count = 0
        self.game_id = game_id
        self.start_time = 0
        self.end_time = 0
        
        # Initialize statistics
        self.player1_stats = create_player_statistics(str(agent1))
        self.player2_stats = create_player_statistics(str(agent2))
        
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

    def __track_move(self, player_num: int, move: str, is_valid: bool):
        """Track move statistics for a player."""
        if player_num == 0:
            self.player1_stats["total_moves"] += 1
            if not is_valid:
                self.player1_stats["invalid_moves"] += 1
        else:
            self.player2_stats["total_moves"] += 1
            if not is_valid:
                self.player2_stats["invalid_moves"] += 1

    def __track_cube_decision(self, player_num: int, decision: str):
        """Track cube decision statistics."""
        if player_num == 0:
            self.player1_stats["cube_decisions"] += 1
            if decision == "accept":
                self.player1_stats["cube_accepts"] += 1
            elif decision == "reject":
                self.player1_stats["cube_rejects"] += 1
        else:
            self.player2_stats["cube_decisions"] += 1
            if decision == "accept":
                self.player2_stats["cube_accepts"] += 1
            elif decision == "reject":
                self.player2_stats["cube_rejects"] += 1

    def __update_final_statistics(self, winner_index: int):
        """Update final game statistics."""
        # Get final board state
        checkers_count = get_checkers_count()
        checkers_on_bar = get_checkers_on_bar()
        pip_counts = get_pip_count()

        # Update player 1 stats
        self.player1_stats["checkers_remaining"] = checkers_count[0]
        self.player1_stats["checkers_on_bar"] = checkers_on_bar[0]
        self.player1_stats["pip_count"] = pip_counts[0]

        # Update player 2 stats
        self.player2_stats["checkers_remaining"] = checkers_count[1]
        self.player2_stats["checkers_on_bar"] = checkers_on_bar[1]
        self.player2_stats["pip_count"] = pip_counts[1]

    def get_game_statistics(self, winner_index: int) -> GameStatistics:
        """Generate comprehensive game statistics."""
        self.end_time = time.time()
        self.__update_final_statistics(winner_index)
        
        loser_index = 1 - winner_index if winner_index is not None else None
        winner_checkers = self.player1_stats["checkers_remaining"] if winner_index == 0 else self.player2_stats["checkers_remaining"]
        loser_checkers = self.player2_stats["checkers_remaining"] if winner_index == 0 else self.player1_stats["checkers_remaining"]
        
        # Determine game type
        game_type = determine_game_type(winner_checkers, loser_checkers)
        
        # Calculate score difference (pip count difference)
        final_score_difference = abs(self.player1_stats["pip_count"] - self.player2_stats["pip_count"])
        
        return GameStatistics(
            game_id=self.game_id,
            winner=winner_index if winner_index is not None else -1,
            loser=loser_index if loser_index is not None else -1,
            winner_name=self.player1_stats["name"] if winner_index == 0 else self.player2_stats["name"] if winner_index == 1 else "Unknown",
            loser_name=self.player2_stats["name"] if winner_index == 0 else self.player1_stats["name"] if winner_index == 1 else "Unknown",
            total_turns=self.turn_count,
            game_duration=self.end_time - self.start_time,
            player1_stats=self.player1_stats,
            player2_stats=self.player2_stats,
            final_score_difference=final_score_difference,
            game_type=game_type
        )

    def __init_game(self):
        gnubg.command("new game")
        gnubg.command("set player 0 human")
        gnubg.command("set player 1 human")

        logger.debug(f"starting new game with agents: {self.agent1} vs {self.agent2}")
    def play(self):
        self.__init_game()
        self.start_time = time.time()
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
                self.__track_cube_decision(turn, "decision")
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
            
            # Get move from appropriate agent
            if turn == 0:
                extra_input = self.agent1.filter_inputs(possible_moves, hints, best_move)
                move = self.agent1.choose_move(board, extra_input)
            else:
                extra_input = self.agent2.filter_inputs(possible_moves, hints, best_move)
                move = self.agent2.choose_move(board, extra_input)
            
            # Track move and validate
            is_valid_move = move is not None and move in possible_moves if possible_moves else move is not None
            self.__track_move(turn, move, is_valid_move)
            
            # Execute move
            move_piece(curr_player, move)

        winner = self.__find_winner()
        return winner, self.get_game_statistics(winner)