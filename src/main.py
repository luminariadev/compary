import customtkinter as ctk
from src.gui.main_window import MainWindow
from pillow_heif import register_heif_opener

def main():
    # Register HEIF opener for Pillow
    register_heif_opener()
    
    ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    root = ctk.CTk()
    root.title("HEIC Compression Comparison - Group 9")
    root.geometry("1100x800")
    
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
