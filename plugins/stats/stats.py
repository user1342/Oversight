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

class ModelInspector:
    """
    A utility class to load a pretrained language model, inspect its key attributes,
    and return information relevant for understanding its configuration and design.
    """

    def __init__(self, model_name: str, loader,loader_name, device: str = "cuda", quantization: bool = False):
        """
        Initializes the ModelInspector class and loads the model and tokenizer.

        Args:
            model_name (str): Name of the pretrained language model.
            device (str): Device to load the model onto (e.g., "cuda" or "cpu").
            quantization (bool): If True, load model with quantization (e.g., 4-bit or 8-bit).
        """
        self.model_name = model_name
        self.device = device
        self.quantization = quantization
        self.model, self.tokenizer, self.loader = self._load_model(loader, loader_name)

    # Function to load model and tokenizer
    def _load_model(self,loader, loader_name):
        # Call the provided load method to get the model and tokenizer
        loader = loader(loader_name=loader_name, model_name=self.model_name)
        model, tokenizer = loader.load()

        return model, tokenizer, loader

    def inspect_model(self) -> dict:
        """
        Gathers key information about the loaded model and tokenizer.

        Returns:
            dict: A dictionary containing model configuration and attributes.
        """
        model_info = {
            "model_name": self.model_name,
            "num_parameters": sum(p.numel() for p in self.model.parameters()),
            "quantized": self.quantization,
            "dtype": str(self.model.dtype),
            "device_map": self.model.hf_device_map if hasattr(self.model, 'hf_device_map') else "default",
            "model_type": self.model.config.model_type,
            "max_position_embeddings": getattr(self.model.config, 'max_position_embeddings', None),
            "vocab_size": self.tokenizer.vocab_size,
            "special_tokens": self.tokenizer.special_tokens_map,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        self.loader.unload()
        return model_info


class StatsPlugin(PluginBase):
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

    def register_routes(self):
        """Register plugin routes."""
        
        @self.bp.route('/default')
        def default():
            model_path = self._get_system_config_value('llm_path')
            model_info = {}
            
            if model_path and model_path != "":
                    loader = self._get_config_value('loader')
                    inspector = ModelInspector(model_path, self._get_loader, loader)
                    self._model_info = inspector.inspect_model()
                    self.set_ready(True)  # Mark as ready after successful inspection

            else:
                self.set_ready(False)
            
            return self.render("stats.html", model_path=model_path, model_info=self._model_info or {})

    def to_json(self):
        """Convert plugin data to JSON format."""
        if not self._model_info:
            raise Exception("Model inspection not complete")
            
        return {
            "plugin": self.name,
            "model_path": self._get_system_config_value('llm_path'),
            "model_info": self._model_info
        }
