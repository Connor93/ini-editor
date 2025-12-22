import customtkinter as ctk
import sys
import os

# Allow importing from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_parser import ConfigFile, ConfigLine
import theme

class EditorView(ctk.CTkFrame):
    def __init__(self, master, file_path, close_callback=None, **kwargs):
        super().__init__(master, fg_color=theme.FG_COLOR, corner_radius=10, **kwargs)
        self.file_path = file_path
        self.close_callback = close_callback
        self.config_file = ConfigFile()
        self.config_file.load(file_path)
        self.entry_map = {} # Maps key to (EntryWidget, OriginalValue)

        self.setup_ui()

    def setup_ui(self):
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=os.path.basename(self.file_path),
            font=("Arial", 20, "bold"),
            text_color=theme.TEXT_COLOR
        )
        self.title_label.pack(side="left")

        # Buttons Right Side
        self.buttons_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.buttons_frame.pack(side="right")

        if self.close_callback:
            self.close_button = ctk.CTkButton(
                self.buttons_frame,
                text="Close",
                command=self.close_callback,
                fg_color="#f04747", # Redish (Discord red-ish)
                hover_color="#d84040",
                text_color=theme.TEXT_COLOR,
                height=30,
                width=80,
                corner_radius=6
            )
            self.close_button.pack(side="right", padx=(10, 0))

        self.save_button = ctk.CTkButton(
            self.buttons_frame,
            text="Save Changes",
            command=self.save_changes,
            fg_color=theme.ACCENT_COLOR,
            hover_color=theme.HOVER_COLOR,
            text_color=theme.TEXT_COLOR,
            height=30,
            corner_radius=6
        )
        self.save_button.pack(side="right")

        # Separator (visual)
        self.separator = ctk.CTkFrame(self, height=2, fg_color=theme.ACCENT_COLOR)
        self.separator.pack(fill="x", padx=10, pady=5)

        # Scrollable content area
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent", 
            scrollbar_button_color=theme.ACCENT_COLOR,
            scrollbar_button_hover_color=theme.HOVER_COLOR
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Populate rows
        self.populate_rows()

    def populate_rows(self):
        row_idx = 0
        for line in self.config_file.lines:
            if line.type == ConfigLine.TYPE_KEY_VALUE:
                self.create_key_value_row(line, row_idx)
                row_idx += 1
            elif line.type == ConfigLine.TYPE_COMMENT:
                # Optionally show comments, but to keep it clean maybe just show as specific label 
                # or simplified view. For now let's just show key/values to edit.
                # If we want to be fancy we could interleave comments.
                # Let's try to add them as small text labels if they are standalone?
                # Actually user requirement is just "read and edit". Clean editing is better.
                # But context is important. Let's add comments as small gray labels.
                
                # Check if it's a section header style comment "### MISC ###"
                if "###" in line.raw_line:
                     self.create_section_header(line.raw_line, row_idx)
                     row_idx += 1
                else:
                     # Regular comment
                     self.create_comment_row(line.raw_line, row_idx)
                     row_idx += 1
            elif line.type == ConfigLine.TYPE_WHITESPACE:
                 # Add a small spacer
                 spacer = ctk.CTkFrame(self.scroll_frame, height=10, fg_color="transparent")
                 spacer.grid(row=row_idx, column=0, columnspan=2, sticky="ew")
                 row_idx += 1

    def create_key_value_row(self, line_obj, row_idx):
        # Key Label
        key_label = ctk.CTkLabel(
            self.scroll_frame,
            text=line_obj.key,
            anchor="w",
            text_color=theme.TEXT_COLOR,
            font=("Arial", 14)
        )
        key_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")

        # Value Entry
        value_entry = ctk.CTkEntry(
            self.scroll_frame,
            border_color=theme.ACCENT_COLOR,
            fg_color=theme.BG_COLOR,
            text_color=theme.TEXT_COLOR,
            width=300
        )
        value_entry.insert(0, line_obj.value)
        value_entry.grid(row=row_idx, column=1, padx=10, pady=5, sticky="ew")
        
        # Expand column 1
        self.scroll_frame.grid_columnconfigure(1, weight=1)

        self.entry_map[line_obj.key] = value_entry

    def create_comment_row(self, text, row_idx):
        comment_label = ctk.CTkLabel(
            self.scroll_frame,
            text=text.strip(),
            anchor="w",
            text_color=theme.TEXT_SECONDARY_COLOR,
            font=("Arial", 12, "italic"),
            wraplength=600,
            justify="left"
        )
        comment_label.grid(row=row_idx, column=0, columnspan=2, padx=20, pady=2, sticky="w")

    def create_section_header(self, text, row_idx):
        header_label = ctk.CTkLabel(
            self.scroll_frame,
            text=text.strip().replace("#","").strip(),
            anchor="w",
            text_color=theme.ACCENT_COLOR,
            font=("Arial", 16, "bold")
        )
        header_label.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=(15,5), sticky="w")

    def save_changes(self):
        # Iterate over entry map
        changed = False
        for key, entry_widget in self.entry_map.items():
            new_val = entry_widget.get()
            current_val = self.config_file.get_value(key)
            if new_val != current_val:
                self.config_file.update_value(key, new_val)
                changed = True
        
        if changed:
            try:
                self.config_file.save()
                # Optional: Show success feedback?
                self.save_button.configure(text="Saved!", fg_color="#43b581") # Green
                self.after(2000, lambda: self.save_button.configure(text="Save Changes", fg_color=theme.ACCENT_COLOR))
            except Exception as e:
                print(f"Error saving: {e}")
                self.save_button.configure(text="Error!", fg_color="#f04747") # Red
