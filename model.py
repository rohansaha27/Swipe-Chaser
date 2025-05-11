import random

class GameModel:
    def __init__(self):
        self.width = 400
        self.height = 600
        self.game_state = "start"  # start, playing, game_over
        self.reset()
        
    def reset(self):
        self.player_lane = 1  # 0=left, 1=center, 2=right
        self.score = 0
        self.obstacles = []  # List of (lane, y) tuples
        self.coins = []      # List of (lane, y) tuples
        self.speed = 5
        self.tick = 0
        
    def move_player(self, direction):
        if direction == 'left' and self.player_lane > 0:
            self.player_lane -= 1
        elif direction == 'right' and self.player_lane < 2:
            self.player_lane += 1
            
    def start_game(self):
        self.reset()
        self.game_state = "playing"
        
    def end_game(self):
        self.game_state = "game_over"
        
    def update(self):
        if self.game_state != "playing":
            return
            
        self.tick += 1
        # Move obstacles and coins down
        self.obstacles = [(lane, y + self.speed) for lane, y in self.obstacles]
        self.coins = [(lane, y + self.speed) for lane, y in self.coins]
        # Remove off-screen
        self.obstacles = [(lane, y) for lane, y in self.obstacles if y < self.height]
        self.coins = [(lane, y) for lane, y in self.coins if y < self.height]
        # Add new obstacles/coins
        if self.tick % 30 == 0:
            lane = random.randint(0, 2)
            self.obstacles.append((lane, -50))
            if random.random() < 0.5:
                coin_lane = random.randint(0, 2)
                self.coins.append((coin_lane, -30))
        # Collision detection
        player_y = 500
        for lane, y in list(self.obstacles):  # Use list() to avoid modification during iteration
            if lane == self.player_lane and player_y-30 < y < player_y+30:
                self.end_game()
        for lane, y in list(self.coins):  # Use list() to avoid modification during iteration
            if lane == self.player_lane and player_y-30 < y < player_y+30:
                self.score += 1
                self.coins.remove((lane, y))
