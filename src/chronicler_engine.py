"""
Chronicler Engine: Pure Narrative Generation

The Chronicler is responsible for ONLY writing D&D-style prose.
No mechanics - just vivid storytelling based on what the Arbiter calculated.
"""

import os

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import Agent


class ChroniclerProse(BaseModel):
    """D&D-style narrative prose."""
    
    narrative: str = Field(
        description="DM-style narration of what happened (2-3 sentences, vivid and flavorful)"
    )


class ChroniclerEngine:
    """
    The Narrative Chronicler: Writes D&D prose from Arbiter results.
    
    Design:
    - Uses larger, creative model (llama3.2:3b)
    - Prompt focuses ONLY on storytelling
    - Receives Arbiter's state changes as input
    """
    
    def __init__(
        self,
        model_name: str = 'ollama:llama3.2:3b',
        tone: str = "humorous"
    ):
        """
        Initialize chronicler engine.
        
        Args:
            model_name: Larger Ollama model for creative prose
            tone: Narrative style (humorous, serious, gritty)
        """
        # Set Ollama base URL
        if 'OLLAMA_BASE_URL' not in os.environ:
            os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
        
        self.tone = tone
        system_prompt = self._build_chronicler_prompt(tone)
        
        logger.info(f"Initializing Chronicler with {model_name}")
        
        self.agent = Agent(
            model_name,
            output_type=ChroniclerProse,
            system_prompt=system_prompt
        )
    
    def _build_chronicler_prompt(self, tone: str) -> str:
        """Construct focused prompt for narrative generation."""
        base = (
            "You are the CHRONICLER: a creative storyteller for a D&D-style RPG.\n\n"
            "Your ONLY job is to narrate what happened. DO NOT calculate stats.\n\n"
            "Rules:\n"
            "- Write 2-3 vivid sentences\n"
            "- Use the provided outcome data to guide your story\n"
            "- Make NPCs feel alive with personality\n"
            "- Focus on player agency and consequences\n"
        )
        
        tone_mods = {
            "humorous": "- Add wit and unexpected twists\n- NPCs are quirky and memorable",
            "serious": "- Maintain gravitas\n- Consequences are weighty",
            "gritty": "- Violence has impact\n- Failure hurts"
        }
        
        return base + "\n" + tone_mods.get(tone, "")
    
    async def narrate_outcome(
        self,
        player_input: str,
        intent_id: str,
        arbiter_result: dict,
        context: str
    ) -> ChroniclerProse:
        """
        Generate narrative prose from Arbiter results.
        
        Args:
            player_input: Original player text
            intent_id: Resolved intent
            arbiter_result: Dictionary with success, hp_delta, npc_state, etc.
            context: Room description and NPC states
        
        Returns:
            ChroniclerProse with vivid D&D narration
        """
        prompt = (
            f"Context: {context}\n\n"
            f"Player Action: \"{player_input}\"\n"
            f"Intent: {intent_id}\n\n"
            f"Arbiter Result:\n"
            f"- Success: {arbiter_result.get('success')}\n"
            f"- HP Change: {arbiter_result.get('hp_delta', 0)}\n"
            f"- Gold Change: {arbiter_result.get('gold_delta', 0)}\n"
            f"- NPC State: {arbiter_result.get('new_npc_state')}\n"
            f"- Reasoning: {arbiter_result.get('reasoning')}\n\n"
            f"Write the narrative:"
        )
        
        logger.debug(f"Chronicler narrating: {intent_id}")
        
        try:
            result = await self.agent.run(prompt)
            prose = result.data
            
            logger.info(f"Chronicler generated: {prose.narrative[:50]}...")
            return prose
            
        except Exception as e:
            logger.error(f"Chronicler failed: {e}")
            
            # Fallback narrative
            return self._fallback_prose(player_input, arbiter_result)
    
    def _fallback_prose(self, player_input: str, arbiter_result: dict) -> ChroniclerProse:
        """Fallback narrative if LLM fails."""
        logger.warning("Using fallback chronicler prose")
        
        success = arbiter_result.get('success', False)
        
        if success:
            narrative = f"You attempt {player_input}. {arbiter_result.get('reasoning', 'The action succeeds')}."
        else:
            narrative = f"You attempt {player_input}, but the action fails."
        
        return ChroniclerProse(narrative=narrative)
