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
                               bg='#333333', fg='#FFD700',
                               activebackground='#444444', activeforeground='#FFFFFF',
                               command=self.start_game, **button_style)
        start_button.pack(pady=10)
        
        exit_button = tk.Button(button_frame, text="EXIT", 
                              bg='#333333', fg='#FFD700',
                              activebackground='#444444', activeforeground='#FFFFFF',
                              command=self.root.quit, **button_style)
        exit_button.pack(pady=10)
        
        # Version info
        version_label = tk.Label(menu_frame, text="v1.0.0", 
                               font=("Arial", 10),
                               fg="#FFD700", bg="#121212")
        version_label.pack(side=tk.BOTTOM, pady=10)
    
    def start_game(self):
        """Start the game"""
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
        
        # Show countdown before starting
        self.show_countdown(self.begin_game)
    
    def show_countdown(self, callback):
        """Show a countdown before starting the game"""
        countdown_frame = tk.Frame(self.canvas, bg='#121212')
        countdown_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        countdown_label = tk.Label(countdown_frame, text="3", 
                                 font=("Arial", 48, "bold"),
                                 fg="#FFD700", bg="#121212")
        countdown_label.pack()
        
        def update_countdown(count):
            if count > 0:
                countdown_label.config(text=str(count))
                self.root.after(1000, update_countdown, count-1)
            else:
                countdown_label.config(text="GO!")
                self.root.after(500, countdown_frame.destroy)
                self.root.after(500, callback)
        
        update_countdown(3)
    
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
    game = SwipeChaserGame()
    game.root.mainloop()

if __name__ == '__main__':
    main()
