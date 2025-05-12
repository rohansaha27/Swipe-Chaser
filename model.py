import random
import time
import os

# Import ML components
from ml.player_profiler import PlayerProfiler
from ml.difficulty_model import DifficultyModel
from ml.data_store import PlayerDataStore

class GameModel:
    def __init__(self):
        self.width = 400
        self.height = 600
        self.game_state = "start"  # start, playing, game_over
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Initialize ML components
        self.data_store = PlayerDataStore(data_dir=data_dir)
        self.player_profiler = PlayerProfiler()
        self.difficulty_model = DifficultyModel()
        
        # Session tracking
        self.session_start_time = None
        self.obstacle_id_counter = 0
        
        # Initialize game state
        self.reset()
        
    def reset(self):
        self.player_lane = 1  # 0=left, 1=center, 2=right
        self.score = 0
        self.obstacles = []  # List of (obstacle_id, lane, y) tuples
        self.coins = []      # List of (coin_id, lane, y) tuples
        
        # Default difficulty parameters (will be adjusted by ML)
        self.difficulty_params = {
            'speed': 5.0,
            'obstacle_frequency': 30,
            'pattern_complexity': 1.0,
            'coin_value': 1
        }
        
        # Game state tracking
        self.tick = 0
        self.coin_id_counter = 0
        self.obstacle_id_counter = 0
        
        # Reset player profiler for new game
        self.player_profiler.reset()
        
    def move_player(self, direction):
        old_lane = self.player_lane
        
        if direction == 'left' and self.player_lane > 0:
            self.player_lane -= 1
        elif direction == 'right' and self.player_lane < 2:
            self.player_lane += 1
            
        # Track lane change for player profiling if lane actually changed
        if old_lane != self.player_lane:
            self.player_profiler.track_lane_change(self.player_lane)
            
    def start_game(self):
        self.reset()
        self.game_state = "playing"
        
        # Start session tracking
        self.session_start_time = time.time()
        self.player_profiler.start_session()
        
        # Load initial difficulty parameters
        player_stats = self.data_store.get_player_stats()
        if player_stats['games_played'] > 0:
            # Adjust initial difficulty based on player history
            metrics = self.player_profiler.get_metrics()
            self.difficulty_params = self.difficulty_model.get_difficulty_params(metrics)
        
    def end_game(self):
        # Debug print to trace when game ends
        print(f"Game ending with score: {self.score}")
        print(f"Current game state: {self.game_state}")
        
        # Only end the game if we're in playing state
        # This prevents double-ending which could cause issues
        if self.game_state != "playing":
            print("Game already ended, ignoring end_game call")
            return
            
        self.game_state = "game_over"
        
        # End session tracking
        if self.session_start_time:
            session_duration = time.time() - self.session_start_time
            self.player_profiler.end_session()
            
            # Save session data
            self.data_store.update_session_data(
                play_time=session_duration,
                score=self.score
            )
            
            # Record difficulty parameters and performance
            metrics = self.player_profiler.get_metrics()
            self.data_store.add_difficulty_record(
                metrics=metrics,
                params=self.difficulty_params,
                score=self.score,
                duration=session_duration
            )
            
            # Add training example for the difficulty model
            # Calculate success rating based on score and duration
            success_rating = min(1.0, (self.score / max(1, session_duration * 0.1)))
            self.difficulty_model.add_training_example(
                player_metrics=metrics,
                difficulty_params=self.difficulty_params,
                success_rating=success_rating
            )
        
    def update(self):
        if self.game_state != "playing":
            return
            
        self.tick += 1
        
        # Update difficulty more frequently - every 3 seconds instead of 5
        if self.tick % 180 == 0 and self.tick > 0:
            print(f"Updating difficulty at tick {self.tick}")
            
            try:
                metrics = self.player_profiler.get_metrics()
                new_params = self.difficulty_model.get_difficulty_params(metrics)
                
                # Get current and new difficulty levels for comparison
                from view import GameView
                
                # Create a temporary view instance to use its difficulty calculation
                temp_view = GameView(None)
                current_level = temp_view._get_difficulty_level(self.difficulty_params)
                new_level = temp_view._get_difficulty_level(new_params)
                
                # Print current and new parameters with difficulty levels
                print(f"Current difficulty: {current_level}")
                print(f"Current params: {self.difficulty_params}")
                print(f"Target difficulty: {new_level}")
                print(f"Target params: {new_params}")
                
                # Print clear message if difficulty is changing
                if current_level != new_level:
                    print(f"\n*** DIFFICULTY CHANGING: {current_level} → {new_level} ***\n")
                
                # Make difficulty changes more significant - 30% change instead of 10%
                for key in self.difficulty_params:
                    if key in new_params:
                        current = self.difficulty_params[key]
                        target = new_params[key]
                        # Move 30% toward the target value for more noticeable changes
                        self.difficulty_params[key] = current + 0.3 * (target - current)
                
                # TESTING: Force difficulty progression based on score
                # This ensures you'll see difficulty changes even in short play sessions
                if self.score >= 5 and current_level == "Novice":
                    print("\n*** FORCING DIFFICULTY TO EASY DUE TO SCORE ***\n")
                    self.difficulty_params['speed'] = 5.0
                    self.difficulty_params['pattern_complexity'] = 1.2
                
                if self.score >= 10 and current_level in ["Novice", "Easy"]:
                    print("\n*** FORCING DIFFICULTY TO MEDIUM DUE TO SCORE ***\n")
                    self.difficulty_params['speed'] = 6.5
                    self.difficulty_params['pattern_complexity'] = 1.8
                
                if self.score >= 15 and current_level in ["Novice", "Easy", "Medium"]:
                    print("\n*** FORCING DIFFICULTY TO HARD DUE TO SCORE ***\n")
                    self.difficulty_params['speed'] = 8.0
                    self.difficulty_params['pattern_complexity'] = 2.5
                
                # FIXED: Ensure obstacle_frequency is always a reasonable value
                # This prevents obstacles from stopping
                if 'obstacle_frequency' in self.difficulty_params:
                    # Clamp to reasonable range (15-60)
                    self.difficulty_params['obstacle_frequency'] = max(15, min(60, self.difficulty_params['obstacle_frequency']))
                
                print(f"Updated params: {self.difficulty_params}")
            except Exception as e:
                print(f"Error updating difficulty: {e}")
                # Fallback to default parameters if something goes wrong
                self.difficulty_params = {
                    'speed': 5.0,
                    'obstacle_frequency': 30,
                    'pattern_complexity': 1.0,
                    'coin_value': 1
                }
        
        # Get current difficulty parameters
        speed = self.difficulty_params['speed']
        obstacle_frequency = self.difficulty_params['obstacle_frequency']
        pattern_complexity = self.difficulty_params['pattern_complexity']
        
        # FIXED: Ensure coin value is always an integer
        coin_value = int(self.difficulty_params['coin_value'])
        print(f"Using coin value: {coin_value} (from difficulty params)")
        
        # Move obstacles and coins down with dynamic speed
        new_obstacles = []
        for obs_id, lane, y in self.obstacles:
            new_y = y + speed
            if new_y < self.height:
                new_obstacles.append((obs_id, lane, new_y))
            else:
                # Obstacle went off screen - track as avoided
                self.player_profiler.track_obstacle_avoided(obs_id)
        self.obstacles = new_obstacles
        
        # Move coins down
        new_coins = []
        for coin_id, lane, y in self.coins:
            new_y = y + speed
            if new_y < self.height:
                new_coins.append((coin_id, lane, new_y))
            else:
                # Coin went off screen - track as missed
                self.player_profiler.track_coin_missed()
        self.coins = new_coins
        
        # FIXED: Ensure obstacle frequency is a positive integer
        if obstacle_frequency <= 0:
            obstacle_frequency = 30  # Default value if something went wrong
            print(f"WARNING: Invalid obstacle frequency {obstacle_frequency}, using default 30")
        
        # Debug print for obstacle spawning
        if self.tick % 30 == 0:
            print(f"Tick: {self.tick}, Obstacle frequency: {obstacle_frequency}, Pattern complexity: {pattern_complexity}")
            print(f"Current obstacles: {len(self.obstacles)}, Current coins: {len(self.coins)}")
        
        # Add new obstacles based on dynamic frequency and pattern complexity
        # FIXED: Use modulo with max to prevent division by zero or negative values
        if self.tick % max(1, int(obstacle_frequency)) == 0:
            # Debug print for obstacle spawning
            print(f"Spawning new obstacles at tick {self.tick}")
            
            # Ensure pattern is a valid integer between 1-3
            pattern = max(1, min(3, int(pattern_complexity)))
            print(f"Using pattern complexity: {pattern}")
            
            if pattern == 1:
                # Simple pattern - single random obstacle
                lane = random.randint(0, 2)
                self._spawn_obstacle(lane)
                print(f"Spawned simple obstacle in lane {lane}")
            elif pattern == 2:
                # Medium pattern - two obstacles with one gap
                lanes = [0, 1, 2]
                empty_lane = random.choice(lanes)
                lanes.remove(empty_lane)
                for lane in lanes:
                    self._spawn_obstacle(lane)
                print(f"Spawned medium pattern with gap in lane {empty_lane}")
            else:
                # Complex pattern - special formations
                pattern_type = random.randint(1, 3)
                if pattern_type == 1:
                    # Zigzag pattern
                    self._spawn_obstacle(1)  # Center
                    self._spawn_obstacle_delayed(0, 15)  # Left, delayed
                    self._spawn_obstacle_delayed(2, 30)  # Right, more delayed
                    print("Spawned zigzag pattern")
                elif pattern_type == 2:
                    # Wall with small gap
                    gap = random.randint(0, 2)
                    for lane in range(3):
                        if lane != gap:
                            self._spawn_obstacle(lane)
                    print(f"Spawned wall pattern with gap in lane {gap}")
                else:
                    # Random pattern
                    for _ in range(2):
                        lane = random.randint(0, 2)
                        self._spawn_obstacle(lane)
                    print("Spawned random pattern")
            
            # Add coins with 50% probability
            if random.random() < 0.5:
                coin_lane = random.randint(0, 2)
                self._spawn_coin(coin_lane)
                print(f"Spawned coin in lane {coin_lane}")
            
            # FIXED: Always spawn at least one coin every 3 obstacle patterns
            # This ensures coins keep appearing throughout the game
            elif self.tick % (max(1, int(obstacle_frequency)) * 3) == 0:
                coin_lane = random.randint(0, 2)
                self._spawn_coin(coin_lane)
                print(f"Forced coin spawn in lane {coin_lane}")
        
        player_y = 500
        
        # Process coin collection FIRST to ensure coins are collected even if player hits obstacle
        collected_coins = []
        
        # Debug print for coin value
        print(f"Current coin value: {coin_value}, Current score: {self.score}")
        
        # Make a copy of coins to iterate over
        coins_to_check = self.coins.copy()
        
        for coin_id, lane, y in coins_to_check:  # Iterate through coins
            if lane == self.player_lane and abs(player_y - y) < 30:
                # Collect coin with dynamic value
                print(f"Collecting coin: {coin_id}, value: {coin_value}")
                self.score += coin_value
                print(f"New score after collection: {self.score}")
                collected_coins.append((coin_id, lane, y))
                self.player_profiler.track_coin_collected()
        
        # Remove collected coins after iteration
        for coin in collected_coins:
            if coin in self.coins:  # Make sure it's still in the list
                self.coins.remove(coin)
                print(f"Removed coin: {coin[0]}, remaining coins: {len(self.coins)}")
        
        # Collision detection AFTER coin collection
        collision_detected = False
        
        # Make a copy of obstacles to avoid modification during iteration
        obstacles_to_check = self.obstacles.copy()
        
        for obs_id, lane, y in obstacles_to_check:
            # Check for collision
            if lane == self.player_lane:
                distance = abs(player_y - y)
                print(f"Obstacle {obs_id} at distance {distance} in lane {lane}, player lane: {self.player_lane}")
                # More precise collision detection - use a smaller hitbox
                if distance < 20:  # Collision - reduced further from 25 to 20 for more precise detection
                    print(f"COLLISION DETECTED with obstacle {obs_id}")
                    collision_detected = True
                    # Don't break immediately to allow processing of other game elements
                elif distance < 50:  # Near miss
                    self.player_profiler.track_near_miss(obs_id, distance)
        
        # End game only after all processing is complete
        if collision_detected and self.game_state == "playing":
            print("Ending game due to collision")
            self.end_game()
    
    def _spawn_obstacle(self, lane):
        """Spawn a new obstacle in the specified lane"""
        self.obstacle_id_counter += 1
        obstacle_id = f"obs_{self.obstacle_id_counter}"
        self.obstacles.append((obstacle_id, lane, -50))
        self.player_profiler.track_obstacle_spawn(obstacle_id, lane)
    
    def _spawn_obstacle_delayed(self, lane, delay):
        """Spawn an obstacle with a delay (used for complex patterns)"""
        self.obstacle_id_counter += 1
        obstacle_id = f"obs_{self.obstacle_id_counter}"
        self.obstacles.append((obstacle_id, lane, -50 - delay))
        self.player_profiler.track_obstacle_spawn(obstacle_id, lane)
    
    def _spawn_coin(self, lane):
        """Spawn a new coin in the specified lane"""
        self.coin_id_counter += 1
        coin_id = f"coin_{self.coin_id_counter}"
        self.coins.append((coin_id, lane, -30))
