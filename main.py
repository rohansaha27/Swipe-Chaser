import tkinter as tk
from model import GameModel
from view import GameView
from presenter import GamePresenter

def main():
    # Create the root window
    root = tk.Tk()
    root.title('Subway Surfers MVP')
    root.resizable(False, False)
    
    # Create the MVP components
    model = GameModel()
    view = GameView(root)
    presenter = GamePresenter(model, view, root)
    
    # Start the game loop
    root.mainloop()

if __name__ == '__main__':
    main()
