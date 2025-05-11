import tkinter as tk

LANE_X = [100, 200, 300]
PLAYER_Y = 500

class GameView:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=400, height=600, bg='#1E90FF')  # Blue background
        self.canvas.pack()
        
        # Store canvas items that need to be updated
        # Create text with background for better visibility
        self.score_bg = self.canvas.create_rectangle(10, 10, 130, 40, fill='white', outline='black')
        self.score_text = self.canvas.create_text(70, 25, text="Score: 0", fill="black", font=("Arial", 16, "bold"))
        
        # Game state text (start, game over)
        self.state_bg = self.canvas.create_rectangle(50, 250, 350, 350, fill='white', outline='black', state='hidden')
        self.state_text = self.canvas.create_text(200, 280, text="", fill="black", font=("Arial", 20, "bold"))
        self.instructions_text = self.canvas.create_text(200, 320, text="", fill="black", font=("Arial", 12), width=250)
        
    def draw(self, model):
        # Clear canvas except for persistent UI elements
        for item in self.canvas.find_all():
            if item not in [self.score_bg, self.score_text, self.state_bg, self.state_text, self.instructions_text]:
                self.canvas.delete(item)
        
        # Handle different game states
        if model.game_state == "start":
            self._draw_start_screen()
        elif model.game_state == "game_over":
            self._draw_game_screen(model)
            self._draw_game_over_screen(model.score)
        else:  # playing
            self._draw_game_screen(model)
            # Hide instructions during gameplay
            self.canvas.itemconfig(self.state_bg, state='hidden')
            self.canvas.itemconfig(self.state_text, text="")
            self.canvas.itemconfig(self.instructions_text, text="")
            
        # Always update score and ensure it's on top
        self.canvas.itemconfig(self.score_text, text=f'Score: {model.score}')
        self.canvas.tag_raise(self.score_bg)
        self.canvas.tag_raise(self.score_text)
        
        self.root.update()
    
    def _draw_start_screen(self):
        # Show start screen
        self.canvas.itemconfig(self.state_bg, state='normal')
        self.canvas.itemconfig(self.state_text, text="Subway Surfers MVP")
        self.canvas.itemconfig(self.instructions_text, 
                              text="Controls:\n" +
                                   "← → Arrow keys to move\n" +
                                   "Press SPACE to start")
    
    def _draw_game_over_screen(self, score):
        # Show game over screen - ensure it's on top
        self.canvas.tag_raise(self.state_bg)
        self.canvas.tag_raise(self.state_text)
        self.canvas.tag_raise(self.instructions_text)
        
        self.canvas.itemconfig(self.state_bg, state='normal')
        self.canvas.itemconfig(self.state_text, text=f"Game Over! Score: {score}")
        self.canvas.itemconfig(self.instructions_text, text="Press R to restart")
    
    def _draw_game_screen(self, model):
        # Draw lanes (background layer)
        for x in LANE_X:
            self.canvas.create_rectangle(x-30, 0, x+30, 600, fill='#A9A9A9', outline='')  # Gray lanes
            
        # Draw player
        self.canvas.create_rectangle(
            LANE_X[model.player_lane]-20, PLAYER_Y-20, 
            LANE_X[model.player_lane]+20, PLAYER_Y+20, 
            fill='#FFD700', outline='')  # Gold player
            
        # Draw obstacles
        for lane, y in model.obstacles:
            self.canvas.create_rectangle(
                LANE_X[lane]-20, y-20, 
                LANE_X[lane]+20, y+20, 
                fill='#DC143C', outline='')  # Red obstacles
                
        # Draw coins
        for lane, y in model.coins:
            self.canvas.create_oval(
                LANE_X[lane]-15, y-15, 
                LANE_X[lane]+15, y+15, 
                fill='#FFFF00', outline='')  # Yellow coins
