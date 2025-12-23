import customtkinter as ctk
import sys
import os

# Allow importing from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_parser import ConfigFile, ConfigLine
import theme

class EditorView(ctk.CTkFrame):
    def __init__(self, master, file_path, close_callback=None, search_query="", **kwargs):
        super().__init__(master, fg_color=theme.FG_COLOR, corner_radius=10, **kwargs)
        self.file_path = file_path
        self.close_callback = close_callback
        self.initial_search_query = search_query
        self.config_file = ConfigFile()
        self.config_file.load(file_path)
        self.entry_map = {} # Maps key to (EntryWidget, OriginalValue)
        self.label_map = {} # Maps key to LabelWidget
        self.comment_labels = []
        self.header_labels = []

        self.setup_ui()
        
        # Apply initial highlight if query exists
        if self.initial_search_query:
             # Delay slightly to ensure widgets are rendered/packed? Not strictly necessary in tkinter usually but good for scroll
             self.after(100, lambda: self.highlight_search(self.initial_search_query))

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
        self.label_map[line_obj.key] = key_label

    def highlight_search(self, query):
        query = query.lower()
        first_match = None
        
        # Helper to reset/highlight label
        def check_label(label, text):
            if query and query in text.lower():
                label.configure(text_color=theme.HIGHLIGHT_COLOR)
                return True
            else:
                label.configure(text_color=theme.TEXT_COLOR if label not in self.header_labels else theme.ACCENT_COLOR) # Restore defaults
                # Note: header default is ACCENT_COLOR, comment is TEXT_SECONDARY_COLOR. 
                # This simple restore might overwrite specific colors.
                # Better to store original color?
                # Or just check label type/list.
                return False

        # Reset and check keys
        for key, label in self.label_map.items():
            is_match = False
            if query and query in key.lower():
                label.configure(text_color=theme.HIGHLIGHT_COLOR)
                is_match = True
            else:
                label.configure(text_color=theme.TEXT_COLOR)
            
            if is_match and not first_match: first_match = label
                
        # Reset and check values
        for key, entry in self.entry_map.items():
            val = entry.get().lower()
            if query and query in val:
                entry.configure(text_color=theme.HIGHLIGHT_COLOR)
                if not first_match: first_match = entry
            else:
                entry.configure(text_color=theme.TEXT_COLOR)
        
        # Check comments
        for label in self.comment_labels:
            if query and query in label.cget("text").lower():
                label.configure(text_color=theme.HIGHLIGHT_COLOR)
                if not first_match: first_match = label
            else:
                label.configure(text_color=theme.TEXT_SECONDARY_COLOR)

        # Check headers
        for label in self.header_labels:
             # Header text might be modified (stripped), check displayed text
             if query and query in label.cget("text").lower():
                label.configure(text_color=theme.HIGHLIGHT_COLOR)
                if not first_match: first_match = label
             else:
                label.configure(text_color=theme.ACCENT_COLOR)

        if first_match:
             # Scroll to match without focusing (to keep search box active)
             try:
                # CTkScrollableFrame uses a canvas internally.
                # We need to calculate the position of the widget relative to the scrollable content.
                
                # Force update to ensure coordinates are calculated
                self.update_idletasks()
                
                # Get widget y position relative to the scrollable frame content
                widget_y = first_match.winfo_y()
                
                # Get total height of the content
                # self.scroll_frame.winfo_children()[0] is usually the internal frame containing widgets?
                # Actually CustomTkinter architecture puts widgets in self.scroll_frame
                # But self.scroll_frame is a CTkScrollableFrame, which has ._parent_canvas and ._parent_frame (the content)
                
                # The widgets are grid/packed into self.scroll_frame (which acts as the frame).
                # But correctly, the content frame is usually accessible via a property or by inspection.
                # In CTK 5.x, self.scroll_frame IS the frame you pack into? No.
                # Let's rely on calculating fraction based on widget_y / total_height
                
                # Total height of the scrollable content
                # This is tricky without internal access, but .winfo_height() of the frame should work if it's fully expanded?
                # No, scroll frame height is the visible height.
                # The scroll region is in the canvas.
                
                scroll_region = self.scroll_frame._parent_canvas.bbox("all")
                if scroll_region:
                    content_height = scroll_region[3] - scroll_region[1]
                else:
                    # Fallback
                    content_height = 1
                
                # Height of viewport
                viewport_height = self.scroll_frame._parent_canvas.winfo_height()
                
                # If content fits, no scroll needed
                if content_height <= viewport_height:
                    return

                # Calculate fraction
                # We want the widget to be at the top, or at least visible.
                # For simplicity, try to center or put at top.
                fraction = widget_y / content_height
                
                self.scroll_frame._parent_canvas.yview_moveto(fraction)
                
             except Exception as e:
                 print(f"Scroll error: {e}")
                 pass

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
        self.comment_labels.append(comment_label)

    def create_section_header(self, text, row_idx):
        header_label = ctk.CTkLabel(
            self.scroll_frame,
            text=text.strip().replace("#","").strip(),
            anchor="w",
            text_color=theme.ACCENT_COLOR,
            font=("Arial", 16, "bold")
        )
        header_label.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=(15,5), sticky="w")
        self.header_labels.append(header_label)

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
