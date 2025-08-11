#!/usr/bin/env python3
import subprocess
import os
import argparse
import sys

def run_silent_game(log_file_name, log_folder_name, agent1, agent2, debug_mode):
    """Run a single game silently and return winner"""
    # Set environment variables to pass parameters to the game
    env = os.environ.copy()
    env['GAME_LOG_FILE'] = log_file_name
    env['GAME_LOG_FOLDER'] = log_folder_name
    env['GAME_AGENT1'] = agent1
    env['GAME_AGENT2'] = agent2
    env['GAME_DEBUG_MODE'] = str(debug_mode).lower()
    
    # Redirect gnubg output to /dev/null
    with open(os.devnull, 'w') as devnull:
        result = subprocess.run([
            "gnubg", "-t", "-p", "app.py"
        ], stdout=devnull, stderr=devnull, capture_output=False, env=env)

    # You'll need to modify main.py to output just the winner
    # For now, assuming it returns 0 for player 0 win, 1 for player 1 win
    return result.returncode

def run_batch_games(num_games, log_file_name="game", log_folder_name="output", agent1="DebugAgent", agent2="RandomAgent"):
    """Run multiple games and show summary"""
    print(f"Running {num_games} games...")
    
    player_0_wins = 0
    player_1_wins = 0
    
    for i in range(num_games):
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_games}")
        
        winner = run_silent_game(log_file_name, log_folder_name, agent1, agent2, debug_mode)
        print(f"Winner in game {i + 1}: Player {winner}")
        if winner == 0:
            player_0_wins += 1
        else:
            player_1_wins += 1
    
    print(f"\n=== RESULTS ===")
    print(f"Player 0 ({agent1}) won: {player_0_wins} times ({player_0_wins/num_games*100:.1f}%)")
    print(f"Player 1 ({agent2}) won: {player_1_wins} times ({player_1_wins/num_games*100:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description='Run backgammon games with configurable agents')
    parser.add_argument('--log_file_name', type=str, default='game',
                        help='Name for the log file (default: game)')
    parser.add_argument('--log_folder_name', type=str, default='output',
                        help='Folder name for logs (default: output)')
    parser.add_argument('--agent1', type=str, default='DebugAgent',
                        choices=['DebugAgent', 'RandomAgent', 'LLMAgent', 'LiveCodeAgent'],
                        help='Agent type for player 1 (default: DebugAgent)')
    parser.add_argument('--agent2', type=str, default='RandomAgent',
                        choices=['DebugAgent', 'RandomAgent', 'LLMAgent', 'LiveCodeAgent'],
                        help='Agent type for player 2 (default: RandomAgent)')
    parser.add_argument('--number_of_games', type=int, default=1,
                        help='Number of games to play (default: 1)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.number_of_games <= 0:
        print("Error: number_of_games must be a positive integer")
        sys.exit(1)
    
    run_batch_games(
        num_games=args.number_of_games,
        log_file_name=args.log_file_name,
        log_folder_name=args.log_folder_name,
        agent1=args.agent1,
        agent2=args.agent2,
        debug_mode=args.debug_mode
    )

if __name__ == "__main__":
    main()