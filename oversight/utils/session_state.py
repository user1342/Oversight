import json

class SessionState:
    def __init__(self, file_path):
        self.file_path = file_path
        self.state = self.load_state()

    def load_state(self):
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_state(self):
        with open(self.file_path, "w") as file:
            json.dump(self.state, file)

    def update_state(self, key, value):
        self.state[key] = value
        self.save_state()

    def get_plugin_config(self, plugin_name):
        return self.state.get(plugin_name, {})

    def set_plugin_config(self, plugin_name, config):
        self.state[plugin_name] = config
        self.save_state()
