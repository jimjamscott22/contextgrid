import os
import sys
from pathlib import Path

def get_base_dir() -> Path:
    """
    Get the base directory of the application.
    
    When running normally from source, this resolves to the project root 
    (where the .env file is located).
    
    When running as a PyInstaller bundled executable, this resolves to 
    the ephemeral `sys._MEIPASS` folder where PyInstaller unpacks data files.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return Path(sys._MEIPASS)
    
    # Running from source: resolve up from src/utils/paths.py to the root dir
    return Path(__file__).resolve().parent.parent.parent

def get_data_dir() -> Path:
    """
    Get the path to the user's data directory. 
    This should not be inside `_MEIPASS` since that is ephemeral.
    Defaults to the `data/` folder in the project root if from source,
    or the current working directory if compiled.
    """
    if getattr(sys, 'frozen', False):
        return Path(os.getcwd()) / "data"
    
    return get_base_dir() / "data"
