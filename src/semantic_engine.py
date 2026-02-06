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
    Extensible repository of game intents with exemplar-based matching.
    
    Each intent has:
    - intent_id: Unique identifier (e.g., 'distract', 'force')
    - exemplars: List of concrete action examples for semantic matching
    
    Design: Multiple exemplars increase semantic hit-rate for small models
    by providing diverse action patterns within the same intent category.
    """
    
    def __init__(self):
        self._intents: Dict[str, list[str]] = {}
        self._embeddings: Optional[Dict[str, np.ndarray]] = None
        self._embeddings_stale = True
    
    def add_intent(self, intent_id: str, exemplars: list[str]) -> None:
        """
        Add or update an intent with action exemplars.
        
        Args:
            intent_id: Unique intent identifier
            exemplars: 3-5 concrete action examples (e.g., "Throw a beer", "Kick a table")
        """
        if not exemplars:
            raise ValueError(f"Intent '{intent_id}' must have at least one exemplar")
        
        self._intents[intent_id] = exemplars
        self._embeddings_stale = True
        logger.debug(f"Added intent: {intent_id} with {len(exemplars)} exemplars")
    
    def get_intents(self) -> Dict[str, list[str]]:
        """Return all registered intents with their exemplars."""
        return self._intents.copy()
    
    def mark_embeddings_computed(self, embeddings: Dict[str, np.ndarray]) -> None:
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
        """
        Compute and cache embeddings for all intent exemplars.
        
        For each intent, we compute embeddings for ALL exemplars, allowing
        max-similarity matching during resolution.
        """
        intents = self.intent_library.get_intents()
        
        if not intents:
            logger.warning("Intent library is empty!")
            return
        
        # Compute embeddings per-intent (each intent has multiple exemplars)
        embeddings_dict = {}
        total_exemplars = 0
        
        for intent_id, exemplars in intents.items():
            # Encode all exemplars for this intent
            exemplar_embeddings = self.model.encode(exemplars, convert_to_numpy=True)
            embeddings_dict[intent_id] = exemplar_embeddings
            total_exemplars += len(exemplars)
        
        self.intent_library.mark_embeddings_computed(embeddings_dict)
        logger.info(
            f"Precomputed embeddings for {len(intents)} intents "
            f"({total_exemplars} total exemplars)"
        )
    
    def resolve_intent(self, player_input: str) -> Optional[IntentMatch]:
        """
        Find the best matching intent using max-similarity across exemplars.
        
        Algorithm:
        1. Encode player input
        2. For each intent, compute similarity against ALL exemplars
        3. Take the MAX similarity score for that intent
        4. Select the intent with the highest max score
        5. Fallback to 'improvise' if confidence is too low
        
        Args:
            player_input: Natural language action (e.g., "I kick the table")
        
        Returns:
            IntentMatch if confidence exceeds threshold, otherwise None
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
        
        # Encode player input once
        input_embedding = self.model.encode(player_input, convert_to_numpy=True)
        
        # Find best intent via max-similarity matching
        best_intent_id = None
        best_score = 0.0
        best_exemplar = ""
        
        for intent_id, exemplar_embeddings in self.intent_library._embeddings.items():
            # Compute similarity against all exemplars for this intent
            scores = util.cos_sim(input_embedding, exemplar_embeddings)[0]
            
            # Take the MAX score (closest exemplar match)
            max_score = float(np.max(scores))
            max_idx = int(np.argmax(scores))
            
            # Track the best intent across all intents
            if max_score > best_score:
                best_score = max_score
                best_intent_id = intent_id
                best_exemplar = intents[intent_id][max_idx]
        
        if best_intent_id is None:
            logger.error("No intent matched (should not happen)")
            return None
        
        logger.info(
            f"Intent resolution: '{player_input}' → {best_intent_id} "
            f"(confidence: {best_score:.3f}, matched exemplar: '{best_exemplar}')"
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
            description=best_exemplar,  # Return the matched exemplar
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
