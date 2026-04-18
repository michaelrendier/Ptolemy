from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime
from enum import Enum

class Sentiment(Enum):
    NEUTRAL = 0
    POSITIVE = 1
    NEGATIVE = 2
    AMBIGUOUS = 3

@dataclass
class Etymology:
    root_language: str
    original_meaning: str
    evolution_timeline: List[str] = field(default_factory=list)

@dataclass
class SensoryProfile:
    """Associations with physical senses (e.g., 'velvet' has a tactile profile)."""
    visual_associations: List[str] = field(default_factory=list)
    auditory_resonance: Optional[str] = None # Phonetic 'weight'
    tactile_texture: Optional[str] = None
    scent_memory: List[str] = field(default_factory=list)

@dataclass
class SemanticLayer:
    denotation: str  # Literal dictionary definition
    connotations: List[str] = field(default_factory=list) # Cultural 'feel'
    synonyms: Set[str] = field(default_factory=set)
    antonyms: Set[str] = field(default_factory=set)
    idiomatic_uses: List[str] = field(default_factory=list)

@dataclass
class PersonalResonance:
    """The 'Ptolemy' specific layer: How the word exists in YOUR world."""
    usage_frequency: int = 0
    first_encountered: Optional[datetime] = None
    linked_memories: List[str] = field(default_factory=list) # References to 'fragments'
    subjective_sentiment: Sentiment = Sentiment.NEUTRAL
    associated_people: List[str] = field(default_factory=list)

@dataclass
class SemanticWord:
    token: str
    linguistic_category: str  # Noun, Verb, etc.
    
    # The 'Database' behind the word
    semantics: SemanticLayer
    etymology: Etymology
    sensory: SensoryProfile
    resonance: PersonalResonance
    
    # Vector space representation for Phaleron's indexing
    embedding_coordinates: List[float] = field(default_factory=list)
    
    # Cross-references to other Word objects (Phaleron's web)
    related_tokens: Dict[str, str] = field(default_factory=dict) # word: relationship_type

    def __post_init__(self):
        self.token = self.token.strip().lower()

# Example of how Phaleron might initialize a word:
# word_entry = SemanticWord(
#     token="Horizon",
#     linguistic_category="Noun",
#     semantics=SemanticLayer(denotation="The line at which the earth's surface and the sky appear to meet."),
#     ...
# )
