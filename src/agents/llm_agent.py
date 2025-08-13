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
    Return one best move according to your analysis.
    """

default_system_prompt = "You are an expert backgammon assistant."

class LLMAgent(Agent):
    """Agent that uses an LLM to select moves (uses prompt if provided)."""
    def __init__(self, inputs: AgentInputConfig = {}, prompt=None, system_prompt=None):
        self.defaultPrompt = prompt or default_prompt
        self.system_prompt = system_prompt or default_system_prompt
        super().__init__(inputs)

    def choose_move(self, board, extra_input: AgentInput = None):
        try:
            possible_moves = extra_input.get("possible_moves", [])
            hints = extra_input.get("hints", [])
            best_move = extra_input.get("best_move", None)

            answer_schema = {
                "full_answer": "str",
                "best_move": "str",
            }
            prompt_with_schema = self.defaultPrompt + "\n\nReturn as JSON with schema: {schema}"
            llm_response = consult_llm(board, prompt=prompt_with_schema, system_prompt=self.system_prompt,
                                           possible_moves=possible_moves, hints=hints, best_move=best_move, schema=answer_schema)

            if llm_response:
                chosen_move = llm_response.get("best_move", None)
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