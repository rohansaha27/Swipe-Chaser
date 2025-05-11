class GamePresenter:
    def __init__(self, model, view, root):
        self.model = model
        self.view = view
        self.root = root
        
        # Game state
        self.paused = False
        self.last_score = 0
        
        # Set up key bindings
        self.root.bind('<Left>', self.handle_left)
        self.root.bind('<Right>', self.handle_right)
        self.root.bind('r', self.handle_restart)
        self.root.bind('R', self.handle_restart)
        self.root.bind('m', self.handle_menu)
        self.root.bind('M', self.handle_menu)
        self.root.bind('<space>', self.handle_space)
        
        # Set up game loop
        self.update_id = None
    
    def handle_left(self, event):
        if self.model.game_state == "playing" and not self.paused:
            self.model.move_player('left')
    
    def handle_right(self, event):
        if self.model.game_state == "playing" and not self.paused:
            self.model.move_player('right')
    
    def handle_space(self, event):
        if self.model.game_state == "start" and not self.paused:
            self.model.start_game()
        
    def handle_restart(self, event):
        if self.model.game_state == "game_over":
            self.model.start_game()
    
    def handle_menu(self, event):
        """Handle menu key press"""
        if self.model.game_state == "game_over":
            # Find the main game instance
            # Look for the main game instance in the root window's attributes
            for widget in self.root.winfo_children():
                if hasattr(widget, '_nametowidget'):
                    # Try to find the main game instance
                    if hasattr(self.root, 'master') and hasattr(self.root.master, 'show_main_menu'):
                        self.root.master.show_main_menu()
                        return
            
            # If we can't find the game instance through normal means, use a global approach
            # This is a fallback to ensure the menu button works
            for widget in self.root.winfo_toplevel().winfo_children():
                if hasattr(widget, 'show_main_menu'):
                    widget.show_main_menu()
                    return
                    
            # Last resort - try to access through global namespace
            try:
                import __main__
                if hasattr(__main__, 'game') and hasattr(__main__.game, 'show_main_menu'):
                    __main__.game.show_main_menu()
            except:
                # If all else fails, restart the game
                self.model.start_game()
    
    def update(self):
        """Main game loop update"""
        if not self.paused:
            # Update model
            self.model.update()
            
            # Check for game over state change
            if self.model.game_state == "game_over" and self.last_score != self.model.score:
                self.last_score = self.model.score
        
        # Draw the current state
        self.view.draw(self.model)
        
        # Schedule the next update (60 FPS)
        self.update_id = self.root.after(16, self.update)
