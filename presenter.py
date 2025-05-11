class GamePresenter:
    def __init__(self, model, view, root):
        self.model = model
        self.view = view
        self.root = root
        
        # Set up key bindings
        self.root.bind('<Left>', self.handle_left)
        self.root.bind('<Right>', self.handle_right)
        self.root.bind('r', self.handle_restart)
        self.root.bind('R', self.handle_restart)
        self.root.bind('<space>', self.handle_space)
        
        # Set up game loop
        self.update()
    
    def handle_left(self, event):
        if self.model.game_state == "playing":
            self.model.move_player('left')
    
    def handle_right(self, event):
        if self.model.game_state == "playing":
            self.model.move_player('right')
    
    def handle_space(self, event):
        if self.model.game_state == "start":
            self.model.start_game()
        
    def handle_restart(self, event):
        if self.model.game_state == "game_over":
            self.model.start_game()
    
    def update(self):
        self.model.update()
        self.view.draw(self.model)
        
        # Schedule the next update (30 FPS)
        self.root.after(33, self.update)
