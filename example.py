from game import Game
from agents import GnuBGAgent, LLMAgent
import time

def main():
    # Create agents
    print("Initializing agents...")
    agent0 = GnuBGAgent()
    agent1 = LLMAgent()
    time.sleep(30) # Simulate some delay for initialization
    # Initialize the game
    game = Game(agent0, agent1)

    # Play the game
    game.play()