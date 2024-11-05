from flask import jsonify, current_app, render_template, request
from transformers import AutoModelForCausalLM
import torch
from oversight.utils.plugin_base import PluginBase
import json
import os
import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import json
import os 
from flask import jsonify


class ActivationDistributionsPlugin(PluginBase):
    def __init__(self, app, session_state):
        # Load the plugin configuration
        config = self._get_config()
        super().__init__(
            app,
            session_state,
            name=config['name'],
            import_name=__name__,
            url_prefix=f"/{config['name']}",
            template_folder='templates'
        )
        self._model_info = None

    # Function to load model and tokenizer
    def _load_model(self):
        # Call the provided load method to get the model and tokenizer
        loader_name = self._get_config_value('loader')
        model_name=self._get_system_config_value('llm_path')
        loader = self._get_loader(loader_name=loader_name, model_name=model_name)
        model, tokenizer = loader.load()
        model.eval()
        return model, tokenizer, loader

    def prepare_inputs(self, input_text, tokenizer):
        # Tokenize and move inputs specifically to GPU
        inputs = tokenizer(input_text, return_tensors="pt")
        inputs = {key: tensor.to("cuda") for key, tensor in inputs.items()}  # Force inputs to GPU
        return inputs
    
    # Function to generate activation distributions for a given input text
    def get_activation_distributions(self, input_text):
        model, tokenizer, loader = self._load_model()

        # Tokenize input and get activations
        inputs = self.prepare_inputs(input_text, tokenizer)
        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)

        # Collect hidden states (activations) for each layer
        hidden_states = outputs.hidden_states  # List of tensors for each layer

        # Convert to JSON serializable format
        activation_data = [
            layer_activation.squeeze().tolist() for layer_activation in hidden_states
        ]

        # Enrich data with statistics
        enriched_data = []
        for layer_index, layer_activation in enumerate(activation_data):
            layer_stats = {
                "layer": layer_index,
                "mean": torch.mean(torch.tensor(layer_activation)).item(),
                "std": torch.std(torch.tensor(layer_activation)).item(),
                "min": torch.min(torch.tensor(layer_activation)).item(),
                "max": torch.max(torch.tensor(layer_activation)).item(),
                "activations": layer_activation
            }
            enriched_data.append(layer_stats)

        loader.unload()
        return {"activation_data": enriched_data}

    def register_routes(self):
        """Register plugin routes."""
        
        @self.bp.route('/default')
        def default():
            model_path = self._get_system_config_value('llm_path')
            model_info = {}
            
            if model_path and model_path != "":
                self._model_info = self.get_activation_distributions(input_text=str(self._get_system_config_value('ANALYSIS_TEXT')))
                self.set_ready(True)  # Mark as ready after successful inspection

            else:
                self.set_ready(False)
            
            return self.render("layers2.html", model_path=model_path, model_info=self._model_info or {})

    def to_json(self):
        """Convert plugin data to JSON format."""
        if not self._model_info:
            raise Exception("Model inspection not complete")
            
        return {
            "plugin": self.name,
            "model_path": self._get_system_config_value('llm_path'),
            "model_info": self._model_info
        }
