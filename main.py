import tkinter as tk
import os
import time

from model import GameModel
from view import GameView
from presenter import GamePresenter

class SwipeChaserGame:
    def __init__(self):
        # Create the root window with custom styling
        self.root = tk.Tk()
        self.root.title('Swipe Chaser')
        self.root.resizable(False, False)
        self.root.configure(bg='#121212')  # Dark background
        
        # Game state
        self.current_screen = "main_menu"
        self.game_running = False
        
        # Create main menu
        self.show_main_menu()
    
    def show_main_menu(self):
        """Display the main menu"""
        self.current_screen = "main_menu"
        self.game_running = False
        
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create a frame for the menu
        menu_frame = tk.Frame(self.root, bg='#121212', padx=20, pady=20)
        menu_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(menu_frame, text="SWIPE CHASER", 
                             font=("Arial", 24, "bold"),
                             fg="#FFD700", bg="#121212")
        title_label.pack(pady=(30, 50))
        
        # Buttons container
        button_frame = tk.Frame(menu_frame, bg='#121212')
        button_frame.pack(pady=10)
        
        # Create styled buttons
        button_style = {
            'font': ('Arial', 12, 'bold'),
            'width': 20,
            'bd': 1,
            'relief': tk.RAISED,
            'padx': 10,
            'pady': 5
        }
        
        start_button = tk.Button(button_frame, text="START GAME", 
                               bg='#FFD700', fg='#000000',
                               activebackground='#D4AF37', activeforeground='#000000',
                               command=self.start_game, **button_style)
        start_button.pack(pady=10)
        
        exit_button = tk.Button(button_frame, text="EXIT", 
                              bg='#FFD700', fg='#000000',
                              activebackground='#D4AF37', activeforeground='#000000',
                              command=self.root.quit, **button_style)
        exit_button.pack(pady=10)
        
        # Version info
        version_label = tk.Label(menu_frame, text="v1.0.0", 
                               font=("Arial", 10),
                               fg="#FFD700", bg="#121212")
        version_label.pack(side=tk.BOTTOM, pady=10)
    
    def start_game(self):
        """Initialize the game components"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create game canvas
        self.canvas = tk.Canvas(self.root, width=400, height=600, bg='#121212')
        self.canvas.pack()
        
        # Create the MVP components
        self.model = GameModel()
        self.view = GameView(self.root, canvas=self.canvas)
        
        # Create presenter
        self.presenter = GamePresenter(
            self.model, 
            self.view, 
            self.root
        )
        
        # Start the game loop
        self.presenter.update()
    
    def show_countdown(self, callback):
        """Show a countdown on a separate screen"""
        # Clear the entire window first
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create a full-screen canvas for the countdown
        countdown_canvas = tk.Canvas(self.root, width=400, height=600, bg='#121212')
        countdown_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create a large centered countdown label
        countdown_label = tk.Label(self.root, text="3", 
                                 font=("Arial", 120, "bold"),
                                 fg="#FFD700", bg="#121212")
        countdown_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Make sure the countdown is visible on top
        self.root.update()
        
        def update_countdown(count):
            if count > 0:
                countdown_label.config(text=str(count))
                self.root.after(1000, update_countdown, count-1)
            else:
                countdown_label.config(text="GO!")
                self.root.after(800, lambda: self.prepare_game_screen(callback))
        
        # Start the countdown
        update_countdown(3)
        
    def prepare_game_screen(self, callback):
        """Prepare the game screen after countdown"""
        # Clear the countdown screen
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create game canvas
        self.canvas = tk.Canvas(self.root, width=400, height=600, bg='#121212')
        self.canvas.pack()
        
        # Create the MVP components
        self.model = GameModel()
        self.view = GameView(self.root, canvas=self.canvas)
        self.presenter = GamePresenter(self.model, self.view, self.root)
        
        # Set up key bindings
        self.root.bind('<Left>', self.presenter.handle_left)
        self.root.bind('<Right>', self.presenter.handle_right)
        self.root.bind('r', self.presenter.handle_restart)
        self.root.bind('R', self.presenter.handle_restart)
        self.root.bind('m', self.presenter.handle_menu)
        self.root.bind('M', self.presenter.handle_menu)
        self.root.bind('<space>', self.presenter.handle_space)
        self.root.bind('<Escape>', lambda e: self.toggle_pause())
        
        # Important: Start the game BEFORE calling the callback
        self.model.start_game()  # This sets game_state to "playing"
        
        # Set game state variables
        self.current_screen = "game"
        self.game_running = True
        
        # Start the game loop
        self.presenter.update()
        
        # Call the callback if needed
        # callback()  # We don't need this anymore
    
    def begin_game(self):
        """Begin the game after countdown"""
        self.current_screen = "game"
        self.game_running = True
        
        # Set up pause key
        self.root.bind('<Escape>', lambda e: self.toggle_pause())
        
        # Start the game
        self.presenter.update()
    
    def toggle_pause(self):
        """Toggle game pause state"""
        if not self.game_running:
            return
            
        if hasattr(self, 'pause_menu'):
            # Resume game
            self.pause_menu.destroy()
            delattr(self, 'pause_menu')
            self.presenter.paused = False
        else:
            # Pause game
            self.presenter.paused = True
            
            # Create pause menu
            self.pause_menu = tk.Frame(self.canvas, bg='#333333', bd=2, relief=tk.RAISED)
            self.pause_menu.place(relx=0.5, rely=0.5, anchor=tk.CENTER, 
                                relwidth=0.8, relheight=0.6)
            
            # Pause text
            pause_label = tk.Label(self.pause_menu, text="PAUSED", 
                                 font=("Arial", 24, "bold"),
                                 fg="#FFD700", bg="#333333")
            pause_label.pack(pady=(30, 50))
            
            # Buttons
            button_frame = tk.Frame(self.pause_menu, bg='#333333')
            button_frame.pack(pady=10)
            
            button_style = {
                'font': ('Arial', 12, 'bold'),
                'width': 15,
                'bd': 1,
                'relief': tk.RAISED,
                'padx': 10,
                'pady': 5
            }
            
            resume_button = tk.Button(button_frame, text="RESUME", 
                                   bg='#333333', fg='#FFD700',
                                   activebackground='#444444', activeforeground='#FFFFFF',
                                   command=self.toggle_pause, **button_style)
            resume_button.pack(pady=10)
            
            menu_button = tk.Button(button_frame, text="MAIN MENU", 
                                  bg='#333333', fg='#FFD700',
                                  activebackground='#444444', activeforeground='#FFFFFF',
                                  command=self.show_main_menu, **button_style)
            menu_button.pack(pady=10)

def main():
    # Create assets directory if it doesn't exist
    os.makedirs("assets/images", exist_ok=True)
    
    # Start the game
    global game  # Make the game instance globally accessible
    game = SwipeChaserGame()
    game.root.mainloop()

if __name__ == '__main__':
    main()
