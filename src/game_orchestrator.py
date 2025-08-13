import os
from .game import Game
from .agents import BestMoveAgent, RandomAgent, LLMAgent, LiveCodeAgent
from .logger import Logger

def create_agent(agent_type):
    """Factory function to create agents based on type string"""
    if agent_type == "BestMoveAgent":
        return BestMoveAgent(inputs={"best_move": True})
    elif agent_type == "RandomAgent":
        return RandomAgent(inputs={"possible_moves": True})
    elif agent_type == "LLMAgent":
        return LLMAgent()
    elif agent_type == "LiveCodeAgent":
        return LiveCodeAgent()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

def main():
    # Get configuration from environment variables
    log_file_name = os.getenv('GAME_LOG_FILE', 'game')
    log_folder_path = os.getenv('GAME_LOG_PATH', 'output')
    agent1_type = os.getenv('GAME_AGENT1', 'BestMoveAgent')
    agent2_type = os.getenv('GAME_AGENT2', 'RandomAgent')
    debug_mode = os.getenv('GAME_DEBUG_MODE', 'true').lower() == 'true'

    # Initialize logger with custom parameters
    logger = Logger(log_file=log_file_name, output_folder=log_folder_path, debug_mode=debug_mode)
    
    try:
        agent0 = create_agent(agent1_type)
        agent1 = create_agent(agent2_type)
    except ValueError as e:
        logger.error(f"Error creating agents: {e}")
        return None

    game = Game(agent0, agent1)

    # Play the game
    result = game.play()
    return result