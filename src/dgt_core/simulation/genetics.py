"""
DGT Advanced Genetics Engine
Strategic Transplant from TurboShells - Pydantic V2 Refactored

17 genetic traits with Mendelian inheritance, mutation, and terrain adaptation
Integrated with DGT's Universal Packet system for distributed architecture
"""

import random
import math
import hashlib
from typing import Dict, List, Optional, Tuple, Union, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
import json

from loguru import logger


class TraitType(str, Enum):
    """Genetic trait types for validation and processing"""
    CONTINUOUS = "continuous"
    DISCRETE = "discrete"
    RGB = "rgb"
    POLYGENIC = "polygenic"


class TerrainType(str, Enum):
    """Terrain types that affect turtle performance"""
    NORMAL = "normal"
    GRASS = "grass"
    WATER = "water"
    SAND = "sand"
    MUD = "mud"
    ROCKS = "rocks"
    BOOST = "boost"


class Gene(BaseModel):
    """Individual gene with inheritance and mutation properties"""
    name: str
    value: Union[float, str, Tuple[int, int, int]]
    trait_type: TraitType
    dominance: float = Field(default=0.5, ge=0.0, le=1.0, description="Dominance factor (0=recessive, 1=dominant)")
    mutation_rate: float = Field(default=0.05, ge=0.0, le=1.0, description="Mutation probability")
    
    class Config:
        validate_assignment = True


class GeneticTrait(BaseModel):
    """Base model for genetic traits with validation"""
    name: str
    trait_type: TraitType
    value_range: Union[Tuple[float, float], List[str]]
    default_value: Union[float, str, Tuple[int, int, int]]
    terrain_modifiers: Dict[TerrainType, float] = Field(default_factory=dict)
    
    def validate_value(self, value: Union[float, str, Tuple[int, int, int]]) -> bool:
        """Validate if value is within acceptable range"""
        if self.trait_type == TraitType.CONTINUOUS:
            return isinstance(value, (int, float)) and self.value_range[0] <= value <= self.value_range[1]
        elif self.trait_type == TraitType.DISCRETE:
            return value in self.value_range
        elif self.trait_type == TraitType.RGB:
            return (isinstance(value, tuple) and len(value) == 3 and 
                   all(isinstance(v, int) and 0 <= v <= 255 for v in value))
        return False
    
    def get_terrain_modifier(self, terrain: TerrainType) -> float:
        """Get performance modifier for specific terrain"""
        return self.terrain_modifiers.get(terrain, 1.0)


