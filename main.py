#!/usr/bin/env python3
import subprocess
import os
import argparse
import sys

def run_silent_game(log_file_name, log_folder_path, agent1, agent2, debug_mode, possible_moves=False, hints=False, best_move=False):
    """Run a single game silently and return winner"""
    # Set environment variables to pass parameters to the game
    env = os.environ.copy()
    env['GAME_LOG_FILE'] = log_file_name
    env['GAME_LOG_PATH'] = log_folder_path
    env['GAME_AGENT1'] = agent1
    env['GAME_AGENT2'] = agent2
    env['GAME_DEBUG_MODE'] = str(debug_mode).lower()
    env['GAME_POSSIBLE_MOVES'] = str(possible_moves).lower()
    env['GAME_HINTS'] = str(hints).lower()
    env['GAME_BEST_MOVE'] = str(best_move).lower()
    
    # Redirect gnubg output to /dev/null
    with open(os.devnull, 'w') as devnull:
        result = subprocess.run([
            "gnubg", "-t", "-p", "app.py"
        ], stdout=devnull, stderr=devnull, capture_output=False, env=env)

    # You'll need to modify main.py to output just the winner
    # For now, assuming it returns 0 for player 0 win, 1 for player 1 win
    return result.returncode

def run_batch_games(num_games, log_file_name="game", log_folder_path="output", agent1="BestMoveAgent", agent2="RandomAgent", debug_mode=True, possible_moves=False, hints=False, best_move=False):
    """Run multiple games and show summary"""
    print(f"Running {num_games} games...")
    
    agent1_wins = 0
    agent2_wins = 0

    for i in range(num_games):
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_games}")
        
        winner = run_silent_game(log_file_name, log_folder_path, agent1, agent2, debug_mode, possible_moves, hints, best_move)
        if winner == 0:
            agent1_wins += 1
        elif winner == 1:
            agent2_wins += 1
        else:
            print(f"Game {i + 1} ended in an unknown state. Winner: {winner}")

    print(f"\n=== RESULTS ===")
    print(f"Player 0 ({agent1}) won: {agent1_wins} times ({agent1_wins/num_games*100:.1f}%)")
    print(f"Player 1 ({agent2}) won: {agent2_wins} times ({agent2_wins/num_games*100:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description='Run backgammon games with configurable agents')
    parser.add_argument('--log_file_name', '--fn', type=str, default='game',
                        help='Name for the log file (default: game)')
    parser.add_argument('--log_folder_path', '--fp', type=str, default='output',
                        help='Folder path for logs (default: output)')
    parser.add_argument('--agent1', '--a1', type=str, default='BestMoveAgent',
                        choices=['BestMoveAgent', 'RandomAgent', 'LLMAgent', 'LiveCodeAgent'],
                        help='Agent type for player 1 (default: BestMoveAgent)')
    parser.add_argument('--agent2', '--a2', type=str, default='RandomAgent',
                        choices=['BestMoveAgent', 'RandomAgent', 'LLMAgent', 'LiveCodeAgent'],
                        help='Agent type for player 2 (default: RandomAgent)')
    parser.add_argument('--number_of_games', '--n', type=int, default=1,
                        help='Number of games to play (default: 1)')
    parser.add_argument('--debug_mode', '--d', action='store_true', default=True,
                        help='Enable debug mode for detailed logging (default: False)') #TODO: return debug mode to false
    
    # Agent input configuration arguments
    parser.add_argument('--possible_moves', '--pm', action='store_true', default=False,
                        help='Enable possible moves input for agents')
    parser.add_argument('--hints', '--hi', action='store_true', default=False,
                        help='Enable hints input for agents')
    parser.add_argument('--best_move', '--bm', action='store_true', default=False,
                        help='Enable best move input for agents')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.number_of_games <= 0:
        print("Error: number_of_games must be a positive integer")
        sys.exit(1)
    
    run_batch_games(
        num_games=args.number_of_games,
        log_file_name=args.log_file_name,
        log_folder_path=args.log_folder_path,
        agent1=args.agent1,
        agent2=args.agent2,
        debug_mode=args.debug_mode,
        possible_moves=args.possible_moves,
        hints=args.hints,
        best_move=args.best_move
    )

if __name__ == "__main__":
    main()