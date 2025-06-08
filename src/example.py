from .game import Game
from .agents import GnuBGAgent, LLMAgent

def main():
    # Create agents
    print("Initializing agents...")
    agent0 = GnuBGAgent()
    agent1 = GnuBGAgent()

    game = Game(agent0, agent1)

    # Play the game
    game.play()