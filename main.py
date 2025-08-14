#!/usr/bin/env python3
import subprocess
import os
import argparse
import sys

def run_silent_game(game_id, log_file_name, log_folder_path, agent1, agent2, debug_mode, possible_moves=False, hints=False, best_move=False, prompt=None, system_prompt=None):
    """Run a single game silently and return winner and statistics"""
    # Set environment variables to pass parameters to the game
    env = os.environ.copy()
    env['GAME_ID'] = str(game_id)
    env['GAME_LOG_FILE'] = f"{log_file_name}_{game_id}"
    env['GAME_LOG_PATH'] = log_folder_path
    env['GAME_AGENT1'] = agent1
    env['GAME_AGENT2'] = agent2
    env['GAME_DEBUG_MODE'] = str(debug_mode).lower()
    env['GAME_POSSIBLE_MOVES'] = str(possible_moves).lower()
    env['GAME_HINTS'] = str(hints).lower()
    env['GAME_BEST_MOVE'] = str(best_move).lower()
    env['GAME_PROMPT'] = prompt or ""
    env['GAME_SYSTEM_PROMPT'] = system_prompt or ""
    
    # Redirect gnubg output to /dev/null
    with open(os.devnull, 'w') as devnull:
        result = subprocess.run([
            "gnubg", "-t", "-p", "app.py"
        ], stdout=devnull, stderr=devnull, capture_output=False, env=env)

    # Return the exit code (should be winner index or error code)
    return result.returncode

