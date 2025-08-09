from .game import Game
from .agents import GnuBGAgent, LLMAgent, DebugAgent, RandomAgent

def main():
    # Create agents
    print("Initializing agents...")
    agent0 = DebugAgent(inputs={"possible_moves": True, "hints": True, "best_move": True})
    agent1 = RandomAgent()

    game = Game(agent0, agent1)

    # Play the game
    return game.play()