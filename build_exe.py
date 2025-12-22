import PyInstaller.__main__
import customtkinter
import os

# Get the path to customtkinter module to include its assets
ctk_path = os.path.dirname(customtkinter.__file__)

print(f"Building exe with customtkinter path: {ctk_path}")

PyInstaller.__main__.run([
    'main.py',
    '--name=EndlessINIEditor',
    '--noconfirm',
    '--windowed',        # Don't show terminal window
    '--onefile',         # Bundle everything into a single exe
    f'--add-data={ctk_path};customtkinter', # Include CTK assets (Windows format ; separator)
    '--clean',
])
