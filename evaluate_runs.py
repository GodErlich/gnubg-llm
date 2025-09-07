"""
Game Run Evaluation Script

This script evaluates games based on files inside run_timestamp folders,
using the game_stats.json files to create comprehensive analysis similar
to the game_results functionality in main.py.
"""

import json
import os
import glob
import argparse
import sys
from typing import Dict, List

class GameRunEvaluator:
    """Evaluates and analyzes game runs from run_timestamp folders."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.runs_data = {}
        
    def find_run_folders(self) -> List[str]:
        """Find all run_timestamp folders in the output directory."""
        pattern = os.path.join(self.output_dir, "run_*")
        run_folders = glob.glob(pattern)
        return sorted(run_folders)
    
    def load_game_stats(self, run_folder: str) -> List[Dict]:
        """Load all game_stats.json files from a run folder."""
        stats_files = glob.glob(os.path.join(run_folder, "*_stats.json"))
        game_results = []
        
        for stats_file in sorted(stats_files):
            try:
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                    game_results.append(stats)
            except Exception as e:
                print(f"Warning: Could not read {stats_file}: {e}")
                continue
                
        return game_results
    
    def analyze_run(self, run_folder: str) -> Dict:
        """Analyze a single run folder and return comprehensive statistics."""
        run_name = os.path.basename(run_folder)
        game_results = self.load_game_stats(run_folder)
        
        if not game_results:
            return {
                "run_name": run_name,
                "run_folder": run_folder,
                "num_games": 0,
                "error": "No game statistics found"
            }
        
        # Initialize counters
        agent1_wins = 0
        agent2_wins = 0
        total_invalid_moves_p1 = 0
        total_invalid_moves_p2 = 0
        total_moves_p1 = 0
        total_moves_p2 = 0
        total_duration = 0
        total_turns = 0
        game_types = {"normal": 0, "gammon": 0, "backgammon": 0}
        
        # Get agent names from first game
        agent1_name = game_results[0].get("player1_stats", {}).get("name", "Player1")
        agent2_name = game_results[0].get("player2_stats", {}).get("name", "Player2")
        
        # Process each game
        for game in game_results:
            winner = game.get("winner")
            if winner == 0:
                agent1_wins += 1
            elif winner == 1:
                agent2_wins += 1
            
            # Aggregate statistics
            p1_stats = game.get("player1_stats", {})
            p2_stats = game.get("player2_stats", {})
            
            total_invalid_moves_p1 += p1_stats.get("invalid_moves", 0)
            total_invalid_moves_p2 += p2_stats.get("invalid_moves", 0)
            total_moves_p1 += p1_stats.get("total_moves", 0)
            total_moves_p2 += p2_stats.get("total_moves", 0)
            total_duration += game.get("game_duration", 0)
            total_turns += game.get("total_turns", 0)
            
            game_type = game.get("game_type", "normal")
            game_types[game_type] = game_types.get(game_type, 0) + 1
        
        num_games = len(game_results)
        
        return {
            "run_name": run_name,
            "run_folder": run_folder,
            "num_games": num_games,
            "agent1_name": agent1_name,
            "agent2_name": agent2_name,
            "agent1_wins": agent1_wins,
            "agent2_wins": agent2_wins,
            "agent1_win_rate": agent1_wins / num_games * 100 if num_games > 0 else 0,
            "agent2_win_rate": agent2_wins / num_games * 100 if num_games > 0 else 0,
            "total_duration": total_duration,
            "avg_duration": total_duration / num_games if num_games > 0 else 0,
            "total_turns": total_turns,
            "avg_turns": total_turns / num_games if num_games > 0 else 0,
            "total_invalid_moves_p1": total_invalid_moves_p1,
            "total_invalid_moves_p2": total_invalid_moves_p2,
            "total_moves_p1": total_moves_p1,
            "total_moves_p2": total_moves_p2,
            "invalid_move_rate_p1": total_invalid_moves_p1 / total_moves_p1 * 100 if total_moves_p1 > 0 else 0,
            "invalid_move_rate_p2": total_invalid_moves_p2 / total_moves_p2 * 100 if total_moves_p2 > 0 else 0,
            "game_types": game_types,
            "game_results": game_results
        }
    
    def evaluate_all_runs(self) -> Dict:
        """Evaluate all run folders and return comprehensive analysis."""
        run_folders = self.find_run_folders()
        
        if not run_folders:
            return {"error": f"No run folders found in {self.output_dir}"}
        
        print(f"Found {len(run_folders)} run folders to analyze:")
        for folder in run_folders:
            print(f"  - {os.path.basename(folder)}")
        
        runs_analysis = {}
        for run_folder in run_folders:
            print(f"\nAnalyzing {os.path.basename(run_folder)}...")
            analysis = self.analyze_run(run_folder)
            runs_analysis[analysis["run_name"]] = analysis
        
        return runs_analysis
    
    def print_detailed_report(self, runs_analysis: Dict):
        """Print a detailed report similar to main.py's output format."""
        print(f"\n{'='*80}")
        print(f"{'GAME RUN EVALUATION REPORT':^80}")
        print(f"{'='*80}")
        
        # Summary of all runs
        total_runs = len(runs_analysis)
        total_games = sum(run.get("num_games", 0) for run in runs_analysis.values())
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total runs analyzed: {total_runs}")
        print(f"   Total games across all runs: {total_games}")
        
        # Individual run analysis
        for run_name, analysis in runs_analysis.items():
            if analysis.get("error"):
                print(f"\n❌ {run_name}: {analysis['error']}")
                continue
                
            print(f"\n{'='*80}")
            print(f"RUN: {run_name}")
            print(f"{'='*80}")
            
            # Overall results
            print(f"\n🏆 OVERALL RESULTS:")
            print(f"   {analysis['agent1_name']} won: {analysis['agent1_wins']} times ({analysis['agent1_win_rate']:.1f}%)")
            print(f"   {analysis['agent2_name']} won: {analysis['agent2_wins']} times ({analysis['agent2_win_rate']:.1f}%)")
            
            # Game-by-game results
            print(f"\n📊 GAME-BY-GAME RESULTS:")
            print(f"{'Game':<4} {'Winner':<12} {'Loser':<12} {'Duration':<8} {'Turns':<6} {'Invalid Moves (P1/P2)':<20} {'Checkers Left (Loser)':<18} {'Type':<10}")
            print(f"{'-'*100}")
            
            for game in analysis["game_results"]:
                game_id = game["game_id"]
                winner_name = game["winner_name"][:10]
                loser_name = game["loser_name"][:10]
                
                duration = f"{game.get('game_duration', 0):.1f}s"
                turns = game.get('total_turns', 'N/A')
                
                p1_invalid = game.get("player1_stats", {}).get("invalid_moves", 0)
                p2_invalid = game.get("player2_stats", {}).get("invalid_moves", 0)
                invalid_moves = f"{p1_invalid}/{p2_invalid}"
                
                loser_checkers = "N/A"
                if game.get("winner") == 0:  # Player 1 won
                    loser_checkers = game.get("player2_stats", {}).get("checkers_remaining", "N/A")
                elif game.get("winner") == 1:  # Player 2 won
                    loser_checkers = game.get("player1_stats", {}).get("checkers_remaining", "N/A")
                
                game_type = game.get('game_type', 'N/A')
                
                print(f"{game_id:<4} {winner_name:<12} {loser_name:<12} {duration:<8} {turns:<6} {invalid_moves:<20} {loser_checkers:<18} {game_type:<10}")
            
            # Aggregate statistics
            print(f"\n📈 AGGREGATE STATISTICS:")
            print(f"   Total games: {analysis['num_games']}")
            print(f"   Average game duration: {analysis['avg_duration']:.2f} seconds")
            print(f"   Average turns per game: {analysis['avg_turns']:.1f}")
            print(f"   Total invalid moves - {analysis['agent1_name']}: {analysis['total_invalid_moves_p1']}, {analysis['agent2_name']}: {analysis['total_invalid_moves_p2']}")
            print(f"   Invalid move rate - {analysis['agent1_name']}: {analysis['invalid_move_rate_p1']:.2f}%")
            print(f"   Invalid move rate - {analysis['agent2_name']}: {analysis['invalid_move_rate_p2']:.2f}%")
            
            print(f"\n🎯 GAME TYPES:")
            for game_type, count in analysis['game_types'].items():
                if count > 0:
                    percentage = count / analysis['num_games'] * 100
                    print(f"   {game_type.capitalize()}: {count} games ({percentage:.1f}%)")
    
    
    def compare_runs(self, runs_analysis: Dict):
        """Compare performance across different runs."""
        print(f"\n{'='*80}")
        print(f"{'RUN COMPARISON':^80}")
        print(f"{'='*80}")
        
        # Filter out runs with errors
        valid_runs = {k: v for k, v in runs_analysis.items() if not v.get("error")}
        
        if len(valid_runs) < 2:
            print("Need at least 2 valid runs for comparison.")
            return
        
        print(f"\n📈 PERFORMANCE COMPARISON:")
        print(f"{'Run':<20} {'Games':<6} {'Agent1 Win%':<12} {'Agent2 Win%':<12} {'Avg Duration':<12} {'Avg Turns':<10}")
        print(f"{'-'*80}")
        
        for run_name, analysis in valid_runs.items():
            print(f"{run_name:<20} {analysis['num_games']:<6} {analysis['agent1_win_rate']:<11.1f}% {analysis['agent2_win_rate']:<11.1f}% {analysis['avg_duration']:<11.2f}s {analysis['avg_turns']:<9.1f}")
        print(f"{'-'*80}")

