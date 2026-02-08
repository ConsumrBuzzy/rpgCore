"""
DGT Training Paddock - ADR 136 Implementation
Enhanced training system with headless mode and fitness threshold auto-stop

This module extends the original training_paddock.py to support:
- Headless hyperspeed training
- Multiprocessing parallel evaluation
- Auto-stop at fitness threshold
- Elite genome snapshot system
"""

import os
import json
import time
import multiprocessing as mp
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from .neuro_pilot import NeuroPilot, NeuroPilotFactory
from .headless_server import HeadlessSimulationServer, HeadlessConfig, EliteGenome


@dataclass
class TrainingMetrics:
    """Training session metrics"""
    total_generations: int
    total_time: float
    best_fitness: float
    avg_fitness: float
    fitness_progression: List[float]
    elite_genomes_saved: int
    convergence_generation: Optional[int] = None


class TrainingPaddock:
    """Enhanced training paddock with headless mode and auto-stop"""
    
    def __init__(self, population_size: int = 50, num_processes: int = None, 
                 headless_mode: bool = True, fitness_threshold: float = 200000.0):
        self.population_size = population_size
        self.num_processes = num_processes or mp.cpu_count()
        self.headless_mode = headless_mode
        self.fitness_threshold = fitness_threshold
        
        # Initialize components
        self.pilot_factory = NeuroPilotFactory("neat_config_minimal.txt")
        self.headless_server = HeadlessSimulationServer(HeadlessConfig(
            pop_size=population_size,
            num_processes=self.num_processes,
            fitness_threshold=fitness_threshold,
            headless_mode=headless_mode,
            enable_logging=not headless_mode
        ))
        
        # Training state
        self.current_generation = 0
        self.pilots: List[NeuroPilot] = []
        self.training_metrics: Optional[TrainingMetrics] = None
        self.is_training = False
        self.start_time = 0.0
        
        # Fitness tracking
        self.fitness_history: List[float] = []
        self.best_fitness_history: List[float] = []
        
        # Registry
        self.registry_path = Path("src/dgt_core/registry/brains")
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🧠 Enhanced TrainingPaddock initialized: {population_size} pilots, {self.num_processes} cores")
    
    def initialize_population(self) -> List[NeuroPilot]:
        """Initialize training population"""
        self.pilots = self.pilot_factory.create_population(self.population_size)
        self.current_generation = 0
        self.fitness_history.clear()
        self.best_fitness_history.clear()
        
        logger.info(f"🧠 Initialized population: {len(self.pilots)} pilots")
        return self.pilots
    
    def run_training_generation(self, num_matches: int = 5) -> List[Dict[str, Any]]:
        """Run one generation of training with headless evaluation"""
        if not self.pilots:
            self.initialize_population()
        
        logger.info(f"🧠 Running Generation {self.current_generation}")
        
        if self.headless_mode:
            # Headless hyperspeed evaluation
            self.pilots = self.headless_server.run_headless_generation(self.pilots)
        else:
            # Standard evaluation (for debugging/visualization)
            results = self._run_standard_evaluation(num_matches)
            self._update_pilot_fitnesses(results)
        
        # Track fitness progression
        avg_fitness = sum(p.fitness for p in self.pilots) / len(self.pilots)
        best_fitness = max(p.fitness for p in self.pilots)
        
        self.fitness_history.append(avg_fitness)
        self.best_fitness_history.append(best_fitness)
        
        # Check convergence
        if self._check_convergence():
            logger.info(f"🎯 Fitness threshold reached: {best_fitness:.2f}")
            self.is_training = False
            return self.get_training_stats()
        
        self.current_generation += 1
        return self.get_training_stats()
    
    def _run_standard_evaluation(self, num_matches: int) -> List[Dict[str, Any]]:
        """Run standard evaluation (non-headless)"""
        # This would implement the original evaluation method
        # For now, return dummy results
        results = []
        for pilot in self.pilots:
            results.append({
                'pilot_id': pilot.genome.key,
                'fitness': pilot.fitness,
                'hits_scored': 0,
                'shots_fired': 0,
                'enemies_destroyed': 0
            })
        return results
    
    def _update_pilot_fitnesses(self, results: List[Dict[str, Any]]):
        """Update pilot fitnesses from evaluation results"""
        for result in results:
            pilot = next((p for p in self.pilots if str(p.genome.key) == result['pilot_id']), None)
            if pilot:
                pilot.fitness = result['fitness']
                pilot.hits_scored = result.get('hits_scored', 0)
                pilot.shots_fired = result.get('shots_fired', 0)
                pilot.enemies_destroyed = result.get('enemies_destroyed', 0)
    
    def _check_convergence(self) -> bool:
        """Check if training has converged (reached fitness threshold)"""
        if not self.pilots:
            return False
        
        best_fitness = max(p.fitness for p in self.pilots)
        return best_fitness >= self.fitness_threshold
    
    def evolve_population(self) -> List[NeuroPilot]:
        """Evolve population to next generation"""
        if not self.pilots:
            self.initialize_population()
        
        # Use headless server for evolution
        self.pilots = self.headless_server.pilot_factory.evolve_population(self.pilots)
        
        logger.info(f"🧠 Evolved to generation {self.current_generation}")
        return self.pilots
    
    def run_training_session(self, max_generations: int = 100) -> TrainingMetrics:
        """Run complete training session with auto-stop"""
        logger.info(f"🚀 Starting training session: {max_generations} generations")
        
        self.is_training = True
        self.start_time = time.time()
        
        # Initialize population
        self.initialize_population()
        
        # Training loop
        for generation in range(max_generations):
            if not self.is_training:
                break
            
            # Run generation
            self.run_training_generation()
            
            # Evolve population
            if self.is_training:
                self.evolve_population()
        
        # Calculate metrics
        total_time = time.time() - self.start_time
        best_fitness = max(self.best_fitness_history) if self.best_fitness_history else 0.0
        avg_fitness = sum(self.fitness_history) / len(self.fitness_history) if self.fitness_history else 0.0
        
        # Find convergence generation
        convergence_gen = None
        for i, fitness in enumerate(self.best_fitness_history):
            if fitness >= self.fitness_threshold:
                convergence_gen = i
                break
        
        self.training_metrics = TrainingMetrics(
            total_generations=self.current_generation,
            total_time=total_time,
            best_fitness=best_fitness,
            avg_fitness=avg_fitness,
            fitness_progression=self.best_fitness_history.copy(),
            elite_genomes_saved=len(self.headless_server.elite_genomes),
            convergence_generation=convergence_gen
        )
        
        logger.info(f"🏆 Training complete: {self.current_generation} generations, best fitness {best_fitness:.2f}")
        
        # Save training report
        self._save_training_report()
        
        return self.training_metrics
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get current training statistics"""
        if not self.pilots:
            return {
                'generation': 0,
                'population_size': 0,
                'total_matches': 0,
                'training_mode': 'headless' if self.headless_mode else 'standard',
                'top_fitness': 0.0,
                'average_fitness': 0.0,
                'top_elo': 0.0,
                'average_elo': 0.0,
                'best_pilots': []
            }
        
        # Calculate statistics
        fitnesses = [p.fitness for p in self.pilots]
        top_fitness = max(fitnesses)
        avg_fitness = sum(fitnesses) / len(fitnesses)
        
        # Get top performers
        best_pilots = sorted(self.pilots, key=lambda p: p.fitness, reverse=True)[:3]
        best_pilot_stats = []
        
        for pilot in best_pilots:
            stats = pilot.get_performance_stats()
            best_pilot_stats.append(stats)
        
        return {
            'generation': self.current_generation,
            'population_size': len(self.pilots),
            'total_matches': self.current_generation * 5,  # Approximate
            'training_mode': 'headless' if self.headless_mode else 'standard',
            'top_fitness': top_fitness,
            'average_fitness': avg_fitness,
            'top_elo': top_fitness,  # Simplified
            'average_elo': avg_fitness,  # Simplified
            'best_pilots': best_pilot_stats
        }
    
    def _save_training_report(self):
        """Save training report to registry"""
        if not self.training_metrics:
            return
        
        report = {
            'training_metrics': {
                'total_generations': self.training_metrics.total_generations,
                'total_time': self.training_metrics.total_time,
                'best_fitness': self.training_metrics.best_fitness,
                'avg_fitness': self.training_metrics.avg_fitness,
                'elite_genomes_saved': self.training_metrics.elite_genomes_saved,
                'convergence_generation': self.training_metrics.convergence_generation
            },
            'fitness_progression': self.training_metrics.fitness_progression,
            'config': {
                'population_size': self.population_size,
                'num_processes': self.num_processes,
                'fitness_threshold': self.fitness_threshold,
                'headless_mode': self.headless_mode
            },
            'timestamp': time.time()
        }
        
        report_path = self.registry_path / "training_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Training report saved to {report_path}")
    
    def load_elite_genome(self, filename: str) -> Optional[NeuroPilot]:
        """Load elite genome from registry"""
        try:
            return self.headless_server.load_elite_genome(filename)
        except Exception as e:
            logger.error(f"❌ Failed to load elite genome: {e}")
            return None
    
    def get_latest_elite(self) -> Optional[NeuroPilot]:
        """Get latest elite pilot"""
        return self.headless_server.get_latest_elite()
    
    def stop_training(self):
        """Stop training session"""
        self.is_training = False
        logger.info("⏹️ Training stopped by user")
    
    def resume_training(self):
        """Resume training session"""
        self.is_training = True
        logger.info("▶️ Training resumed")


# Global training paddock
training_paddock = None

def initialize_training_paddock(population_size: int = 50, num_processes: int = 4, 
                               headless_mode: bool = True, fitness_threshold: float = 200000.0) -> TrainingPaddock:
    """Initialize global training paddock"""
    global training_paddock
    training_paddock = TrainingPaddock(population_size, num_processes, headless_mode, fitness_threshold)
    logger.info("🧠 Global TrainingPaddock initialized")
    return training_paddock

def get_training_paddock() -> Optional[TrainingPaddock]:
    """Get global training paddock"""
    return training_paddock
