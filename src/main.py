import tkinter as tk
from src.gui.main_window import MainWindow
from pillow_heif import register_heif_opener

def main():
    # Register HEIF opener for Pillow
    register_heif_opener()
    
    root = tk.Tk()
    root.title("HEIC Compression Comparison - Group 9")
    root.geometry("1000x800")
    
    # Optional: configure basic theme/style
    
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