class TurboGenome(BaseModel):
    """
    Advanced turtle genome with 17 TurboShells traits
    Refactored for Pydantic V2 with proper validation
    """
    
    # === Shell Genetics (4 traits) ===
    shell_base_color: Tuple[int, int, int] = Field(default=(34, 139, 34), description="Primary shell RGB color")
    shell_pattern_type: str = Field(default="hex", description="Shell pattern type")
    shell_pattern_color: Tuple[int, int, int] = Field(default=(255, 255, 255), description="Pattern RGB color")
    shell_pattern_density: float = Field(default=0.5, ge=0.1, le=1.0, description="Pattern density")
    
    # === Body Genetics (4 traits) ===
    body_base_color: Tuple[int, int, int] = Field(default=(107, 142, 35), description="Body RGB color")
    body_pattern_type: str = Field(default="solid", description="Body pattern type")
    body_pattern_color: Tuple[int, int, int] = Field(default=(85, 107, 47), description="Body pattern RGB color")
    body_pattern_density: float = Field(default=0.3, ge=0.1, le=1.0, description="Body pattern density")
    
    # === Performance Genetics (5 traits) ===
    speed: float = Field(default=1.0, ge=0.1, le=3.0, description="Base speed multiplier")
    stamina: float = Field(default=1.0, ge=0.1, le=3.0, description="Stamina/endurance factor")
    climb: float = Field(default=1.0, ge=0.1, le=3.0, description="Climbing ability")
    swim: float = Field(default=1.0, ge=0.1, le=3.0, description="Swimming ability")
    intelligence: float = Field(default=1.0, ge=0.1, le=3.0, description="Intelligence/strategy factor")
    
    # === Physical Genetics (4 traits) ===
    head_size_modifier: float = Field(default=1.0, ge=0.7, le=1.3, description="Head size scaling")
    leg_length: float = Field(default=1.0, ge=0.5, le=1.5, description="Leg length scaling")
    shell_size_modifier: float = Field(default=1.0, ge=0.5, le=1.5, description="Shell size scaling")
    leg_thickness_modifier: float = Field(default=1.0, ge=0.7, le=1.3, description="Leg thickness")
    
    # === Meta Properties ===
    generation: int = Field(default=0, ge=0, description="Generation number")
    mutation_rate: float = Field(default=0.1, ge=0.0, le=1.0, description="Overall mutation rate")
    genetic_signature: Optional[str] = Field(default=None, description="Unique genetic hash")
    
    class Config:
        validate_assignment = True
        use_enum_values = True
    
    @validator('shell_pattern_type')
    def validate_shell_pattern(cls, v):
        allowed = ['hex', 'spots', 'stripes', 'rings']
        if v not in allowed:
            raise ValueError(f"Shell pattern must be one of: {allowed}")
        return v
    
    @validator('body_pattern_type')
    def validate_body_pattern(cls, v):
        allowed = ['solid', 'mottled', 'speckled', 'marbled']
        if v not in allowed:
            raise ValueError(f"Body pattern must be one of: {allowed}")
        return v
    
    def __post_init__(self):
        """Generate genetic signature after creation"""
        if not self.genetic_signature:
            self.genetic_signature = self._calculate_signature()
    
    def _calculate_signature(self) -> str:
        """Calculate unique genetic signature"""
        # Create deterministic representation
        genome_dict = self.dict(exclude={'genetic_signature'})
        sorted_data = json.dumps(genome_dict, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()[:16]
    
    def get_dominant_shell_color(self) -> Tuple[int, int, int]:
        """Get effective shell color (simplified for DGT)"""
        return self.shell_base_color
    
    def get_dominant_body_color(self) -> Tuple[int, int, int]:
        """Get effective body color"""
        return self.body_base_color
    
    def calculate_speed_on_terrain(self, terrain: TerrainType) -> float:
        """Calculate effective speed based on terrain"""
        base_speed = self.speed
        
        # Terrain modifiers from TurboShells
        terrain_multipliers = {
            TerrainType.NORMAL: 1.0,
            TerrainType.GRASS: 1.1,
            TerrainType.WATER: self.swim * 1.2,
            TerrainType.SAND: 0.7,
            TerrainType.MUD: 0.4,
            TerrainType.ROCKS: self.climb * 0.6,
            TerrainType.BOOST: 1.5
        }
        
        modifier = terrain_multipliers.get(terrain, 1.0)
        return base_speed * modifier
    
    def calculate_fitness(self) -> float:
        """Calculate overall fitness score"""
        # Weighted fitness formula (TurboShells inspired)
        speed_weight = 0.3
        stamina_weight = 0.25
        intelligence_weight = 0.2
        physical_weight = 0.15
        diversity_weight = 0.1
        
        # Physical traits average
        physical_score = (
            self.head_size_modifier + self.leg_length + 
            self.shell_size_modifier + self.leg_thickness_modifier
        ) / 4
        
        # Color diversity bonus
        color_diversity = self._calculate_color_diversity()
        
        fitness = (
            self.speed * speed_weight +
            self.stamina * stamina_weight +
            self.intelligence * intelligence_weight +
            physical_score * physical_weight +
            color_diversity * diversity_weight
        )
        
        return max(0.1, min(3.0, fitness))  # Clamp to valid range
    
    def _calculate_color_diversity(self) -> float:
        """Calculate color diversity score"""
        shell_color = self.shell_base_color
        body_color = self.body_base_color
        pattern_color = self.shell_pattern_color
        
        # Simple diversity metric based on color variance
        shell_variance = sum((c - 128) ** 2 for c in shell_color) / (255 ** 2 * 3)
        body_variance = sum((c - 128) ** 2 for c in body_color) / (255 ** 2 * 3)
        pattern_variance = sum((c - 128) ** 2 for c in pattern_color) / (255 ** 2 * 3)
        
        return (shell_variance + body_variance + pattern_variance) / 3
    
    def crossover(self, partner: 'TurboGenome', inheritance_mode: str = "mendelian") -> 'TurboGenome':
        """
        Perform genetic crossover with partner
        Salvaged and refined from TurboShells inheritance logic
        """
        if inheritance_mode == "mendelian":
            return self._mendelian_crossover(partner)
        elif inheritance_mode == "blended":
            return self._blended_crossover(partner)
        elif inheritance_mode == "dominant":
            return self._dominant_crossover(partner)
        else:
            return self._mendelian_crossover(partner)
    
    def _mendelian_crossover(self, partner: 'TurboGenome') -> 'TurboGenome':
        """Standard Mendelian inheritance (50/50 chance)"""
        offspring_data = {}
        
        # Get all field names except meta properties
        genetic_fields = [f for f in self.__fields__ if f not in ['generation', 'mutation_rate', 'genetic_signature']]
        
        for field in genetic_fields:
            # 50/50 inheritance
            if random.random() < 0.5:
                offspring_data[field] = getattr(self, field)
            else:
                offspring_data[field] = getattr(partner, field)
        
        # Meta properties
        offspring_data['generation'] = max(self.generation, partner.generation) + 1
        offspring_data['mutation_rate'] = (self.mutation_rate + partner.mutation_rate) / 2
        
        return TurboGenome(**offspring_data)
    
    def _blended_crossover(self, partner: 'TurboGenome') -> 'TurboGenome':
        """Blended inheritance for continuous values"""
        offspring_data = {}
        
        genetic_fields = [f for f in self.__fields__ if f not in ['generation', 'mutation_rate', 'genetic_signature']]
        
        for field in genetic_fields:
            self_value = getattr(self, field)
            partner_value = getattr(partner, field)
            
            # Blend continuous and RGB values
            if isinstance(self_value, (int, float)) and isinstance(partner_value, (int, float)):
                offspring_data[field] = (self_value + partner_value) / 2
            elif isinstance(self_value, tuple) and isinstance(partner_value, tuple) and len(self_value) == 3:
                offspring_data[field] = tuple(
                    int((self_value[i] + partner_value[i]) / 2) for i in range(3)
                )
            else:
                # Random for discrete values
                offspring_data[field] = self_value if random.random() < 0.5 else partner_value
        
        offspring_data['generation'] = max(self.generation, partner.generation) + 1
        offspring_data['mutation_rate'] = (self.mutation_rate + partner.mutation_rate) / 2
        
        return TurboGenome(**offspring_data)
    
    def _dominant_crossover(self, partner: 'TurboGenome') -> 'TurboGenome':
        """Dominance-based inheritance"""
        offspring_data = {}
        
        genetic_fields = [f for f in self.__fields__ if f not in ['generation', 'mutation_rate', 'genetic_signature']]
        
        for field in genetic_fields:
            # Higher fitness parent has dominance
            if self.calculate_fitness() > partner.calculate_fitness():
                offspring_data[field] = getattr(self, field)
            else:
                offspring_data[field] = getattr(partner, field)
        
        offspring_data['generation'] = max(self.generation, partner.generation) + 1
        offspring_data['mutation_rate'] = (self.mutation_rate + partner.mutation_rate) / 2
        
        return TurboGenome(**offspring_data)
    
    def mutate(self, mutation_intensity: str = "moderate") -> 'TurboGenome':
        """
        Apply mutations based on TurboShells mutation patterns
        Enhanced with targeted and adaptive mutations
        """
        intensity_rates = {
            "low": 0.05,
            "moderate": 0.1,
            "high": 0.2,
            "extreme": 0.3
        }
        
        mutation_rate = intensity_rates.get(mutation_intensity, self.mutation_rate)
        mutated_data = self.dict(exclude={'genetic_signature'})
        
        genetic_fields = [f for f in self.__fields__ if f not in ['generation', 'mutation_rate', 'genetic_signature']]
        
        for field in genetic_fields:
            if random.random() < mutation_rate:
                current_value = getattr(self, field)
                mutated_data[field] = self._mutate_gene(field, current_value)
        
        # Increment generation
        mutated_data['generation'] = self.generation + 1
        
        return TurboGenome(**mutated_data)
    
    def _mutate_gene(self, gene_name: str, current_value: Union[float, str, Tuple[int, int, int]]) -> Union[float, str, Tuple[int, int, int]]:
        """Mutate individual gene based on TurboShells patterns"""
        if gene_name in ['speed', 'stamina', 'climb', 'swim', 'intelligence']:
            # Performance traits: gaussian mutation
            mutation = random.gauss(0, 0.1)
            new_value = current_value + mutation
            return max(0.1, min(3.0, new_value))
        
        elif gene_name in ['head_size_modifier', 'leg_length', 'shell_size_modifier', 'leg_thickness_modifier']:
            # Size traits: small gaussian mutation
            mutation = random.gauss(0, 0.05)
            new_value = current_value + mutation
            return max(0.5, min(1.5, new_value))
        
        elif gene_name in ['shell_pattern_density', 'body_pattern_density']:
            # Density traits: small mutation
            mutation = random.gauss(0, 0.05)
            new_value = current_value + mutation
            return max(0.1, min(1.0, new_value))
        
        elif gene_name.endswith('_color') and isinstance(current_value, tuple):
            # RGB colors: shift by small amount
            mutated = list(current_value)
            for i in range(3):
                shift = random.randint(-20, 20)
                mutated[i] = max(0, min(255, current_value[i] + shift))
            return tuple(mutated)
        
        elif gene_name.endswith('_pattern_type'):
            # Pattern types: random selection
            if gene_name == 'shell_pattern_type':
                patterns = ['hex', 'spots', 'stripes', 'rings']
            else:  # body_pattern_type
                patterns = ['solid', 'mottled', 'speckled', 'marbled']
            
            available = [p for p in patterns if p != current_value]
            return random.choice(available) if available else current_value
        
        else:
            return current_value
    
    def to_universal_packet(self) -> Dict[str, Any]:
        """Convert to DGT Universal Packet format"""
        return {
            'genetic_signature': self.genetic_signature,
            'generation': self.generation,
            'shell_pattern': self.shell_pattern_type,
            'primary_color': f"#{self.shell_base_color[0]:02x}{self.shell_base_color[1]:02x}{self.shell_base_color[2]:02x}",
            'secondary_color': f"#{self.body_base_color[0]:02x}{self.body_base_color[1]:02x}{self.body_base_color[2]:02x}",
            'speed': self.speed,
            'stamina': self.stamina,
            'intelligence': self.intelligence,
            'fitness_score': self.calculate_fitness(),
            'terrain_adaptations': {
                'water': self.swim,
                'climb': self.climb,
                'physical': (self.head_size_modifier + self.leg_length + self.shell_size_modifier) / 3
            }
        }


class GeneticRegistry:
    """Registry for genetic trait definitions and validation"""
    
    def __init__(self):
        self.trait_definitions = self._initialize_traits()
    
    def _initialize_traits(self) -> Dict[str, GeneticTrait]:
        """Initialize all 17 genetic traits with TurboShells definitions"""
        return {
            # Shell traits
            'shell_base_color': GeneticTrait(
                name='shell_base_color',
                trait_type=TraitType.RGB,
                value_range=(0, 255),
                default_value=(34, 139, 34),
                terrain_modifiers={TerrainType.GRASS: 1.1, TerrainType.WATER: 0.9}
            ),
            'shell_pattern_type': GeneticTrait(
                name='shell_pattern_type',
                trait_type=TraitType.DISCRETE,
                value_range=['hex', 'spots', 'stripes', 'rings'],
                default_value='hex'
            ),
            'shell_pattern_color': GeneticTrait(
                name='shell_pattern_color',
                trait_type=TraitType.RGB,
                value_range=(0, 255),
                default_value=(255, 255, 255)
            ),
            'shell_pattern_density': GeneticTrait(
                name='shell_pattern_density',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.1, 1.0),
                default_value=0.5
            ),
            
            # Body traits
            'body_base_color': GeneticTrait(
                name='body_base_color',
                trait_type=TraitType.RGB,
                value_range=(0, 255),
                default_value=(107, 142, 35)
            ),
            'body_pattern_type': GeneticTrait(
                name='body_pattern_type',
                trait_type=TraitType.DISCRETE,
                value_range=['solid', 'mottled', 'speckled', 'marbled'],
                default_value='solid'
            ),
            'body_pattern_color': GeneticTrait(
                name='body_pattern_color',
                trait_type=TraitType.RGB,
                value_range=(0, 255),
                default_value=(85, 107, 47)
            ),
            'body_pattern_density': GeneticTrait(
                name='body_pattern_density',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.1, 1.0),
                default_value=0.3
            ),
            
            # Performance traits
            'speed': GeneticTrait(
                name='speed',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.1, 3.0),
                default_value=1.0,
                terrain_modifiers={
                    TerrainType.GRASS: 1.1,
                    TerrainType.SAND: 0.7,
                    TerrainType.BOOST: 1.5
                }
            ),
            'stamina': GeneticTrait(
                name='stamina',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.1, 3.0),
                default_value=1.0,
                terrain_modifiers={TerrainType.MUD: 0.5, TerrainType.WATER: 1.2}
            ),
            'climb': GeneticTrait(
                name='climb',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.1, 3.0),
                default_value=1.0,
                terrain_modifiers={TerrainType.ROCKS: 2.0, TerrainType.NORMAL: 1.0}
            ),
            'swim': GeneticTrait(
                name='swim',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.1, 3.0),
                default_value=1.0,
                terrain_modifiers={TerrainType.WATER: 2.0, TerrainType.SAND: 0.5}
            ),
            'intelligence': GeneticTrait(
                name='intelligence',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.1, 3.0),
                default_value=1.0,
                terrain_modifiers={TerrainType.BOOST: 1.3}
            ),
            
            # Physical traits
            'head_size_modifier': GeneticTrait(
                name='head_size_modifier',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.7, 1.3),
                default_value=1.0
            ),
            'leg_length': GeneticTrait(
                name='leg_length',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.5, 1.5),
                default_value=1.0
            ),
            'shell_size_modifier': GeneticTrait(
                name='shell_size_modifier',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.5, 1.5),
                default_value=1.0
            ),
            'leg_thickness_modifier': GeneticTrait(
                name='leg_thickness_modifier',
                trait_type=TraitType.CONTINUOUS,
                value_range=(0.7, 1.3),
                default_value=1.0
            )
        }
    
    def get_trait(self, trait_name: str) -> Optional[GeneticTrait]:
        """Get trait definition by name"""
        return self.trait_definitions.get(trait_name)
    
    def validate_genome(self, genome: TurboGenome) -> bool:
        """Validate genome against trait definitions"""
        for trait_name, trait_def in self.trait_definitions.items():
            value = getattr(genome, trait_name)
            if not trait_def.validate_value(value):
                logger.warning(f"Invalid value for {trait_name}: {value}")
                return False
        return True


# Global registry instance
genetic_registry = GeneticRegistry()
