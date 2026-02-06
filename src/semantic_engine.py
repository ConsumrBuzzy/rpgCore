"""
Semantic Intent Resolution Engine

Uses sentence embeddings to map natural language player input to structured intents.
Designed for laptop-friendly performance (<50ms on CPU).
"""

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer, util


@dataclass
class IntentMatch:
    """Result of intent resolution with confidence scoring."""
    
    intent_id: str
    description: str
    confidence: float


class IntentLibrary:
    """
    Extensible repository of game intents.
    
    Each intent has:
    - intent_id: Unique identifier (e.g., 'distract', 'attack')
    - description: Natural language description used for semantic matching
    """
    
    def __init__(self):
        self._intents: Dict[str, str] = {}
        self._embeddings: Optional[np.ndarray] = None
        self._embeddings_stale = True
    
    def add_intent(self, intent_id: str, description: str) -> None:
        """Add or update an intent definition."""
        self._intents[intent_id] = description
        self._embeddings_stale = True
        logger.debug(f"Added intent: {intent_id}")
    
    def get_intents(self) -> Dict[str, str]:
        """Return all registered intents."""
        return self._intents.copy()
    
    def mark_embeddings_computed(self, embeddings: np.ndarray) -> None:
        """Cache precomputed embeddings (called by SemanticResolver)."""
        self._embeddings = embeddings
        self._embeddings_stale = False


class SemanticResolver:
    """
    Maps player input to intents using cosine similarity.
    
    Performance:
    - Model load: ~200ms (one-time)
    - Inference: <50ms per query on CPU
    """
    
    def __init__(
        self,
        intent_library: IntentLibrary,
        model_name: str = 'all-MiniLM-L6-v2',
        confidence_threshold: float = 0.5
    ):
        """
        Initialize semantic resolver.
        
        Args:
            intent_library: Library of intents to match against
            model_name: SentenceTransformer model (default: MiniLM, 80MB)
            confidence_threshold: Minimum similarity score (0-1) to accept match
        """
        self.intent_library = intent_library
        self.confidence_threshold = confidence_threshold
        
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Pre-compute intent embeddings
        self._update_intent_embeddings()
    
    def _update_intent_embeddings(self) -> None:
        """Compute and cache embeddings for all intents."""
        intents = self.intent_library.get_intents()
        
        if not intents:
            logger.warning("Intent library is empty!")
            return
        
        descriptions = list(intents.values())
        embeddings = self.model.encode(descriptions, convert_to_numpy=True)
        
        self.intent_library.mark_embeddings_computed(embeddings)
        logger.info(f"Precomputed embeddings for {len(intents)} intents")
    
    def resolve_intent(self, player_input: str) -> Optional[IntentMatch]:
        """
        Find the best matching intent for player input.
        
        Args:
            player_input: Natural language action (e.g., "I kick the table")
        
        Returns:
            IntentMatch if confidence exceeds threshold, None otherwise
        """
        if not player_input.strip():
            logger.warning("Empty input received")
            return None
        
        intents = self.intent_library.get_intents()
        
        if not intents:
            logger.error("Cannot resolve intent: library is empty")
            return None
        
        # Get cached embeddings (or recompute if stale)
        if self.intent_library._embeddings_stale:
            self._update_intent_embeddings()
        
        # Encode player input
        input_embedding = self.model.encode(player_input, convert_to_numpy=True)
        
        # Compute cosine similarity
        scores = util.cos_sim(input_embedding, self.intent_library._embeddings)[0]
        
        # Find best match
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        
        intent_ids = list(intents.keys())
        best_intent_id = intent_ids[best_idx]
        
        logger.info(
            f"Intent resolution: '{player_input}' → {best_intent_id} "
            f"(confidence: {best_score:.3f})"
        )
        
        # Reject low-confidence matches
        if best_score < self.confidence_threshold:
            logger.warning(
                f"Confidence {best_score:.3f} below threshold "
                f"{self.confidence_threshold}"
            )
            return None
        
        return IntentMatch(
            intent_id=best_intent_id,
            description=intents[best_intent_id],
            confidence=best_score
        )
    
    def add_intent(self, intent_id: str, description: str) -> None:
        """Convenience method to add intent and invalidate cache."""
        self.intent_library.add_intent(intent_id, description)


def create_default_intent_library() -> IntentLibrary:
    """
    Create a library with common RPG intents.
    
    These descriptions are optimized for semantic matching, not player display.
    """
    library = IntentLibrary()
    
    # Stealth & Avoidance
    library.add_intent(
        "sneak",
        "Move quietly without being noticed, hide, or avoid detection"
    )
    library.add_intent(
        "distract",
        "Create a diversion, redirect attention, or cause a distraction"
    )
    
    # Force & Combat
    library.add_intent(
        "attack",
        "Use a weapon or physical force to harm a target"
    )
    library.add_intent(
        "defend",
        "Block, parry, dodge, or protect yourself from harm"
    )
    library.add_intent(
        "improvised_attack",
        "Use an unconventional object or environment to cause damage"
    )
    
    # Social & Persuasion
    library.add_intent(
        "persuade",
        "Convince, negotiate, charm, or talk your way through a situation"
    )
    library.add_intent(
        "intimidate",
        "Threaten, coerce, or frighten someone into compliance"
    )
    library.add_intent(
        "deceive",
        "Lie, bluff, trick, or mislead someone"
    )
    
    # Utility
    library.add_intent(
        "investigate",
        "Examine, search, inspect, or study something closely"
    )
    library.add_intent(
        "use_item",
        "Utilize equipment, tools, or objects from your inventory"
    )
    
    return library
