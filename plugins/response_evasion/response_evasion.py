from flask import jsonify, current_app, render_template, request
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from oversight.utils.plugin_base import PluginBase
import json
import os

class ResponseEvasionPlugin(PluginBase):
    def __init__(self, app, session_state):
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
        self._model = None

    def _load_model(self):
        loader_name = self._get_config_value('loader')
        model_name = self._get_system_config_value('llm_path')
        loader = self._get_loader(loader_name=loader_name, model_name=model_name)
        model, tokenizer = loader.load()
        model.eval()
        self._model = model
        return model, tokenizer, loader

    def prepare_inputs(self, input_text, tokenizer):
        inputs = tokenizer(input_text, return_tensors="pt")
        inputs = {key: tensor.to("cuda") for key, tensor in inputs.items()}
        return inputs

    def analyze_response_evasion(self, input_text):
        model, tokenizer, loader = self._load_model()
        inputs = self.prepare_inputs(input_text, tokenizer)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=50)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        loader.unload()
        return response

    def register_routes(self):
        @self.bp.route('/default')
        def default():
            model_path = self._get_system_config_value('llm_path')
            model_info = {}
            if model_path and model_path != "":
                response = self.analyze_response_evasion(input_text=str(self._get_system_config_value('ANALYSIS_TEXT')))
                total_layers = self._model.config.num_hidden_layers
                self._model_info = {
                    "response": response,
                    "total_layers": total_layers,
                }
                self.set_ready(True)
            else:
                self.set_ready(False)
            return self.render("response_evasion.html", model_path=model_path, model_info=self._model_info)

    def to_json(self):
        if not self._model_info:
            raise Exception("Model inspection not complete")
        return {
            "plugin": self.name,
            "model_path": self._get_system_config_value('llm_path'),
            "model_info": self._model_info
        }
