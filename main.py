#!/usr/bin/env python3
import subprocess
import os

def run_silent_game():
    """Run a single game silently and return winner"""
    # Redirect gnubg output to /dev/null
    with open(os.devnull, 'w') as devnull:
        result = subprocess.run([
            "gnubg", "-t", "-p", "app.py"
        ], stdout=devnull, stderr=devnull, capture_output=False)
    
    # You'll need to modify main.py to output just the winner
    # For now, assuming it returns 0 for player 0 win, 1 for player 1 win
    return result.returncode

def run_batch_games(num_games=2):
    """Run multiple games and show summary"""
    print(f"Running {num_games} games...")
    
    player_0_wins = 0
    player_1_wins = 0
    
    for i in range(num_games):
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_games}")
        
        winner = run_silent_game()
        print(winner)
        if winner == 0:
            player_0_wins += 1
        else:
            player_1_wins += 1
    
    print(f"\n=== RESULTS ===")
    print(f"Player 0 won: {player_0_wins} times ({player_0_wins/num_games*100:.1f}%)")
    print(f"Player 1 won: {player_1_wins} times ({player_1_wins/num_games*100:.1f}%)")

if __name__ == "__main__":
    run_batch_games()