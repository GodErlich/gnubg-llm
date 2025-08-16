import os
import json

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

def get_prompts_from_env() -> tuple:
    """Get prompts from environment variables"""
    prompt = os.getenv('GAME_PROMPT', None)
    system_prompt = os.getenv('GAME_SYSTEM_PROMPT', None)
    return prompt, system_prompt

def create_agent(agent_type, inputs: AgentInputConfig=None, prompt: str=None, system_prompt:str=None):
    """Factory function to create agents based on type string"""
    if agent_type == "BestMoveAgent":
        return BestMoveAgent(inputs=inputs)
    elif agent_type == "RandomAgent":
        return RandomAgent(inputs=inputs)
    elif agent_type == "LLMAgent":
        return LLMAgent(inputs=inputs, prompt=prompt, system_prompt=system_prompt)
    elif agent_type == "LiveCodeAgent":
        return LiveCodeAgent(inputs=inputs, prompt=prompt, system_prompt=system_prompt)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

def main():
    # Get configuration from environment variables
    game_id = int(os.getenv('GAME_ID', '1'))
    log_file_name = os.getenv('GAME_LOG_FILE', 'game')
    log_folder_path = os.getenv('GAME_LOG_PATH', 'output')
    agent1_type = os.getenv('GAME_AGENT1', 'BestMoveAgent')
    agent2_type = os.getenv('GAME_AGENT2', 'RandomAgent')
    debug_mode = os.getenv('GAME_DEBUG_MODE', 'false').lower() == 'true'
    
    # Get agent input configuration from environment variables
    agent_inputs = get_agent_input_config_from_env()
    prompt, system_prompt = get_prompts_from_env()
    # Initialize logger with custom parameters
    logger_instance = Logger(log_file=log_file_name, output_folder=log_folder_path, debug_mode=debug_mode)
    
    # update the global logger's debug mode
    from .logger import logger as global_logger
    if global_logger:
        global_logger.set_debug_mode(debug_mode)

    try:
        agent1 = create_agent(agent1_type, inputs=agent_inputs, prompt=prompt, system_prompt=system_prompt)
        agent2 = create_agent(agent2_type, inputs=agent_inputs, prompt=prompt, system_prompt=system_prompt)
    except ValueError as e:
        logger_instance.error(f"Error creating agents: {e}")
        return None

    game = Game(agent1, agent2, game_id=game_id)

    winner, game_stats = game.play()
    
    # Export statistics to JSON file
    try:
        os.makedirs(log_folder_path, exist_ok=True)
        stats_file = os.path.join(log_folder_path, f"{log_file_name}_stats.json")
        with open(stats_file, 'w') as f:
            json.dump(game_stats, f, indent=2)
        logger_instance.debug(f"Statistics exported to {stats_file}")
    except Exception as e:
        logger_instance.error(f"Failed to export statistics: {e}")
    
    return winner, game_stats