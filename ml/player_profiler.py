"""
Player Profiler for Swipe Chaser
Tracks and analyzes player performance metrics for dynamic difficulty adjustment
"""
import time
import numpy as np
from collections import deque

class PlayerProfiler:
    def __init__(self, history_size=50):
        """
        Initialize the player profiler with default metrics
        
        Args:
            history_size: Number of recent events to keep for rolling metrics
        """
        # Performance metrics
        self.reaction_times = deque(maxlen=history_size)  # Time between obstacle spawn and player reaction
        self.near_misses = deque(maxlen=history_size)     # Distance of near misses (smaller = closer call)
        self.coin_collection_rate = 0.0                   # Percentage of coins collected
        self.lane_changes = 0                             # Number of lane changes
        self.obstacles_avoided = 0                        # Number of obstacles successfully avoided
        self.coins_collected = 0                          # Number of coins collected
        self.coins_missed = 0                             # Number of coins missed
        self.play_time = 0                                # Total play time in seconds
        self.session_start_time = None                    # When the current session started
        
        # Obstacle tracking for reaction time calculation
        self.active_obstacles = {}  # {obstacle_id: {'lane': lane, 'spawn_time': time}}
        self.last_player_lane = 1   # Default center lane
        self.last_lane_change_time = 0  # Last time player changed lanes
        
    def start_session(self):
        """Start a new play session and reset session-specific metrics"""
        self.session_start_time = time.time()
        self.last_lane_change_time = time.time()
    
    def end_session(self):
        """End the current session and update total play time"""
        if self.session_start_time:
            self.play_time += time.time() - self.session_start_time
            self.session_start_time = None
    
    def track_lane_change(self, new_lane, current_time=None):
        """
        Track when the player changes lanes
        
        Args:
            new_lane: The lane the player moved to (0, 1, or 2)
            current_time: Current timestamp, defaults to time.time()
        """
        if current_time is None:
            current_time = time.time()
            
        if new_lane != self.last_player_lane:
            # Calculate reaction time if there are obstacles in the lane the player just left
            for obs_id, obs_data in list(self.active_obstacles.items()):
                if obs_data['lane'] == self.last_player_lane:
                    reaction_time = current_time - obs_data['spawn_time']
                    self.reaction_times.append(reaction_time)
            
            self.lane_changes += 1
            self.last_player_lane = new_lane
            self.last_lane_change_time = current_time
    
    def track_obstacle_spawn(self, obstacle_id, lane, current_time=None):
        """
        Track when a new obstacle spawns
        
        Args:
            obstacle_id: Unique identifier for the obstacle
            lane: Lane where the obstacle spawned (0, 1, or 2)
            current_time: Current timestamp, defaults to time.time()
        """
        if current_time is None:
            current_time = time.time()
            
        self.active_obstacles[obstacle_id] = {
            'lane': lane,
            'spawn_time': current_time
        }
    
    def track_obstacle_avoided(self, obstacle_id):
        """
        Track when an obstacle is successfully avoided
        
        Args:
            obstacle_id: Unique identifier for the avoided obstacle
        """
        if obstacle_id in self.active_obstacles:
            self.obstacles_avoided += 1
            del self.active_obstacles[obstacle_id]
    
    def track_near_miss(self, obstacle_id, distance):
        """
        Track when player narrowly avoids an obstacle
        
        Args:
            obstacle_id: Unique identifier for the obstacle
            distance: How close the player came to hitting the obstacle (smaller = closer)
        """
        self.near_misses.append(distance)
        if obstacle_id in self.active_obstacles:
            del self.active_obstacles[obstacle_id]
    
    def track_coin_collected(self):
        """Track when player collects a coin"""
        self.coins_collected += 1
        self._update_coin_rate()
    
    def track_coin_missed(self):
        """Track when player misses a coin"""
        self.coins_missed += 1
        self._update_coin_rate()
    
    def _update_coin_rate(self):
        """Update the coin collection rate"""
        total_coins = self.coins_collected + self.coins_missed
        if total_coins > 0:
            self.coin_collection_rate = self.coins_collected / total_coins
    
    def get_metrics(self):
        """
        Get the current player metrics for difficulty adjustment
        
        Returns:
            dict: Dictionary of player metrics
        """
        # Calculate average reaction time (default to 0.5 if no data)
        avg_reaction_time = np.mean(self.reaction_times) if self.reaction_times else 0.5
        
        # Calculate average near miss distance (default to 50 if no data)
        avg_near_miss = np.mean(self.near_misses) if self.near_misses else 50
        
        return {
            'reaction_time': avg_reaction_time,
            'near_miss_distance': avg_near_miss,
            'coin_collection_rate': self.coin_collection_rate,
            'lane_changes_per_minute': self._calculate_lane_changes_per_minute(),
            'obstacles_avoided': self.obstacles_avoided,
            'play_time': self.play_time
        }
    
    def _calculate_lane_changes_per_minute(self):
        """Calculate lane changes per minute of play time"""
        total_time = self.play_time
        if self.session_start_time:
            total_time += time.time() - self.session_start_time
            
        if total_time > 0:
            return (self.lane_changes / total_time) * 60
        return 0
    
    def reset(self):
        """Reset all player metrics"""
        self.reaction_times.clear()
        self.near_misses.clear()
        self.coin_collection_rate = 0.0
        self.lane_changes = 0
        self.obstacles_avoided = 0
        self.coins_collected = 0
        self.coins_missed = 0
        self.play_time = 0
        self.session_start_time = None
        self.active_obstacles = {}
        self.last_player_lane = 1
