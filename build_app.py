import PyInstaller.__main__
import customtkinter
import os

# Get the path to customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

PyInstaller.__main__.run([
    'app.py',                       # Your main script
    '--name=SEO_Analyzer',          # Name of the App
    '--noconsole',                  # Don't show a black terminal window
    '--windowed',                   # Create a .app bundle
    '--onedir',                     # Directory mode (faster startup)
    f'--add-data={ctk_path}:customtkinter', # Include theme files
    '--clean',                      # Clean cache
    # I removed the icon line entirely to fix the error
])