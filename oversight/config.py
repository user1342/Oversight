# config.py

class Config:
    PLUGIN_FOLDER = r"C:\Users\JS\OVERSIGHT\oversight\plugins"
    SECRET_KEY = "your_secret_key"  # Ensure this is set to a secure value
    SESSION_STATE_FILE = "session_state.json"
    SESSION_TYPE = 'filesystem'
    DEBUG = True  # Add this line to enable the debug flag
    LOADER_FOLDER = r"C:\Users\JS\OVERSIGHT\oversight\loaders"
    ANALYSIS_TEXT = "This is a test sentence."