def main():
    parser = argparse.ArgumentParser(description='Evaluate backgammon game runs from run_timestamp folders')
    parser.add_argument('--output_dir', '--dir', type=str, default='output',
                        help='Directory containing run folders (default: output)')
    parser.add_argument('--run_folder', '--run', type=str, default=None,
                        help='Analyze specific run folder (default: analyze all)')
    parser.add_argument('--compare', '--comp', action='store_true', default=False,
                        help='Compare performance across runs')
    parser.add_argument('--quiet', '--q', action='store_true', default=False,
                        help='Suppress detailed output, only show summary')
    
    args = parser.parse_args()
    
    # Validate output directory
    if not os.path.exists(args.output_dir):
        print(f"Error: Output directory '{args.output_dir}' does not exist")
        sys.exit(1)
    
    evaluator = GameRunEvaluator(args.output_dir)
    
    if args.run_folder:
        # Analyze specific run folder
        run_path = os.path.join(args.output_dir, args.run_folder)
        if not os.path.exists(run_path):
            print(f"Error: Run folder '{run_path}' does not exist")
            sys.exit(1)
        
        analysis = evaluator.analyze_run(run_path)
        runs_analysis = {analysis["run_name"]: analysis}
    else:
        # Analyze all runs
        runs_analysis = evaluator.evaluate_all_runs()
        
        if "error" in runs_analysis:
            print(f"Error: {runs_analysis['error']}")
            sys.exit(1)
    
    # Print detailed report unless quiet mode
    if not args.quiet:
        evaluator.print_detailed_report(runs_analysis)
    
    # Compare runs if requested
    if args.compare and len(runs_analysis) > 1:
        evaluator.compare_runs(runs_analysis)
        
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()