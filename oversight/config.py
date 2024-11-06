# config.py

import os

class Config:
    PLUGIN_FOLDER = os.getenv("OVERSIGHT_PLUGIN_FOLDER", r"C:\Users\JS\OVERSIGHT\oversight\plugins")
    SECRET_KEY = os.getenv("OVERSIGHT_SECRET_KEY", "your_secret_key")  # Ensure this is set to a secure value
    SESSION_STATE_FILE = os.getenv("OVERSIGHT_SESSION_STATE_FILE", "session_state.json")
    SESSION_TYPE = os.getenv("OVERSIGHT_SESSION_TYPE", 'filesystem')
    DEBUG = os.getenv("OVERSIGHT_DEBUG", "True").lower() == "true"  # Converts to bool based on env var
    LOADER_FOLDER = os.getenv("OVERSIGHT_LOADER_FOLDER", r"C:\Users\JS\OVERSIGHT\oversight\loaders")
    ANALYSIS_TEXT = os.getenv("OVERSIGHT_ANALYSIS_TEXT", "This is a test sentence.")
