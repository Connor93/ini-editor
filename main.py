import sys
import os

# Ensure dependencies are available (though likely installed in global or venv)
try:
    import customtkinter
except ImportError:
    print("Error: customtkinter is not installed. Please run 'pip install customtkinter'.")
    sys.exit(1)

from ui.app import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
