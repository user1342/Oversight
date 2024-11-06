# plugin_base.py
from flask import Blueprint, render_template
import os 
import json 
from flask import jsonify, current_app, render_template, request
import oversight.utils.loader_runner as loader_runner

class PluginBase:
    def __init__(self, app, session_state, name, import_name, url_prefix, template_folder='templates'):
        """
        Initializes the PluginBase and registers the blueprint with provided settings.
        
        Args:
            app (Flask): The Flask app instance.
            session_state: The session state for plugin configuration.
            name (str): Unique name for the plugin.
            import_name (str): Import name of the plugin module.
            url_prefix (str): URL prefix for the plugin routes.
            template_folder (str): Folder containing the plugin's templates.
        """
        self.app = app
        self.name = name  # Store plugin name
        self.session_state = session_state

        # Set the unique template folder for the plugin
        plugin_dir = os.path.abspath(os.path.dirname(import_name.replace('.', os.sep)))
        self.template_folder = os.path.join(plugin_dir, template_folder)
        
        self.bp = Blueprint(
            name,
            import_name,
            url_prefix=url_prefix,
            template_folder=self.template_folder  # Ensure unique template folder path
        )
        self.register_routes()

        config = self._get_config()
        session_state.set_plugin_config(name, config)
        self._ready = False  # Add ready state tracking

    def register_routes(self):
        """Subclasses should implement this method to define their routes."""
        raise NotImplementedError("register_routes method must be implemented by subclasses")

    def to_json(self):
        """Abstract method that must be implemented by all plugins to return their data as JSON."""
        raise NotImplementedError("to_json method must be implemented by subclasses")

    def _get_config_value(self, key):
        config = self._get_config()
        return config.get(key, None)

    def _get_system_config(self):
        session_state = current_app.config['session_state']
        overall_config = session_state.load_state()
        return overall_config
    
    def _get_system_config_value(self, key):
        overall_config = self._get_system_config()
        return overall_config.get(key, None)

    def _get_loader(self, loader_name, *args, **kwargs):
        return loader_runner.run_loader(loader_name=loader_name, *args, **kwargs)

    def _get_config(self):
        # Get the absolute path of the current plugin's directory
        plugin_dir = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
        config_path = os.path.join(plugin_dir, 'config.json')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"No config found at {config_path} for plugin {self.__class__.__name__}")
        
        # Load the config JSON file
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            return config

    def _get_config_value(self, key):
        config = self._get_config()
        return config.get(key, None)

    def _get_system_config(self):
        session_state = current_app.config['session_state']
        overall_config = session_state.load_state()
        return overall_config
    
    def _get_system_config_value(self, key):
        overall_config = self._get_system_config()
        return overall_config.get(key, None)

    def is_ready(self):
        """Check if plugin has completed its analysis and is ready for reporting."""
        return self._ready

    def set_ready(self, state=True):
        """Set the ready state of the plugin."""
        self._ready = state

    def render(self, template_name, **kwargs):
        """
        Renders the specified template with data passed as kwargs.

        Args:
            template_name (str): Name of the template file.
            **kwargs: Arbitrary keyword arguments for template rendering.
        """
        model_path = kwargs.get('model_path', '')
        if not model_path and model_path != '':
            self._ready = False  # Reset ready state when waiting
            return render_template("waiting.html")

        # Add default config to kwargs
        kwargs['config'] = self._get_config()
        
        # Prepend template path with plugin name to enforce namespacing
        return render_template(template_name, **kwargs)

