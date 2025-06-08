import gnubg
import time
from .agents import Agent
from .utils import get_simple_board, get_possible_moves, default_move, move_piece, roll_dice

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


    def play(self):
        self.__init_game()
        self.turn_count = 0
        while self.turn_count < self.max_turns and not self.__is_game_over():
            self.turn_count += 1
            posinfo = gnubg.posinfo()
            board = get_simple_board()
            turn = posinfo["turn"]
            roll_dice()
            possible_moves = get_possible_moves()
            board = get_simple_board()
            if turn == 0:
                move = self.agent1.choose_move(board, possible_moves)
            else:
                move = self.agent2.choose_move(board, possible_moves)
            if move:
                move_piece(move)
            else:
                print(f"Agent {turn} did not choose a valid move. gnubg will play automatically.")
                move = default_move()
                move_piece(move)

            time.sleep(1)

        # Return winner info
        match_info = gnubg.match()
        if "games" in match_info and match_info["games"]:
            latest_game = match_info["games"][-1]
            if "info" in latest_game and "winner" in latest_game["info"]:
                return latest_game["info"]["winner"]
        return None 