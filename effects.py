import pygame
import math
import random

class ParticleSystem:
    """Handles particle effects for the game"""
    
    def __init__(self):
        """Initialize the particle system"""
        self.particles = []
        pygame.init()
    
    def create_coin_particles(self, x, y, count=10):
        """Create particles for coin collection effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            size = random.uniform(2, 5)
            lifetime = random.uniform(20, 40)
            color = (255, 215, 0)  # Gold color
            
            particle = {
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': color
            }
            self.particles.append(particle)
    
    def create_obstacle_particles(self, x, y, count=15):
        """Create particles for obstacle collision effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            size = random.uniform(3, 7)
            lifetime = random.uniform(15, 30)
            color = (255, 68, 68)  # Red color
            
            particle = {
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': color
            }
            self.particles.append(particle)
    
    def update(self):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['lifetime'] -= 1
            
            # Remove particles that have expired
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Draw all particles to the given surface"""
        for particle in self.particles:
            # Calculate alpha based on remaining lifetime
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            
            # Create a surface for the particle with alpha
            particle_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)), pygame.SRCALPHA)
            
            # Draw the particle with alpha
            pygame.draw.circle(
                particle_surface, 
                (*particle['color'], alpha), 
                (int(particle['size']), int(particle['size'])), 
                int(particle['size'])
            )
            
            # Blit the particle surface to the main surface
            surface.blit(particle_surface, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))


class AnimationManager:
    """Manages animations for game elements"""
    
    def __init__(self):
        """Initialize the animation manager"""
        self.animations = {}
        
    def add_animation(self, name, frames, frame_duration=5):
        """Add a new animation"""
        self.animations[name] = {
            'frames': frames,
            'frame_duration': frame_duration,
            'current_frame': 0,
            'timer': 0,
            'playing': False
        }
    
    def play(self, name, loop=True):
        """Start playing an animation"""
        if name in self.animations:
            self.animations[name]['playing'] = True
            self.animations[name]['loop'] = loop
    
    def stop(self, name):
        """Stop an animation"""
        if name in self.animations:
            self.animations[name]['playing'] = False
            self.animations[name]['current_frame'] = 0
            self.animations[name]['timer'] = 0
    
    def update(self):
        """Update all animations"""
        for name, anim in self.animations.items():
            if anim['playing']:
                anim['timer'] += 1
                
                if anim['timer'] >= anim['frame_duration']:
                    anim['timer'] = 0
                    anim['current_frame'] += 1
                    
                    if anim['current_frame'] >= len(anim['frames']):
                        if anim['loop']:
                            anim['current_frame'] = 0
                        else:
                            anim['playing'] = False
                            anim['current_frame'] = len(anim['frames']) - 1
    
    def get_current_frame(self, name):
        """Get the current frame of an animation"""
        if name in self.animations and self.animations[name]['playing']:
            frame_index = self.animations[name]['current_frame']
            return self.animations[name]['frames'][frame_index]
        return None


class TransitionEffect:
    """Handles screen transitions"""
    
    def __init__(self, width, height):
        """Initialize the transition effect"""
        self.width = width
        self.height = height
        self.progress = 0
        self.duration = 30  # frames
        self.active = False
        self.transition_type = "fade"  # fade, wipe, etc.
        self.callback = None
    
    def start(self, transition_type="fade", duration=30, callback=None):
        """Start a transition effect"""
        self.transition_type = transition_type
        self.duration = duration
        self.progress = 0
        self.active = True
        self.callback = callback
    
    def update(self):
        """Update the transition effect"""
        if not self.active:
            return
            
        self.progress += 1
        
        if self.progress >= self.duration:
            self.active = False
            if self.callback:
                self.callback()
    
    def draw(self, surface):
        """Draw the transition effect"""
        if not self.active:
            return
            
        progress_ratio = self.progress / self.duration
        
        if self.transition_type == "fade":
            # Create a surface with alpha for fading
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            alpha = int(255 * progress_ratio)
            overlay.fill((0, 0, 0, alpha))
            surface.blit(overlay, (0, 0))
            
        elif self.transition_type == "wipe":
            # Create a wipe effect
            wipe_height = int(self.height * progress_ratio)
            pygame.draw.rect(surface, (0, 0, 0), (0, 0, self.width, wipe_height))
