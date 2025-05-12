import tkinter as tk
import os
import math
import random
import time
import traceback

LANE_X = [100, 200, 300]
PLAYER_Y = 500

# Color scheme - black/grey theme with gold
BG_COLOR = '#121212'  # Dark background
LANE_COLOR = '#2A2A2A'  # Dark grey lanes
UI_BG_COLOR = '#333333'  # Dark grey UI elements
UI_TEXT_COLOR = '#FFD700'  # Gold text
PLAYER_COLOR = '#FFD700'  # Gold player
COIN_COLOR = '#FFD700'  # Gold coins
OBSTACLE_COLOR = '#FF4444'  # Red obstacles

class GameView:
    def __init__(self, root, canvas=None):
        self.root = root
        
        # Use provided canvas or create a new one
        if canvas:
            self.canvas = canvas
        else:
            self.canvas = tk.Canvas(root, width=400, height=600, bg=BG_COLOR)
            self.canvas.pack()
        
        # Initialize animation timer
        self.animation_timer = time.time()
        
        # Simple difficulty display
        self.difficulty_display_active = False
        self.difficulty_display_timer = None
        
        # Store canvas items that need to be updated
        # Create text with background for better visibility
        self.score_bg = self.canvas.create_rectangle(10, 10, 130, 40, fill=UI_BG_COLOR, outline=UI_TEXT_COLOR)
        self.score_text = self.canvas.create_text(70, 25, text="Score: 0", fill=UI_TEXT_COLOR, font=("Arial", 16, "bold"))
        
        # Add difficulty indicator
        self.difficulty_bg = self.canvas.create_rectangle(270, 10, 390, 40, fill=UI_BG_COLOR, outline=UI_TEXT_COLOR)
        self.difficulty_text = self.canvas.create_text(330, 25, text="Difficulty: Easy", fill=UI_TEXT_COLOR, font=("Arial", 12, "bold"))
        
        # Simple difficulty level indicator (centered, large, and clear)
        self.difficulty_indicator_bg = self.canvas.create_rectangle(100, 270, 300, 330, fill='#333333', outline='#FFD700', width=2, state='hidden')
        self.difficulty_indicator_text = self.canvas.create_text(200, 300, text="", fill='#FFD700', font=("Arial", 24, "bold"), state='hidden')
        
        # Track current difficulty level to detect changes
        self.current_difficulty = "Easy"
        
        # Game state text (start, game over) - centered in the canvas
        center_x = 400 / 2  # Canvas width / 2
        center_y = 600 / 2  # Canvas height / 2
        panel_width = 300
        panel_height = 200
        
        self.state_bg = self.canvas.create_rectangle(
            center_x - panel_width/2, center_y - panel_height/2,
            center_x + panel_width/2, center_y + panel_height/2,
            fill=UI_BG_COLOR, outline=UI_TEXT_COLOR, state='hidden')
        
        self.state_text = self.canvas.create_text(
            center_x, center_y - 40,  # Title position
            text="", fill=UI_TEXT_COLOR, font=("Arial", 24, "bold"))
            
        self.instructions_text = self.canvas.create_text(
            center_x, center_y + 20,  # Instructions position
            text="", fill=UI_TEXT_COLOR, font=("Arial", 14),
            width=250, justify=tk.CENTER)  # Center-aligned text
        

    
    def draw(self, model):
        """Draw the game state (legacy method)"""
        # Check if canvas still exists
        try:
            # Clear canvas except for persistent UI elements
            for item in self.canvas.find_all():
                if item not in [self.score_bg, self.score_text, self.state_bg, self.state_text, self.instructions_text]:
                    self.canvas.delete(item)
        except tk.TclError:
            # Canvas has been destroyed, nothing to draw
            return
        
        # Handle different game states
        try:
            if model.game_state == "start":
                self.draw_start_screen()
            elif model.game_state == "game_over":
                self.draw_game_screen(model)
                self.draw_game_over_screen(model.score)
            else:  # playing
                self.draw_game_screen(model)
                # Hide instructions during gameplay
                self.canvas.itemconfig(self.state_bg, state='hidden')
                self.canvas.itemconfig(self.state_text, text="")
                self.canvas.itemconfig(self.instructions_text, text="")
        except tk.TclError:
            # Canvas has been destroyed, nothing to draw
            return
            
        try:
            # Always update score and ensure it's on top
            self.canvas.itemconfig(self.score_text, text=f'Score: {model.score}')
            self.canvas.tag_raise(self.score_bg)
            self.canvas.tag_raise(self.score_text)
            
            # Update difficulty indicator
            difficulty_level = self._get_difficulty_level(model.difficulty_params)
            self.canvas.itemconfig(self.difficulty_text, text=f'Difficulty: {difficulty_level}')
            self.canvas.tag_raise(self.difficulty_bg)
            self.canvas.tag_raise(self.difficulty_text)
            
            # Check if difficulty level has changed
            if difficulty_level != self.current_difficulty:
                # Show notification of difficulty change
                self._show_difficulty_change_notification(self.current_difficulty, difficulty_level)
                # Update current difficulty
                self.current_difficulty = difficulty_level
            
            # Update the UI if root still exists
            if self.root.winfo_exists():
                self.root.update()
        except tk.TclError:
            # Canvas has been destroyed, nothing to draw
            return
        
    def draw_start_screen(self):
        """Public method to draw the start screen"""
        try:
            self._draw_start_screen()
        except tk.TclError:
            # Canvas has been destroyed
            pass
        
    def draw_game_screen(self, model):
        """Public method to draw the game screen"""
        try:
            # Clear canvas except for persistent UI elements
            for item in self.canvas.find_all():
                if item not in [self.score_bg, self.score_text, self.state_bg, self.state_text, self.instructions_text]:
                    self.canvas.delete(item)
        except tk.TclError:
            # Canvas has been destroyed
            return
                
        # Draw lanes
        for x in LANE_X:
            self.canvas.create_line(x, 0, x, 600, fill=LANE_COLOR, width=2)
            
        # Draw player
        player_x = LANE_X[model.player_lane]
        player_y = PLAYER_Y
        
        # Draw player as a rectangle with details
        self.canvas.create_rectangle(
            player_x - 20, player_y - 20,
            player_x + 20, player_y + 20,
            fill=PLAYER_COLOR, outline='#B8860B', width=2)
        
        # Add player details
        self.canvas.create_rectangle(
            player_x - 10, player_y - 15,
            player_x + 10, player_y - 5,
            fill='#B8860B')  # Face
        self.canvas.create_rectangle(
            player_x - 5, player_y - 5,
            player_x + 5, player_y + 10,
            fill='#B8860B')  # Body
        
        # Add player shadow
        shadow_offset = 5
        self.canvas.create_oval(
            player_x - 20, player_y + 20 - shadow_offset,
            player_x + 20, player_y + 30 - shadow_offset,
            fill='#000000', outline='', stipple='gray50')
            
        # Draw obstacles
        for obs_id, lane, y in model.obstacles:
            obstacle_x = LANE_X[lane]
            
            # Draw obstacle as a rectangle with details
            self.canvas.create_rectangle(
                obstacle_x - 20, y - 20,
                obstacle_x + 20, y + 20,
                fill=OBSTACLE_COLOR, outline='#8B0000', width=2)
            
            # Add X details to obstacle
            self.canvas.create_line(
                obstacle_x - 15, y - 15,
                obstacle_x + 15, y + 15,
                fill='#FFFFFF', width=2)
            self.canvas.create_line(
                obstacle_x + 15, y - 15,
                obstacle_x - 15, y + 15,
                fill='#FFFFFF', width=2)
            
        # Draw coins
        for coin_id, lane, y in model.coins:
            x = LANE_X[lane]
            # Draw coin as a circle with details
            self.canvas.create_oval(x-12, y-12, x+12, y+12, fill=COIN_COLOR, outline='#B8860B', width=2)
            # Add dollar sign
            self.canvas.create_text(x, y, text="$", fill='#B8860B', font=("Arial", 10, "bold"))
            
        # Update score and make sure it's on top
        self.canvas.itemconfig(self.score_text, text=f'Score: {model.score}')
        self.canvas.tag_raise(self.score_bg)
        self.canvas.tag_raise(self.score_text)
        
        # Hide instructions during gameplay
        self.canvas.itemconfig(self.state_bg, state='hidden')
        self.canvas.itemconfig(self.state_text, text="")
        self.canvas.itemconfig(self.instructions_text, text="")
        
    def draw_game_over_screen(self, score):
        """Public method to draw the game over screen"""
        try:
            self._draw_game_over_screen(score)
        except tk.TclError:
            # Canvas has been destroyed
            pass
    
    def _draw_start_screen(self):
        """Draw the start screen with animated elements"""
        try:
            # Show start screen
            self.canvas.itemconfig(self.state_bg, state='normal')
            self.canvas.itemconfig(self.state_text, text="SWIPE CHASER")
            self.canvas.itemconfig(self.instructions_text, 
                                  text="Controls:\n" +
                                       "← → Arrow keys to move\n" +
                                       "Press SPACE to start\n" +
                                       "ESC to pause")
        except tk.TclError:
            # Canvas has been destroyed
            pass
        
        # No animations on the start screen
    
    def _get_difficulty_level(self, difficulty_params):
        """Convert difficulty parameters to a human-readable level"""
        # Calculate overall difficulty based on speed and pattern complexity
        speed = difficulty_params.get('speed', 5.0)
        complexity = difficulty_params.get('pattern_complexity', 1.0)
        
        # Calculate a difficulty score (0-100)
        difficulty_score = ((speed - 3) / 7) * 50 + ((complexity - 1) / 2) * 50
        
        # Convert to text
        if difficulty_score < 20:
            return "Novice"
        elif difficulty_score < 40:
            return "Easy"
        elif difficulty_score < 60:
            return "Medium"
        elif difficulty_score < 80:
            return "Hard"
        else:
            return "Expert"
    
    def _show_difficulty_change_notification(self, old_level, new_level):
        """Show a simple difficulty level indicator"""
        try:
            # Just show the new difficulty level in large text
            self.canvas.itemconfig(self.difficulty_indicator_text, text=new_level)
            
            # Show the indicator
            self.canvas.itemconfig(self.difficulty_indicator_bg, state='normal')
            self.canvas.itemconfig(self.difficulty_indicator_text, state='normal')
            
            # Bring to front
            self.canvas.tag_raise(self.difficulty_indicator_bg)
            self.canvas.tag_raise(self.difficulty_indicator_text)
            
            # Cancel any existing timer
            if self.difficulty_display_timer:
                self.root.after_cancel(self.difficulty_display_timer)
            
            # Schedule hiding after 3 seconds
            self.difficulty_display_timer = self.root.after(3000, self._hide_difficulty_indicator)
            
            # Print to console for debugging
            print(f"Difficulty changed: {old_level} → {new_level}")
        except tk.TclError:
            # Canvas might be destroyed
            pass
    
    def _hide_difficulty_indicator(self):
        """Hide the difficulty indicator after display time"""
        try:
            self.canvas.itemconfig(self.difficulty_indicator_bg, state='hidden')
            self.canvas.itemconfig(self.difficulty_indicator_text, state='hidden')
            self.difficulty_display_timer = None
        except tk.TclError:
            # Canvas might be destroyed
            pass
    
    def _draw_game_over_screen(self, score):
        """Draw the enhanced game over screen with difficulty info"""
        try:
            # Show game over screen - ensure it's on top
            self.canvas.tag_raise(self.state_bg)
            self.canvas.tag_raise(self.state_text)
            self.canvas.tag_raise(self.instructions_text)
        except tk.TclError:
            # Canvas has been destroyed, nothing to draw
            return
        
        try:
            # Make the game over panel larger to accommodate more information
            center_x = 400 / 2
            center_y = 600 / 2
            panel_width = 350
            panel_height = 250
            
            # Resize the background panel
            self.canvas.coords(
                self.state_bg,
                center_x - panel_width/2, center_y - panel_height/2,
                center_x + panel_width/2, center_y + panel_height/2
            )
            
            # Set up the game over text
            self.canvas.itemconfig(self.state_bg, state='normal')
            self.canvas.itemconfig(self.state_text, text=f"GAME OVER!")
            
            # Get difficulty level name
            try:
                from model import GameModel
                # Safely check if we can access the model
                if hasattr(self.root, 'master') and \
                   hasattr(self.root.master, 'presenter') and \
                   hasattr(self.root.master.presenter, 'model') and \
                   isinstance(self.root.master.presenter.model, GameModel):
                    
                    model = self.root.master.presenter.model
                    if hasattr(model, 'difficulty_params'):
                        difficulty_level = self._get_difficulty_level(model.difficulty_params)
                        speed = round(model.difficulty_params.get('speed', 5.0), 1)
                        pattern = round(model.difficulty_params.get('pattern_complexity', 1.0), 1)
                        coin_value = model.difficulty_params.get('coin_value', 1)
                        
                        # Enhanced game over text with difficulty stats
                        self.canvas.itemconfig(self.instructions_text, 
                                              text=f"Final Score: {score}\n\n" +
                                                   f"Difficulty: {difficulty_level}\n" +
                                                   f"Speed: {speed}\n" +
                                                   f"Pattern Complexity: {pattern}\n" +
                                                   f"Coin Value: {coin_value}\n\n" +
                                                   "The game adapted to your skill level!\n\n" +
                                                   "Press R to restart\n" +
                                                   "Press M for main menu")
                        return
            except (ImportError, AttributeError, TypeError) as e:
                # Just continue to fallback
                pass
                
            # Fallback if model isn't available or any error occurred
            self.canvas.itemconfig(self.instructions_text, 
                                  text=f"Final Score: {score}\n\n" +
                                       "Press R to restart\n" +
                                       "Press M for main menu")
        except tk.TclError:
            # Canvas has been destroyed or other Tkinter error
            return
        
        # We don't need to display the score again as it's already in the instructions text
    
    def _draw_game_screen(self, model):
        """Draw the main game screen with enhanced visuals"""
        # Draw background with gradient effect
        for y in range(0, 600, 4):
            # Calculate gradient color (darker at bottom)
            color_val = max(18, int(36 - (y / 600) * 18))
            color = f'#{color_val:02x}{color_val:02x}{color_val:02x}'
            self.canvas.create_rectangle(0, y, 400, y+4, fill=color, outline='')
        
        # Draw lanes with perspective effect (narrower at top)
        for x in LANE_X:
            # Draw lane segments with perspective
            for y in range(0, 600, 30):
                # Calculate width based on y position (perspective)
                width_factor = 0.5 + (y / 600) * 0.5
                lane_width = 60 * width_factor
                
                self.canvas.create_rectangle(
                    x - lane_width/2, y, 
                    x + lane_width/2, y + 30, 
                    fill=LANE_COLOR, outline='')
                
                # Add lane markers
                if y % 120 == 0:
                    marker_width = 10 * width_factor
                    self.canvas.create_rectangle(
                        x - marker_width/2, y + 10, 
                        x + marker_width/2, y + 20, 
                        fill='#555555', outline='')
        
        # Draw player
        player_x = LANE_X[model.player_lane]
        player_y = PLAYER_Y
        
        # Draw player as a rectangle with details
        self.canvas.create_rectangle(
            player_x - 20, player_y - 20,
            player_x + 20, player_y + 20,
            fill=PLAYER_COLOR, outline='#B8860B', width=2)
        
        # Add player details
        self.canvas.create_rectangle(
            player_x - 10, player_y - 15,
            player_x + 10, player_y - 5,
            fill='#B8860B')  # Face
        self.canvas.create_rectangle(
            player_x - 5, player_y - 5,
            player_x + 5, player_y + 10,
            fill='#B8860B')  # Body
        
        # Add player shadow
        shadow_offset = 5
        self.canvas.create_oval(
            player_x - 20, player_y + 20 - shadow_offset,
            player_x + 20, player_y + 30 - shadow_offset,
            fill='#000000', outline='', stipple='gray50')
            
        # Draw obstacles
        for lane, y in model.obstacles:
            obstacle_x = LANE_X[lane]
            
            # Draw obstacle as a rectangle with details
            self.canvas.create_rectangle(
                obstacle_x - 20, y - 20,
                obstacle_x + 20, y + 20,
                fill=OBSTACLE_COLOR, outline='#8B0000', width=2)
            
            # Add X details to obstacle
            self.canvas.create_line(
                obstacle_x - 15, y - 15,
                obstacle_x + 15, y + 15,
                fill='#8B0000', width=3)
            self.canvas.create_line(
                obstacle_x - 15, y + 15,
                obstacle_x + 15, y - 15,
                fill='#8B0000', width=3)
            
            # Add obstacle shadow
            self.canvas.create_oval(
                obstacle_x - 20, y + 20,
                obstacle_x + 20, y + 30,
                fill='#000000', outline='', stipple='gray50')
                
        # Draw coins with animation
        for lane, y in model.coins:
            coin_x = LANE_X[lane]
            
            # Calculate coin animation (bobbing and rotating)
            current_time = time.time() - self.animation_timer
            bob_offset = 3 * math.sin(current_time * 5 + coin_x * 0.1)
            
            # Draw coin
            coin_radius = 15
            self.canvas.create_oval(
                coin_x - coin_radius, (y + bob_offset) - coin_radius,
                coin_x + coin_radius, (y + bob_offset) + coin_radius,
                fill=COIN_COLOR, outline='#B8860B', width=2)
            
            # Inner detail to give 3D effect
            self.canvas.create_oval(
                coin_x - coin_radius*0.7, (y + bob_offset) - coin_radius*0.7,
                coin_x + coin_radius*0.7, (y + bob_offset) + coin_radius*0.7,
                fill='#F0C000', outline='')
            
            # Add coin glow effect
            glow_size = 5 + 2 * math.sin(current_time * 10 + coin_x * 0.1)
            self.canvas.create_oval(
                coin_x - 15 - glow_size, y - 15 - glow_size + bob_offset,
                coin_x + 15 + glow_size, y + 15 + glow_size + bob_offset,
                fill='', outline='#FFD700', stipple='gray25')
    

