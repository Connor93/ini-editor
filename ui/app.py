import customtkinter as ctk
import os
import sys
import glob

# Allow importing from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import theme
from settings import Settings
from ui.editor_view import EditorView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Endless INI Editor")
        self.geometry("1200x800")
        
        # Apply Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue") # Fallback, we use custom colors mostly
        
        self.configure(fg_color=theme.BG_COLOR)

        self.settings = Settings()
        self.current_folder = self.settings.get_last_folder()
        self.ini_files = [] # List of full paths

        self.setup_ui()

        # If we have a stored folder, try to load it. Otherwise show selector.
        if self.current_folder and os.path.exists(self.current_folder):
            self.load_folder(self.current_folder)
        else:
            self.show_folder_selection()

    def setup_ui(self):
        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=theme.HEADER_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(2, weight=1) # File list expands

        # Sidebar Header
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="INI EDITOR", 
            font=("Arial", 24, "bold"),
            text_color=theme.ACCENT_COLOR
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Change Folder Button
        self.folder_btn = ctk.CTkButton(
            self.sidebar,
            text="Change Folder",
            command=self.select_folder_dialog,
            fg_color=theme.FG_COLOR,
            hover_color=theme.ACCENT_COLOR,
            border_width=2,
            border_color=theme.ACCENT_COLOR
        )
        self.folder_btn.grid(row=1, column=0, padx=20, pady=10)

        # File List Scrollable
        self.file_list_frame = ctk.CTkScrollableFrame(
            self.sidebar, 
            fg_color="transparent",
            label_text="Files Found",
            label_text_color=theme.TEXT_SECONDARY_COLOR
        )
        self.file_list_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Main Content Area
        self.tab_view = ctk.CTkTabview(
            self, 
            fg_color=theme.FG_COLOR,
            segmented_button_fg_color=theme.BG_COLOR,
            segmented_button_selected_color=theme.ACCENT_COLOR,
            segmented_button_selected_hover_color=theme.HOVER_COLOR,
            segmented_button_unselected_color=theme.FG_COLOR,
            segmented_button_unselected_hover_color=theme.HEADER_COLOR
        )
        self.tab_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Welcome Message (Initial state)
        self.welcome_label = ctk.CTkLabel(
            self,
            text="Welcome to Endless INI Editor\nSelect a folder to begin.",
            font=("Arial", 20),
            text_color=theme.TEXT_SECONDARY_COLOR
        )

    def show_folder_selection(self):
        # If no folder loaded, hide tab view and show welcome/prompt
        self.tab_view.grid_forget()
        self.welcome_label.grid(row=0, column=1)
        # Verify valid folder if previously set but now missing
        if self.current_folder and not os.path.exists(self.current_folder):
             self.current_folder = None
             self.settings.set_last_folder(None)
        
        if not self.current_folder:
            # Maybe auto-trigger dialog? Or just let user click button.
            # User requirement: "initially ask you to select a folder".
            # Let's verify if we are in the mainloop first.
            # self.after(100, self.select_folder_dialog) # This can be annoying if popping up immediately
            pass

    def select_folder_dialog(self):
        folder = ctk.filedialog.askdirectory(title="Select Root Folder")
        if folder:
            self.load_folder(folder)

    def load_folder(self, folder_path):
        self.current_folder = folder_path
        self.settings.set_last_folder(folder_path)
        
        # Hide welcome, show tabs
        self.welcome_label.grid_forget()
        self.tab_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Scan for INI files
        self.scan_files()
        
        # Update sidebar
        self.update_file_list()

    def scan_files(self):
        self.ini_files = []
        # Recursive scan for .ini files
        # Using glob for simplicity
        search_pattern = os.path.join(self.current_folder, "**", "*.ini")
        # glob.glob might be slow for huge directories, but for a repo it's fine. 
        # recursive=True requires python 3.5+
        files = glob.glob(search_pattern, recursive=True)
        self.ini_files = sorted(files)

    def update_file_list(self):
        # Clear existing buttons
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        for fpath in self.ini_files:
            # Create relative path for display
            try:
                rel_path = os.path.relpath(fpath, self.current_folder)
            except:
                rel_path = os.path.basename(fpath)

            btn = ctk.CTkButton(
                self.file_list_frame,
                text=rel_path,
                anchor="w",
                fg_color="transparent",
                text_color=theme.TEXT_COLOR,
                hover_color=theme.FG_COLOR,
                command=lambda p=fpath: self.open_file(p)
            )
            btn.pack(fill="x", pady=2)

    def open_file(self, file_path):
        # Check if tab exists
        tab_name = os.path.basename(file_path)
        
        # CTkTabview doesn't easily expose list of tabs to check existence by name safely without error
        # So handle try/except
        try:
            self.tab_view.add(tab_name)
            # If successful, create the view
            
            # Create EditorView inside the tab
            # tab_view.tab(name) returns the frame for that tab
            editor = EditorView(
                self.tab_view.tab(tab_name), 
                file_path,
                close_callback=lambda: self.close_tab(tab_name)
            )
            editor.pack(fill="both", expand=True)
            
        except ValueError:
            # Tab likely already exists
            pass
        
        self.tab_view.set(tab_name)

    def close_tab(self, tab_name):
        self.tab_view.delete(tab_name)
