"""
PPU Core - Pixel Processing Unit with Hardware Burn Integration
ADR 174: PPU Visual Feedback for Resource Depletion
"""

import pygame
import math
import time
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from loguru import logger

from ...kernel.state import PhysicsState
from ...tactics.stakes_manager import ResourceStatus


@dataclass
class RenderState:
    """PPU rendering state with hardware burn effects"""
    base_alpha: float = 255.0
    flicker_intensity: float = 0.0
    screen_shake: float = 0.0
    color_shift: Tuple[int, int, int] = (255, 255, 255)
    static_overlay: float = 0.0
    digital_noise: float = 0.0


class PPUCore:
    """Pixel Processing Unit with Hardware Burn visual feedback"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.screen = None
        self.clock = None
        
        # Hardware burn effects
        self.render_state = RenderState()
        self.flicker_timer = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        
        # Visual effects parameters
        self.flicker_speed = 10.0  # Hz
        self.shake_decay = 0.9
        self.static_intensity = 0.0
        
        logger.debug(f"🎮 PPUCore initialized: {width}x{height}")
    
    def initialize_display(self) -> bool:
        """Initialize pygame display"""
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            self.clock = pygame.time.Clock()
            
            logger.info(f"🎮 PPU display initialized: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            logger.error(f"🎮 Failed to initialize PPU display: {e}")
            return False
    
    def process_hardware_burn(self, physics_state: PhysicsState, resource_status: ResourceStatus) -> RenderState:
        """Process hardware burn effects based on resource status"""
        # Reset render state
        self.render_state = RenderState()
        
        # Fuel depletion effects
        if resource_status == ResourceStatus.CRITICAL:
            self.render_state.flicker_intensity = 0.8
            self.render_state.base_alpha = 128.0 + 127.0 * math.sin(self.flicker_timer * self.flicker_speed)
            self.render_state.color_shift = (255, 100, 100)  # Red tint
        elif resource_status == ResourceStatus.LOW:
            self.render_state.flicker_intensity = 0.3
            self.render_state.base_alpha = 200.0 + 55.0 * math.sin(self.flicker_timer * self.flicker_speed * 0.5)
            self.render_state.color_shift = (255, 200, 100)  # Yellow tint
        
        # Hull integrity effects
        hull_pct = getattr(physics_state, 'hull_integrity', 100.0)
        if hull_pct < 10:
            self.render_state.screen_shake = 5.0 * (1.0 - hull_pct / 10.0)
            self.render_state.static_overlay = 0.3 * (1.0 - hull_pct / 10.0)
            self.render_state.digital_noise = 0.2 * (1.0 - hull_pct / 10.0)
        elif hull_pct < 30:
            self.render_state.screen_shake = 2.0 * (1.0 - hull_pct / 30.0)
            self.render_state.static_overlay = 0.1 * (1.0 - hull_pct / 30.0)
        
        # Thermal overload effects
        thermal_load = getattr(physics_state, 'thermal_load', 0.0)
        if thermal_load > 80:
            self.render_state.color_shift = (255, 150, 50)  # Orange tint
            self.render_state.digital_noise = 0.1 * (thermal_load - 80) / 20.0
        elif thermal_load > 60:
            self.render_state.color_shift = (255, 200, 150)  # Light orange
        
        return self.render_state
    
    def update_effects(self, delta_time: float):
        """Update visual effects over time"""
        # Update flicker timer
        self.flicker_timer += delta_time
        
        # Decay screen shake
        self.shake_offset_x *= self.shake_decay
        self.shake_offset_y *= self.shake_decay
        self.render_state.screen_shake *= self.shake_decay
        
        # Add random shake if active
        if self.render_state.screen_shake > 0.1:
            self.shake_offset_x = (random.random() - 0.5) * self.render_state.screen_shake
            self.shake_offset_y = (random.random() - 0.5) * self.render_state.screen_shake
    
    def render_ship(self, physics_state: PhysicsState, render_state: RenderState) -> pygame.Surface:
        """Render ship with hardware burn effects"""
        # Create ship surface
        ship_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        
        # Base ship color
        base_color = (100, 150, 255)  # Blue
        
        # Apply color shift
        color = tuple(min(255, int(base_color[i] * render_state.color_shift[i] / 255.0)) for i in range(3))
        
        # Apply alpha
        color = (*color, int(render_state.base_alpha))
        
        # Draw ship triangle
        points = [
            (10, 2),   # Top
            (2, 18),   # Bottom left
            (18, 18)   # Bottom right
        ]
        pygame.draw.polygon(ship_surface, color, points)
        
        # Draw thrust indicator if active
        if physics_state.thrust_active:
            thrust_color = (*color, int(render_state.base_alpha * 0.7))
            pygame.draw.polygon(ship_surface, thrust_color, [
                (6, 18),   # Left thrust
                (10, 14),  # Center
                (14, 18)   # Right thrust
            ])
        
        return ship_surface
    
    def render_tracers(self, physics_state: PhysicsState, render_state: RenderState) -> List[pygame.Surface]:
        """Render movement tracers with hardware burn effects"""
        tracers = []
        
        if physics_state.thrust_active:
            # Calculate tracer positions
            velocity_magnitude = math.sqrt(physics_state.velocity_x**2 + physics_state.velocity_y**2)
            
            if velocity_magnitude > 0.1:
                # Create tracer surfaces
                num_tracers = min(5, int(velocity_magnitude * 2))
                
                for i in range(num_tracers):
                    tracer_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                    
                    # Tracer color based on resource status
                    if render_state.flicker_intensity > 0.5:
                        tracer_color = (255, 50, 50, int(render_state.base_alpha * 0.8))  # Red
                    elif render_state.flicker_intensity > 0.1:
                        tracer_color = (255, 200, 50, int(render_state.base_alpha * 0.6))  # Yellow
                    else:
                        tracer_color = (100, 200, 255, int(render_state.base_alpha * 0.4))  # Blue
                    
                    pygame.draw.circle(tracer_surface, tracer_color, (2, 2), 2)
                    tracers.append(tracer_surface)
        
        return tracers
    
    def apply_screen_effects(self, surface: pygame.Surface, render_state: RenderState):
        """Apply screen-wide effects"""
        # Apply screen shake
        if render_state.screen_shake > 0.1:
            shake_surface = pygame.Surface((self.width, self.height))
            shake_surface.blit(surface, (int(self.shake_offset_x), int(self.shake_offset_y)))
            surface.blit(shake_surface, (0, 0))
        
        # Apply static overlay
        if render_state.static_overlay > 0.01:
            static_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Generate static noise
            for _ in range(int(self.width * self.height * render_state.static_overlay)):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                brightness = random.randint(0, 255)
                static_surface.set_at((x, y), (brightness, brightness, brightness, 100))
            
            surface.blit(static_surface, (0, 0))
        
        # Apply digital noise
        if render_state.digital_noise > 0.01:
            noise_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Generate digital artifacts
            for _ in range(int(self.width * self.height * render_state.digital_noise * 0.1)):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                noise_surface.set_at((x, y), (255, 255, 255, 50))
            
            surface.blit(noise_surface, (0, 0))
    
    def render_frame(self, physics_states: List[PhysicsState], resource_states: Dict[str, ResourceStatus]) -> pygame.Surface:
        """Render a complete frame with all ships and effects"""
        if not self.screen:
            return pygame.Surface((self.width, self.height))
        
        # Clear screen
        self.screen.fill((10, 10, 20))  # Dark blue background
        
        # Render each ship
        for physics_state in physics_states:
            ship_id = getattr(physics_state, 'ship_id', 'unknown')
            resource_status = resource_states.get(ship_id, ResourceStatus.OPERATIONAL)
            
            # Process hardware burn effects
            render_state = self.process_hardware_burn(physics_state, resource_status)
            
            # Render ship
            ship_surface = self.render_ship(physics_state, render_state)
            
            # Calculate position
            ship_x = int(physics_state.position[0] + self.width // 2)
            ship_y = int(physics_state.position[1] + self.height // 2)
            
            # Apply screen shake to position
            ship_x += int(self.shake_offset_x)
            ship_y += int(self.shake_offset_y)
            
            # Blit ship to screen
            self.screen.blit(ship_surface, (ship_x - 10, ship_y - 10))
            
            # Render tracers
            tracers = self.render_tracers(physics_state, render_state)
            for i, tracer in enumerate(tracers):
                tracer_offset = i * 8
                tracer_x = ship_x - int(physics_state.velocity_x * tracer_offset)
                tracer_y = ship_y - int(physics_state.velocity_y * tracer_offset)
                self.screen.blit(tracer, (tracer_x - 2, tracer_y - 2))
        
        # Apply screen effects
        self.apply_screen_effects(self.screen, self.render_state)
        
        return self.screen
    
    def update_display(self, physics_states: List[PhysicsState], resource_states: Dict[str, ResourceStatus]):
        """Update and display the PPU"""
        if not self.screen or not self.clock:
            return
        
        # Calculate delta time
        delta_time = self.clock.get_time() / 1000.0
        
        # Update effects
        self.update_effects(delta_time)
        
        # Render frame
        self.render_frame(physics_states, resource_states)
        
        # Update display
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS
    
    def shutdown(self):
        """Shutdown PPU"""
        if self.screen:
            pygame.quit()
            logger.info("🎮 PPU shutdown")
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get PPU performance metrics"""
        if not self.clock:
            return {}
        
        return {
            "fps": self.clock.get_fps(),
            "flicker_intensity": self.render_state.flicker_intensity,
            "screen_shake": self.render_state.screen_shake,
            "static_overlay": self.render_state.static_overlay,
            "digital_noise": self.render_state.digital_noise
        }


# Factory function for easy initialization
def create_ppu_core(width: int = 800, height: int = 600) -> PPUCore:
    """Create a PPUCore instance"""
    return PPUCore(width, height)


# Global instance
ppu_core = create_ppu_core()
