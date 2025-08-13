from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..utils import consult_llm
from ..logger import logger


class LLMAgent(Agent):
    """Agent that uses an LLM to select moves (uses prompt if provided)."""
    def __init__(self, inputs: AgentInputConfig = {}, prompt=None, system_prompt=None):
        self.defaultPrompt = prompt
        self.system_prompt = system_prompt
        super().__init__(inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        try:
            possible_moves = extra_input.get("possible_moves", [])
            hints = extra_input.get("hints", [])
            best_move = extra_input.get("best_move", None)

            chosen_move_data = consult_llm(board, prompt=self.defaultPrompt, system_prompt=self.system_prompt, possible_moves=possible_moves, hints=hints, best_move=best_move)

            if chosen_move_data:
                chosen_move = chosen_move_data["move"]
                logger.debug(f"Playing LLM-recommended move: {chosen_move}")
                return chosen_move

            else:
                logger.warning("No moves available")
                return None

        except Exception as e:
            logger.error(f"Error in play_llm_move: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None