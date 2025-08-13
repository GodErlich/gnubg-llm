import os

from .interfaces import AgentInputConfig
from .game import Game
from .agents import BestMoveAgent, RandomAgent, LLMAgent, LiveCodeAgent
from .logger import Logger

def get_agent_input_config_from_env() -> AgentInputConfig:
    """Get AgentInputConfig from environment variables"""
    return AgentInputConfig(
        possible_moves=os.getenv('GAME_POSSIBLE_MOVES', 'false').lower() == 'true',
        hints=os.getenv('GAME_HINTS', 'false').lower() == 'true',
        best_move=os.getenv('GAME_BEST_MOVE', 'false').lower() == 'true'
    )

def create_agent(agent_type, inputs: AgentInputConfig=None):
    """Factory function to create agents based on type string"""
    if agent_type == "BestMoveAgent":
        return BestMoveAgent(inputs=inputs)
    elif agent_type == "RandomAgent":
        return RandomAgent(inputs=inputs)
    elif agent_type == "LLMAgent":
        return LLMAgent(inputs=inputs)
    elif agent_type == "LiveCodeAgent":
        # Note: LiveCodeAgent is not fully implemented yet. return LLM for now.
        #return LiveCodeAgent(inputs=inputs)
        return LLMAgent(inputs=inputs)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

def main():
    # Get configuration from environment variables
    log_file_name = os.getenv('GAME_LOG_FILE', 'game')
    log_folder_path = os.getenv('GAME_LOG_PATH', 'output')
    agent1_type = os.getenv('GAME_AGENT1', 'BestMoveAgent')
    agent2_type = os.getenv('GAME_AGENT2', 'RandomAgent')
    debug_mode = os.getenv('GAME_DEBUG_MODE', 'true').lower() == 'true'
    
    # Get agent input configuration from environment variables
    agent_inputs = get_agent_input_config_from_env()

    # Initialize logger with custom parameters
    logger = Logger(log_file=log_file_name, output_folder=log_folder_path, debug_mode=debug_mode)
    
    try:
        agent1 = create_agent(agent1_type, inputs=agent_inputs)
        agent2 = create_agent(agent2_type, inputs=agent_inputs)
    except ValueError as e:
        logger.error(f"Error creating agents: {e}")
        return None

    game = Game(agent1, agent2)

    # Play the game
    result = game.play()
    return result