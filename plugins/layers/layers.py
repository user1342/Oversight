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


class AttentionMapsPlugin(PluginBase):
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

    # Function to generate attention weights for a given input text
    def get_attention_maps(self, input_text):
        model, tokenizer, loader = self._load_model()

        # Tokenize the input and generate attention maps
        inputs = self.prepare_inputs(input_text, tokenizer)
        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)

        # Collect attention weights across all layers and heads
        attentions = outputs.attentions  # List of tensors for each layer

        # Convert to JSON serializable format
        attention_data = [
            layer_attention.squeeze().tolist() for layer_attention in attentions
        ]

        loader.unload()
        return attention_data

    def register_routes(self):
        """Register plugin routes."""
        
        @self.bp.route('/default')
        def default():
            model_path = self._get_system_config_value('llm_path')
            model_info = {}
            
            if model_path and model_path != "":
                # Get attention maps and verify data
                self._model_info = self.get_attention_maps(input_text=str(self._get_system_config_value('ANALYSIS_TEXT')))
                print("DEBUG - Attention data shape:", len(self._model_info))  # Add this debug line
                print("DEBUG - First layer shape:", len(self._model_info[0]) if self._model_info else "No data")  # And this
                self.set_ready(True)
            else:
                self.set_ready(False)
            
            return self.render("layers.html", model_path=model_path, model_info=self._model_info)

    def to_json(self):
        """Convert plugin data to JSON format."""
        if not self._model_info:
            raise Exception("Model inspection not complete")
            
        return {
            "plugin": self.name,
            "model_path": self._get_system_config_value('llm_path'),
            "model_info": self._model_info
        }
