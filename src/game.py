from unittest import result
import gnubg
import time

from .agents import Agent
from .utils import get_dice, get_simple_board, get_possible_moves, move_piece, roll_dice, get_hints, get_best_move, map_winner
from .logger import logger

class Game:
    """Manages a backgammon game between two agents."""
    def __init__(self, agent1: Agent, agent2: Agent, max_turns=200):
        self.agent1 = agent1
        self.agent2 = agent2
        self.max_turns = max_turns
        self.turn_count = 0

    def __is_game_over(self):
        board = get_simple_board()
        player1_checkers = sum(board[0])
        player2_checkers = sum(board[1])
        if player1_checkers == 0 or player2_checkers == 0:
            return True
        match_info = gnubg.match()
        if "games" in match_info and match_info["games"]:
            latest_game = match_info["games"][-1]
            if "info" in latest_game and "winner" in latest_game["info"]:
                if latest_game["info"]["winner"] is not None:
                    return True
        return False
    
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
            board = get_simple_board()
            turn = posinfo["turn"]
            curr_player = self.agent1 if turn == 0 else self.agent2

            logger.debug(f"Turn {self.turn_count}, Player {curr_player} - Board: {board}")
            roll_dice()
            logger.debug(f"Player {curr_player} rolled dice: {get_dice()}")
            possible_moves = get_possible_moves()
            hints = get_hints()
            best_move = get_best_move()
            # board = get_simple_board()
            logger.debug(f"Possible moves: {possible_moves}, Hints: {hints}, Best move: {best_move}")
            if turn == 0:
                extra_input = self.agent1.filter_inputs(possible_moves, hints, best_move)
                move = self.agent1.choose_move(board, extra_input)
            else:
                extra_input = self.agent2.filter_inputs(possible_moves, hints, best_move)
                move = self.agent2.choose_move(board, extra_input)
            move_piece(curr_player, move)
            time.sleep(1)

        # Return winner info
        match_info = gnubg.match()
        logger.info(f"Game ended after {self.turn_count} turns.")
        logger.debug(f"Match info: {match_info}")


        if "games" in match_info and match_info["games"]:
            latest_game = match_info["games"][-1]
            if "info" in latest_game and "winner" in latest_game["info"]:
                winner = map_winner(latest_game["info"]["winner"])  
                logger.info(f"Game finished. Winner: {self.agent1 if winner == 0 else self.agent2}")
                return winner

        logger.warning("No winner found in match info.")
        return None