def run_batch_games(num_games, log_file_name="game", log_folder_path="output", agent1="BestMoveAgent", agent2="RandomAgent", debug_mode=True, possible_moves=False, hints=False, best_move=False, prompt=None, system_prompt=None, export_csv=False):
    """Run multiple games and show summary with detailed statistics"""
    print(f"Running {num_games} games...")
    
    agent1_wins = 0
    agent2_wins = 0
    game_results = []
    
    # Statistics tracking
    total_invalid_moves_p1 = 0
    total_invalid_moves_p2 = 0
    total_moves_p1 = 0
    total_moves_p2 = 0
    total_duration = 0
    total_turns = 0
    game_types = {"normal": 0, "gammon": 0, "backgammon": 0}

    for i in range(num_games):
        game_id = i + 1
        if game_id % 10 == 0:
            print(f"Progress: {game_id}/{num_games}")
        
        winner = run_silent_game(game_id, log_file_name, log_folder_path, agent1, agent2, debug_mode, possible_moves, hints, best_move, prompt, system_prompt)
        
        # Read game statistics from log file if available
        stats_file = os.path.join(log_folder_path, f"{log_file_name}_{game_id}_stats.json")
        
        game_result = {
            "game_id": game_id,
            "winner": winner,
            "winner_name": agent1 if winner == 0 else agent2 if winner == 1 else "Unknown",
            "loser_name": agent2 if winner == 0 else agent1 if winner == 1 else "Unknown"
        }
        
        if os.path.exists(stats_file):
            try:
                import json
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                    game_result.update(stats)
                    
                    # Aggregate statistics
                    total_invalid_moves_p1 += stats.get("player1_stats", {}).get("invalid_moves", 0)
                    total_invalid_moves_p2 += stats.get("player2_stats", {}).get("invalid_moves", 0)
                    total_moves_p1 += stats.get("player1_stats", {}).get("total_moves", 0)
                    total_moves_p2 += stats.get("player2_stats", {}).get("total_moves", 0)
                    total_duration += stats.get("game_duration", 0)
                    total_turns += stats.get("total_turns", 0)
                    
                    game_type = stats.get("game_type", "normal")
                    game_types[game_type] = game_types.get(game_type, 0) + 1
                    
            except Exception as e:
                print(f"Warning: Could not read statistics for game {game_id}: {e}")
        
        game_results.append(game_result)
        
        if winner == 0:
            agent1_wins += 1
        elif winner == 1:
            agent2_wins += 1
        else:
            print(f"Game {game_id} ended in an unknown state. Winner: {winner}")

    # Display results
    print(f"\n{'='*60}")
    print(f"{'GAME RESULTS':^60}")
    print(f"{'='*60}")
    
    # Overall win statistics
    print(f"\n🏆 OVERALL RESULTS:")
    print(f"   Player 0 ({agent1}) won: {agent1_wins} times ({agent1_wins/num_games*100:.1f}%)")
    print(f"   Player 1 ({agent2}) won: {agent2_wins} times ({agent2_wins/num_games*100:.1f}%)")
    
    # Game-by-game results
    print(f"\n📊 GAME-BY-GAME RESULTS:")
    print(f"{'Game':<4} {'Winner':<12} {'Loser':<12} {'Duration':<8} {'Turns':<6} {'Invalid Moves (P1/P2)':<20} {'Checkers Left (Loser)':<18} {'Type':<10}")
    print(f"{'-'*100}")
    
    for result in game_results:
        game_id = result["game_id"]
        winner_name = result["winner_name"][:10]
        loser_name = result["loser_name"][:10]
        
        duration = f"{result.get('game_duration', 0):.1f}s" if result.get('game_duration') else "N/A"
        turns = result.get('total_turns', 'N/A')
        
        p1_invalid = result.get("player1_stats", {}).get("invalid_moves", 0)
        p2_invalid = result.get("player2_stats", {}).get("invalid_moves", 0)
        invalid_moves = f"{p1_invalid}/{p2_invalid}"
        
        loser_checkers = "N/A"
        if result.get("winner") == 0:  # Player 1 won
            loser_checkers = result.get("player2_stats", {}).get("checkers_remaining", "N/A")
        elif result.get("winner") == 1:  # Player 2 won
            loser_checkers = result.get("player1_stats", {}).get("checkers_remaining", "N/A")
            
        game_type = result.get('game_type', 'N/A')
        
        print(f"{game_id:<4} {winner_name:<12} {loser_name:<12} {duration:<8} {turns:<6} {invalid_moves:<20} {loser_checkers:<18} {game_type:<10}")
    
    # Aggregate statistics
    if num_games > 0:
        print(f"\n📈 AGGREGATE STATISTICS:")
        print(f"   Average game duration: {total_duration/num_games:.2f} seconds")
        print(f"   Average turns per game: {total_turns/num_games:.1f}")
        print(f"   Total invalid moves - {agent1}: {total_invalid_moves_p1}, {agent2}: {total_invalid_moves_p2}")
        if total_moves_p1 > 0:
            print(f"   Invalid move rate - {agent1}: {total_invalid_moves_p1/total_moves_p1*100:.2f}%")
        if total_moves_p2 > 0:
            print(f"   Invalid move rate - {agent2}: {total_invalid_moves_p2/total_moves_p2*100:.2f}%")
        
        print(f"\n🎯 GAME TYPES:")
        for game_type, count in game_types.items():
            if count > 0:
                print(f"   {game_type.capitalize()}: {count} games ({count/num_games*100:.1f}%)")
    
    # Export to CSV if requested
    if export_csv and game_results:
        try:
            import csv
            csv_file = os.path.join(log_folder_path, f"{log_file_name}_summary.csv")
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'Game_ID', 'Winner', 'Loser', 'Winner_Agent', 'Loser_Agent',
                    'Duration_Seconds', 'Total_Turns', 'Game_Type',
                    'P1_Invalid_Moves', 'P1_Total_Moves', 'P1_Checkers_Remaining', 'P1_Checkers_On_Bar', 'P1_Pip_Count',
                    'P2_Invalid_Moves', 'P2_Total_Moves', 'P2_Checkers_Remaining', 'P2_Checkers_On_Bar', 'P2_Pip_Count',
                    'Final_Score_Difference'
                ])
                
                # Write data rows
                for result in game_results:
                    p1_stats = result.get("player1_stats", {})
                    p2_stats = result.get("player2_stats", {})
                    
                    writer.writerow([
                        result.get("game_id", ""),
                        result.get("winner", ""),
                        result.get("loser", ""),
                        result.get("winner_name", ""),
                        result.get("loser_name", ""),
                        result.get("game_duration", ""),
                        result.get("total_turns", ""),
                        result.get("game_type", ""),
                        p1_stats.get("invalid_moves", ""),
                        p1_stats.get("total_moves", ""),
                        p1_stats.get("checkers_remaining", ""),
                        p1_stats.get("checkers_on_bar", ""),
                        p1_stats.get("pip_count", ""),
                        p2_stats.get("invalid_moves", ""),
                        p2_stats.get("total_moves", ""),
                        p2_stats.get("checkers_remaining", ""),
                        p2_stats.get("checkers_on_bar", ""),
                        p2_stats.get("pip_count", ""),
                        result.get("final_score_difference", "")
                    ])
                    
            print(f"\n📁 CSV exported to: {csv_file}")
            
        except Exception as e:
            print(f"\n❌ Failed to export CSV: {e}")
    
    print(f"\n{'='*60}")

def main():
    parser = argparse.ArgumentParser(description='Run backgammon games with configurable agents')
    parser.add_argument('--log_file_name', '--fn', type=str, default='game',
                        help='Name for the log file (default: game)')
    parser.add_argument('--prompt', '--p', type=str, default=None,
                        help='Custom prompt for the LLM agent (default: None)')
    parser.add_argument('--system_prompt', '--sp', type=str, default=None,
                        help='Custom system prompt for the LLM agent (default: None)')
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
    parser.add_argument('--debug_mode', '--d', action='store_true', default=False,
                        help='Enable debug mode for detailed logging (default: False)')
    
    # Agent input configuration arguments
    parser.add_argument('--possible_moves', '--pm', action='store_true', default=False,
                        help='Enable possible moves input for agents')
    parser.add_argument('--hints', '--hi', action='store_true', default=False,
                        help='Enable hints input for agents')
    parser.add_argument('--best_move', '--bm', action='store_true', default=False,
                        help='Enable best move input for agents')
    parser.add_argument('--export_csv', '--csv', action='store_true', default=False,
                        help='Export detailed statistics to CSV file')
    
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
        prompt=args.prompt,
        system_prompt=args.system_prompt,
        possible_moves=args.possible_moves,
        hints=args.hints,
        best_move=args.best_move,
        export_csv=args.export_csv
    )

if __name__ == "__main__":
    main()