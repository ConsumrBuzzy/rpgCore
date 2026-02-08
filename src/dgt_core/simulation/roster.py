"""
DGT Roster Manager - ADR 127 Implementation
Persistent database service for genetic turtle management

Manages "Active Roster" vs "Genetic Archive" to prevent memory bloat
Supports 400+ turtles with SQLite/JSON-Lines persistence
"""

import sqlite3
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

from loguru import logger
from .genetics import TurboGenome, genetic_registry


@dataclass
class TurtleStats:
    """8 core stats from TurboShells legacy system"""
    speed: float = 1.0
    max_energy: float = 100.0
    recovery: float = 1.0
    swim: float = 1.0
    climb: float = 1.0
    stamina: float = 1.0
    luck: float = 1.0
    intelligence: float = 1.0
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'TurtleStats':
        return cls(**data)
    
    def calculate_power_score(self) -> float:
        """Calculate overall power score for tournament seeding"""
        weights = {
            'speed': 0.25,
            'max_energy': 0.15,
            'recovery': 0.10,
            'swim': 0.10,
            'climb': 0.10,
            'stamina': 0.15,
            'luck': 0.05,
            'intelligence': 0.10
        }
        
        score = 0.0
        for stat, value in self.to_dict().items():
            score += value * weights.get(stat, 0.1)
        
        return score


@dataclass
class TurtleRecord:
    """Persistent turtle record for database storage"""
    name: str
    generation: int
    stats: TurtleStats
    genome: TurboGenome
    turtle_id: str = ""
    created_at: float = 0.0
    last_active: float = 0.0
    race_history: List[Dict[str, Any]] = None
    total_races: int = 0
    wins: int = 0
    earnings: float = 0.0
    is_active: bool = True
    is_retired: bool = False
    
    def __post_init__(self):
        if not self.turtle_id:
            self.turtle_id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = time.time()
        if not self.last_active:
            self.last_active = time.time()
        if not self.race_history:
            self.race_history = []
    
    def to_db_dict(self) -> Dict[str, Any]:
        """Convert to database-compatible dictionary"""
        return {
            'turtle_id': self.turtle_id,
            'name': self.name,
            'generation': self.generation,
            'created_at': self.created_at,
            'last_active': self.last_active,
            'stats': json.dumps(self.stats.to_dict()),
            'genome': json.dumps(self.genome.dict()),
            'race_history': json.dumps(self.race_history),
            'total_races': self.total_races,
            'wins': self.wins,
            'earnings': self.earnings,
            'is_active': self.is_active,
            'is_retired': self.is_retired
        }
    
    @classmethod
    def from_db_dict(cls, data: Dict[str, Any]) -> 'TurtleRecord':
        """Create from database dictionary"""
        return cls(
            turtle_id=data['turtle_id'],
            name=data['name'],
            generation=data['generation'],
            created_at=data['created_at'],
            last_active=data['last_active'],
            stats=TurtleStats.from_dict(json.loads(data['stats'])),
            genome=TurboGenome(**json.loads(data['genome'])),
            race_history=json.loads(data['race_history']),
            total_races=data['total_races'],
            wins=data['wins'],
            earnings=data['earnings'],
            is_active=data['is_active'],
            is_retired=data['is_retired']
        )


