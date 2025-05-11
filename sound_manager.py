import pygame
import os

class SoundManager:
    """Handles all sound effects and music for the game"""
    
    def __init__(self):
        """Initialize the sound manager"""
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Create dictionaries to store sounds and music
        self.sounds = {}
        self.music_tracks = {}
        
        # Default volume settings
        self.sound_volume = 0.7
        self.music_volume = 0.5
        self.sound_enabled = True
        self.music_enabled = True
        
        # Create assets/audio directory if it doesn't exist
        os.makedirs("assets/audio", exist_ok=True)
    
    def load_sound(self, name, path):
        """Load a sound effect"""
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.sound_volume)
            self.sounds[name] = sound
            return True
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
            return False
    
    def load_music(self, name, path):
        """Register a music track"""
        if os.path.exists(path):
            self.music_tracks[name] = path
            return True
        else:
            print(f"Error: Music file {path} not found")
            return False
    
    def play_sound(self, name):
        """Play a sound effect"""
        if not self.sound_enabled:
            return
            
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"Warning: Sound '{name}' not found")
    
    def play_music(self, name, loops=-1):
        """Play a music track"""
        if not self.music_enabled:
            return
            
        if name in self.music_tracks:
            pygame.mixer.music.load(self.music_tracks[name])
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
        else:
            print(f"Warning: Music track '{name}' not found")
    
    def stop_music(self):
        """Stop the currently playing music"""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pause the currently playing music"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause the music"""
        pygame.mixer.music.unpause()
    
    def set_sound_volume(self, volume):
        """Set the volume for sound effects (0.0 to 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
    
    def set_music_volume(self, volume):
        """Set the volume for music (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def toggle_sound(self, enabled=None):
        """Toggle sound effects on/off"""
        if enabled is None:
            self.sound_enabled = not self.sound_enabled
        else:
            self.sound_enabled = enabled
        return self.sound_enabled
    
    def toggle_music(self, enabled=None):
        """Toggle music on/off"""
        if enabled is None:
            self.music_enabled = not self.music_enabled
        else:
            self.music_enabled = enabled
            
        if self.music_enabled:
            pygame.mixer.music.set_volume(self.music_volume)
        else:
            pygame.mixer.music.set_volume(0)
            
        return self.music_enabled
    
    def create_default_sounds(self):
        """Create some default sounds for testing when no sound files are available"""
        # Generate a coin sound
        coin_sound = pygame.mixer.Sound(buffer=self._generate_coin_sound())
        coin_sound.set_volume(self.sound_volume)
        self.sounds['coin'] = coin_sound
        
        # Generate a collision sound
        collision_sound = pygame.mixer.Sound(buffer=self._generate_collision_sound())
        collision_sound.set_volume(self.sound_volume)
        self.sounds['collision'] = collision_sound
        
        # Generate a game over sound
        game_over_sound = pygame.mixer.Sound(buffer=self._generate_game_over_sound())
        game_over_sound.set_volume(self.sound_volume)
        self.sounds['game_over'] = game_over_sound
    
    def _generate_coin_sound(self):
        """Generate a simple coin sound using pygame.sndarray"""
        import numpy as np
        
        sample_rate = 44100
        duration = 0.1  # seconds
        frequency = 1000
        
        # Generate a sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        coin_wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        # Apply a quick fade out
        fade_out = np.linspace(1, 0, len(coin_wave))
        coin_wave = coin_wave * fade_out
        
        # Convert to 16-bit signed integers
        coin_wave = (coin_wave * 32767).astype(np.int16)
        
        # Convert to stereo
        coin_wave = np.column_stack((coin_wave, coin_wave))
        
        return pygame.sndarray.make_sound(coin_wave)
    
    def _generate_collision_sound(self):
        """Generate a simple collision sound using pygame.sndarray"""
        import numpy as np
        
        sample_rate = 44100
        duration = 0.2  # seconds
        
        # Generate white noise
        noise = np.random.uniform(-1, 1, int(sample_rate * duration))
        
        # Apply a quick fade out
        fade_out = np.linspace(1, 0, len(noise))
        noise = noise * fade_out
        
        # Convert to 16-bit signed integers
        noise = (noise * 32767).astype(np.int16)
        
        # Convert to stereo
        noise = np.column_stack((noise, noise))
        
        return pygame.sndarray.make_sound(noise)
    
    def _generate_game_over_sound(self):
        """Generate a simple game over sound using pygame.sndarray"""
        import numpy as np
        
        sample_rate = 44100
        duration = 0.5  # seconds
        
        # Generate a descending tone
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        frequency = np.linspace(500, 100, len(t))
        game_over_wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        # Apply a fade out
        fade_out = np.linspace(1, 0, len(game_over_wave))
        game_over_wave = game_over_wave * fade_out
        
        # Convert to 16-bit signed integers
        game_over_wave = (game_over_wave * 32767).astype(np.int16)
        
        # Convert to stereo
        game_over_wave = np.column_stack((game_over_wave, game_over_wave))
        
        return pygame.sndarray.make_sound(game_over_wave)
