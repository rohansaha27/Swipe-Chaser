import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import os

class ModernUIManager:
    """Handles modern UI elements for the game"""
    
    def __init__(self, root=None):
        """Initialize the UI manager"""
        if root:
            self.root = root
            self.is_themed_tk = False
        else:
            # Create a themed Tk window
            self.root = ThemedTk(theme="equilux")  # Dark modern theme
            self.is_themed_tk = True
            
        self.root.title('Swipe Chaser')
        
        # Store UI elements
        self.frames = {}
        self.buttons = {}
        self.labels = {}
        self.images = {}
        
        # Set up styles
        self.setup_styles()
    
    def setup_styles(self):
        """Set up ttk styles for UI elements"""
        self.style = ttk.Style()
        
        if not self.is_themed_tk:
            # If not using ThemedTk, configure some basic styles
            self.style.configure('TFrame', background='#121212')
            self.style.configure('TButton', 
                                background='#333333', 
                                foreground='#FFD700',
                                borderwidth=1,
                                focusthickness=3,
                                focuscolor='#FFD700')
            self.style.map('TButton',
                        background=[('active', '#444444')],
                        foreground=[('active', '#FFFFFF')])
            self.style.configure('TLabel', 
                                background='#121212', 
                                foreground='#FFD700',
                                font=('Arial', 12))
            self.style.configure('Title.TLabel', 
                                background='#121212', 
                                foreground='#FFD700',
                                font=('Arial', 24, 'bold'))
        
        # Custom styles for specific elements
        self.style.configure('Gold.TButton', 
                            background='#B8860B', 
                            foreground='#000000',
                            font=('Arial', 12, 'bold'))
        self.style.map('Gold.TButton',
                    background=[('active', '#FFD700')],
                    foreground=[('active', '#000000')])
                    
        self.style.configure('Menu.TFrame', background='#1A1A1A', relief='raised', borderwidth=2)
        self.style.configure('Game.TFrame', background='#121212')
        
    def load_image(self, name, path, size=None):
        """Load an image and optionally resize it"""
        try:
            image = Image.open(path)
            if size:
                image = image.resize(size, Image.LANCZOS)
            photo_image = ImageTk.PhotoImage(image)
            self.images[name] = photo_image
            return photo_image
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None
    
    def create_main_menu(self, start_callback, settings_callback, exit_callback):
        """Create a modern main menu"""
        # Clear any existing UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = ttk.Frame(self.root, style='Menu.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frames['main_menu'] = main_frame
        
        # Title
        title_label = ttk.Label(main_frame, text="SWIPE CHASER", style='Title.TLabel')
        title_label.pack(pady=(30, 50))
        self.labels['title'] = title_label
        
        # Buttons container
        button_frame = ttk.Frame(main_frame, style='Menu.TFrame')
        button_frame.pack(pady=10)
        
        # Create styled buttons
        start_button = ttk.Button(button_frame, text="START GAME", style='Gold.TButton',
                                command=start_callback, width=20)
        start_button.pack(pady=10)
        self.buttons['start'] = start_button
        
        settings_button = ttk.Button(button_frame, text="SETTINGS", style='TButton',
                                    command=settings_callback, width=20)
        settings_button.pack(pady=10)
        self.buttons['settings'] = settings_button
        
        exit_button = ttk.Button(button_frame, text="EXIT", style='TButton',
                                command=exit_callback, width=20)
        exit_button.pack(pady=10)
        self.buttons['exit'] = exit_button
        
        # Version info
        version_label = ttk.Label(main_frame, text="v1.0.0", style='TLabel')
        version_label.pack(side=tk.BOTTOM, pady=10)
        self.labels['version'] = version_label
        
        return main_frame
    
    def create_settings_menu(self, back_callback, save_callback):
        """Create a settings menu"""
        # Clear any existing UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create settings frame
        settings_frame = ttk.Frame(self.root, style='Menu.TFrame')
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frames['settings_menu'] = settings_frame
        
        # Title
        title_label = ttk.Label(settings_frame, text="SETTINGS", style='Title.TLabel')
        title_label.pack(pady=(30, 50))
        
        # Settings container
        options_frame = ttk.Frame(settings_frame, style='Menu.TFrame')
        options_frame.pack(pady=10, fill=tk.X)
        
        # Example settings
        difficulty_label = ttk.Label(options_frame, text="Difficulty:", style='TLabel')
        difficulty_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        difficulty_var = tk.StringVar(value="Medium")
        difficulty_combo = ttk.Combobox(options_frame, textvariable=difficulty_var, 
                                      values=["Easy", "Medium", "Hard"], state="readonly", width=15)
        difficulty_combo.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        sound_label = ttk.Label(options_frame, text="Sound:", style='TLabel')
        sound_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        
        sound_var = tk.BooleanVar(value=True)
        sound_check = ttk.Checkbutton(options_frame, variable=sound_var)
        sound_check.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(settings_frame, style='Menu.TFrame')
        button_frame.pack(pady=30)
        
        save_button = ttk.Button(button_frame, text="SAVE", style='Gold.TButton',
                               command=lambda: save_callback(difficulty_var.get(), sound_var.get()), width=15)
        save_button.pack(side=tk.LEFT, padx=10)
        
        back_button = ttk.Button(button_frame, text="BACK", style='TButton',
                               command=back_callback, width=15)
        back_button.pack(side=tk.LEFT, padx=10)
        
        return settings_frame
    
    def create_game_over_screen(self, score, restart_callback, menu_callback):
        """Create a game over screen"""
        # Create overlay frame
        overlay_frame = ttk.Frame(self.root, style='Menu.TFrame')
        overlay_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, 
                          relwidth=0.8, relheight=0.6)
        self.frames['game_over'] = overlay_frame
        
        # Game over text
        game_over_label = ttk.Label(overlay_frame, text="GAME OVER", style='Title.TLabel')
        game_over_label.pack(pady=(30, 20))
        
        # Score
        score_label = ttk.Label(overlay_frame, text=f"Score: {score}", style='TLabel',
                              font=('Arial', 18))
        score_label.pack(pady=20)
        
        # Buttons
        button_frame = ttk.Frame(overlay_frame, style='Menu.TFrame')
        button_frame.pack(pady=30)
        
        restart_button = ttk.Button(button_frame, text="PLAY AGAIN", style='Gold.TButton',
                                  command=restart_callback, width=15)
        restart_button.pack(side=tk.LEFT, padx=10)
        
        menu_button = ttk.Button(button_frame, text="MAIN MENU", style='TButton',
                               command=menu_callback, width=15)
        menu_button.pack(side=tk.LEFT, padx=10)
        
        return overlay_frame
    
    def create_pause_menu(self, resume_callback, menu_callback):
        """Create a pause menu"""
        # Create overlay frame
        overlay_frame = ttk.Frame(self.root, style='Menu.TFrame')
        overlay_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, 
                          relwidth=0.8, relheight=0.6)
        self.frames['pause'] = overlay_frame
        
        # Pause text
        pause_label = ttk.Label(overlay_frame, text="PAUSED", style='Title.TLabel')
        pause_label.pack(pady=(30, 50))
        
        # Buttons
        button_frame = ttk.Frame(overlay_frame, style='Menu.TFrame')
        button_frame.pack(pady=10)
        
        resume_button = ttk.Button(button_frame, text="RESUME", style='Gold.TButton',
                                 command=resume_callback, width=15)
        resume_button.pack(pady=10)
        
        menu_button = ttk.Button(button_frame, text="MAIN MENU", style='TButton',
                               command=menu_callback, width=15)
        menu_button.pack(pady=10)
        
        return overlay_frame
    
    def create_countdown(self, parent, callback):
        """Create a countdown animation before game starts"""
        countdown_frame = ttk.Frame(parent, style='Game.TFrame')
        countdown_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.frames['countdown'] = countdown_frame
        
        countdown_label = ttk.Label(countdown_frame, text="3", style='Title.TLabel',
                                  font=('Arial', 48, 'bold'))
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
        return countdown_frame
