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
            # Try different approaches to find the game instance
            # First, check if we have a direct reference
            try:
                import __main__
                if hasattr(__main__, 'game'):
                    # Access the global game instance
                    __main__.game.show_countdown(lambda: None)  # We don't need to call start_game here
                    return
            except:
                pass
                
            # Try to find the game instance in the root's winfo_toplevel
            root_toplevel = self.root.winfo_toplevel()
            for widget in root_toplevel.winfo_children():
                if hasattr(widget, 'show_countdown'):
                    widget.show_countdown(lambda: None)  # We don't need to call start_game here
                    return
            
            # If all else fails, just start the game directly
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
        if self.model.game_state == "playing" and not self.paused:
            self.model.update()
            
            # Check if game is over
            if self.model.game_state == "game_over":
                self.last_score = self.model.score
                
        # Update view
        if self.model.game_state == "start":
            self.view.draw_start_screen()
        elif self.model.game_state == "playing":
            self.view.draw_game_screen(self.model)
        elif self.model.game_state == "game_over":
            self.view.draw_game_over_screen(self.last_score)
        
        # Debug output to help diagnose issues
        print(f"Game state: {self.model.game_state}")
            
        # Schedule next update
        self.update_id = self.root.after(33, self.update)  # ~30 FPS
