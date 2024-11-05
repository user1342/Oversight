# example_plugin/main.py
from oversight.utils.plugin_base import PluginBase
from flask import current_app, jsonify

class ExamplePlugin(PluginBase):
    def __init__(self, app, session_state):
        # Load the plugin configuration
        config = self._get_config()
        
        # Initialize PluginBase
        super().__init__(
            app,
            session_state,
            name=config['name'],
            import_name=__name__,
            url_prefix=f"/{config['name']}",
            template_folder='templates'
        )
        self._analysis_complete = False

    def register_routes(self):
        """Register plugin routes."""
        
        @self.bp.route('/default')
        def default():
            # Example data to pass to the template
            model_path = self._get_system_config_value('llm_path')
            data = self._get_config_value('data')
            
            if model_path and model_path != '':
                # Perform analysis here
                try:
                    # Simulated analysis
                    self._analysis_complete = True
                    self.set_ready(True)  # Mark plugin as ready after successful analysis
                except Exception as e:
                    self._analysis_complete = False
                    self.set_ready(False)
            else:
                self.set_ready(False)
                
            # Use plugin-specific template
            return self.render("example.html", model_path=model_path, model_data=data)

    def to_json(self):
        """Convert plugin data to JSON format."""
        if not self._analysis_complete:
            raise Exception("Analysis not complete")
            
        return {
            "plugin": self.name,
            "model_path": self._get_system_config_value('llm_path'),
            "data": self._get_config_value('data'),
            "analysis_complete": self._analysis_complete
        }
