from .base import Agent
from ..interfaces import AgentInputConfig, AgentInput
from ..utils import consult_llm
from ..logger import logger


default_prompt = """
    You are an expert backgammon player choosing the best move in this position.
    You have never lost against gnubg because of your superior strategy.
    
    # Current Board Position
    {board_repr}
    
    # Possible Moves (with gnubg evaluations)
    {possible_moves}
    
    # Instructions
    Choose the best move for this position, drawing on both:
    1. Your knowledge of backgammon strategy and tactical patterns
    2. The statistical evaluations from gnubg (shown above)
    
    Consider these factors that might not be fully captured in gnubg's evaluation:
    - Position type (racing, priming, back game, holding game)
    - Tactical patterns (slots, hits, anchors, builders)
    - Checker distribution and flexibility
    - Safety vs. aggression balance
    - Future roll equity
    
    Your analysis should:
    1. Discuss the best move according to your superior knowledge of backgammon.
    2. Identify any strategic patterns or special features of this position
    3. Explain whether you agree or disagree with gnubg's evaluation and why
    
    Remember that negative equity values mean the position is disadvantageous for the player.
    Lower (more negative) values indicate worse moves in this context.
    
    Begin with a brief assessment of the position and what key objectives you see.
    
    Conclude with your recommended move in this exact format:
    RECOMMENDED MOVE: [move notation as shown in the options]
    """


class LLMAgent(Agent):
    """Agent that uses an LLM to select moves (uses prompt if provided)."""
    def __init__(self, inputs: AgentInputConfig = {}, prompt=None, system_prompt=None):
        if prompt is None:
            self.defaultPrompt = default_prompt
        else:
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