class RosterManager:
    """Persistent roster management service"""
    
    def __init__(self, storage_path: Optional[Path] = None, use_sqlite: bool = True):
        self.storage_path = storage_path or Path(__file__).parent.parent.parent.parent / "data" / "roster.db"
        self.use_sqlite = use_sqlite
        
        # In-memory caches for active turtles
        self.active_roster: Dict[str, TurtleRecord] = {}
        self.max_active_roster = 20  # Only keep top 20 in memory
        
        if use_sqlite:
            self._init_sqlite()
        else:
            self._init_json_lines()
        
        self._load_active_roster()
        
        logger.info(f"📋 Roster Manager initialized: {len(self.active_roster)} active turtles")
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        self.db_path = self.storage_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS turtles (
                    turtle_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    last_active REAL NOT NULL,
                    stats TEXT NOT NULL,
                    genome TEXT NOT NULL,
                    race_history TEXT NOT NULL,
                    total_races INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    earnings REAL DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT 1,
                    is_retired BOOLEAN DEFAULT 0
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_active ON turtles(is_active)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_generation ON turtles(generation)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_wins ON turtles(wins)')
            
        logger.debug(f"📋 SQLite database initialized: {self.db_path}")
    
    def _init_json_lines(self):
        """Initialize JSON-Lines storage"""
        self.json_path = self.storage_path.with_suffix('.jsonl')
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file if it doesn't exist
        if not self.json_path.exists():
            self.json_path.touch()
        
        logger.debug(f"📋 JSON-Lines storage initialized: {self.json_path}")
    
    def _load_active_roster(self):
        """Load active roster into memory"""
        if self.use_sqlite:
            self._load_sqlite_active()
        else:
            self._load_json_active()
    
    def _load_sqlite_active(self):
        """Load active turtles from SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM turtles 
                WHERE is_active = 1 AND is_retired = 0
                ORDER BY wins DESC, earnings DESC
                LIMIT ?
            ''', (self.max_active_roster,))
            
            for row in cursor.fetchall():
                columns = [desc[0] for desc in cursor.description]
                data = dict(zip(columns, row))
                turtle = TurtleRecord.from_db_dict(data)
                self.active_roster[turtle.turtle_id] = turtle
        
        logger.debug(f"📋 Loaded {len(self.active_roster)} active turtles from SQLite")
    
    def _load_json_active(self):
        """Load active turtles from JSON-Lines"""
        try:
            with open(self.json_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data.get('is_active') and not data.get('is_retired'):
                            turtle = TurtleRecord.from_db_dict(data)
                            self.active_roster[turtle.turtle_id] = turtle
                            
                            if len(self.active_roster) >= self.max_active_roster:
                                break
        
        except FileNotFoundError:
            logger.debug("📋 JSON-Lines file not found, starting fresh")
        
        logger.debug(f"📋 Loaded {len(self.active_roster)} active turtles from JSON-Lines")
    
    def create_turtle(self, name: str, genome: Optional[TurboGenome] = None, 
                     stats: Optional[TurtleStats] = None) -> str:
        """Create a new turtle and add to roster"""
        # Generate genome if not provided
        if genome is None:
            genome = TurboGenome(
                generation=0,
                mutation_rate=0.1
            )
        
        # Generate stats from genome if not provided
        if stats is None:
            stats = self._stats_from_genome(genome)
        
        # Create turtle record
        turtle = TurtleRecord(
            name=name,
            generation=genome.generation,
            stats=stats,
            genome=genome
        )
        
        # Save to persistent storage
        self._save_turtle(turtle)
        
        # Add to active roster if space available
        if len(self.active_roster) < self.max_active_roster:
            self.active_roster[turtle.turtle_id] = turtle
        
        logger.info(f"📋 Created turtle: {name} ({turtle.turtle_id})")
        return turtle.turtle_id
    
    def _stats_from_genome(self, genome: TurboGenome) -> TurtleStats:
        """Generate 8 core stats from 17 genetic traits"""
        # Map genetic traits to core stats
        base_stats = TurtleStats()
        
        # Speed directly from genome
        base_stats.speed = genome.speed
        
        # Energy from physical traits
        physical_avg = (
            genome.head_size_modifier + genome.leg_length + 
            genome.shell_size_modifier + genome.leg_thickness_modifier
        ) / 4
        base_stats.max_energy = 80 + physical_avg * 20  # 80-120 range
        
        # Recovery from stamina
        base_stats.recovery = 0.5 + genome.stamina * 0.5  # 0.5-1.0 range
        
        # Terrain adaptations
        base_stats.swim = genome.swim
        base_stats.climb = genome.climb
        
        # Stamina from genome
        base_stats.stamina = genome.stamina
        
        # Luck from mutation rate (inverse relationship)
        base_stats.luck = 1.5 - genome.mutation_rate  # Higher mutation = lower luck
        
        # Intelligence from genome
        base_stats.intelligence = genome.intelligence
        
        return base_stats
    
    def _save_turtle(self, turtle: TurtleRecord):
        """Save turtle to persistent storage"""
        if self.use_sqlite:
            self._save_sqlite(turtle)
        else:
            self._save_json(turtle)
    
    def _save_sqlite(self, turtle: TurtleRecord):
        """Save turtle to SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            data = turtle.to_db_dict()
            columns = list(data.keys())
            placeholders = ', '.join(['?'] * len(columns))
            
            conn.execute(f'''
                INSERT OR REPLACE INTO turtles ({', '.join(columns)})
                VALUES ({placeholders})
            ''', list(data.values()))
        
        logger.debug(f"📋 Saved turtle to SQLite: {turtle.turtle_id}")
    
    def _save_json(self, turtle: TurtleRecord):
        """Save turtle to JSON-Lines"""
        # For JSON-Lines, we need to rewrite the whole file
        # In production, this would be optimized with append-only logs
        
        # Load existing data
        existing_data = []
        if self.json_path.exists():
            with open(self.json_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        if data['turtle_id'] != turtle.turtle_id:
                            existing_data.append(data)
        
        # Add updated turtle
        existing_data.append(turtle.to_db_dict())
        
        # Write back
        with open(self.json_path, 'w') as f:
            for data in existing_data:
                f.write(json.dumps(data) + '\n')
        
        logger.debug(f"📋 Saved turtle to JSON-Lines: {turtle.turtle_id}")
    
    def get_active_roster(self, limit: Optional[int] = None) -> List[TurtleRecord]:
        """Get active roster sorted by performance"""
        turtles = list(self.active_roster.values())
        
        # Sort by wins, then earnings, then power score
        turtles.sort(key=lambda t: (t.wins, t.earnings, t.stats.calculate_power_score()), reverse=True)
        
        if limit:
            turtles = turtles[:limit]
        
        return turtles
    
    def get_tournament_candidates(self, count: int = 16) -> List[TurtleRecord]:
        """Get top candidates for tournament seeding"""
        candidates = self.get_active_roster()
        
        # Ensure we have enough candidates
        if len(candidates) < count:
            logger.warning(f"📋 Not enough candidates: {len(candidates)} < {count}")
            return candidates
        
        # Select top candidates with some randomness for variety
        top_candidates = candidates[:count + 4]  # Get extra for randomness
        
        # Add some randomness while preserving skill hierarchy
        selected = []
        remaining = top_candidates.copy()
        
        # Always include top 4 seeds
        for i in range(min(4, len(remaining))):
            selected.append(remaining.pop(0))
        
        # Fill remaining spots with weighted random selection
        while len(selected) < count and remaining:
            # Weight towards better turtles
            weights = [1.0 / (i + 1) for i in range(len(remaining))]
            total_weight = sum(weights)
            probs = [w / total_weight for w in weights]
            
            import random
            chosen_idx = random.choices(range(len(remaining)), weights=probs)[0]
            selected.append(remaining.pop(chosen_idx))
        
        return selected[:count]
    
    def update_race_result(self, turtle_id: str, position: int, earnings: float = 0.0):
        """Update turtle with race results"""
        if turtle_id not in self.active_roster:
            # Try to load from storage
            turtle = self._load_turtle(turtle_id)
            if turtle:
                self.active_roster[turtle_id] = turtle
            else:
                logger.warning(f"📋 Turtle not found: {turtle_id}")
                return
        
        turtle = self.active_roster[turtle_id]
        
        # Update race history
        turtle.race_history.append({
            'timestamp': time.time(),
            'position': position,
            'earnings': earnings
        })
        
        # Update totals
        turtle.total_races += 1
        turtle.earnings += earnings
        turtle.last_active = time.time()
        
        if position == 1:
            turtle.wins += 1
        
        # Save to persistent storage
        self._save_turtle(turtle)
        
        logger.debug(f"📋 Updated race result for {turtle.name}: position {position}")
    
    def _load_turtle(self, turtle_id: str) -> Optional[TurtleRecord]:
        """Load specific turtle from storage"""
        if self.use_sqlite:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT * FROM turtles WHERE turtle_id = ?', (turtle_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    data = dict(zip(columns, row))
                    return TurtleRecord.from_db_dict(data)
        else:
            # JSON-Lines implementation would scan the file
            # For now, return None
            pass
        
        return None
    
    def retire_turtle(self, turtle_id: str):
        """Retire turtle from active roster"""
        if turtle_id in self.active_roster:
            turtle = self.active_roster[turtle_id]
            turtle.is_retired = True
            turtle.is_active = False
            
            # Save to storage
            self._save_turtle(turtle)
            
            # Remove from active roster
            del self.active_roster[turtle_id]
            
            # Load replacement from storage if available
            self._load_active_roster()
            
            logger.info(f"📋 Retired turtle: {turtle.name}")
    
    def get_roster_stats(self) -> Dict[str, Any]:
        """Get roster statistics"""
        total_turtles = len(self.active_roster)
        
        if total_turtles == 0:
            return {'total_active': 0}
        
        total_races = sum(t.total_races for t in self.active_roster.values())
        total_wins = sum(t.wins for t in self.active_roster.values())
        total_earnings = sum(t.earnings for t in self.active_roster.values())
        
        generations = set(t.generation for t in self.active_roster.values())
        
        return {
            'total_active': total_turtles,
            'total_races': total_races,
            'total_wins': total_wins,
            'total_earnings': total_earnings,
            'avg_win_rate': (total_wins / total_races) if total_races > 0 else 0,
            'generations': sorted(generations),
            'storage_type': 'SQLite' if self.use_sqlite else 'JSON-Lines'
        }
    
    def cleanup_inactive(self, days_inactive: int = 30):
        """Remove turtles inactive for specified days"""
        cutoff_time = time.time() - (days_inactive * 24 * 3600)
        
        inactive_turtles = [
            turtle_id for turtle_id, turtle in self.active_roster.items()
            if turtle.last_active < cutoff_time
        ]
        
        for turtle_id in inactive_turtles:
            self.retire_turtle(turtle_id)
        
        logger.info(f"📋 Cleaned up {len(inactive_turtles)} inactive turtles")


# Global roster manager instance
roster_manager = RosterManager()
