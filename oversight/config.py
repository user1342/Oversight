# config.py

class Config:
    PLUGIN_FOLDER = r"oversight\plugins"
    SECRET_KEY = "your_secret_key"  # Ensure this is set to a secure value
    SESSION_STATE_FILE = "session_state.json"
    SESSION_TYPE = 'filesystem'
    DEBUG = True
    LOADER_FOLDER = r"oversight\loaders"
    ANALYSIS_TEXT = "This is a test sentence."
