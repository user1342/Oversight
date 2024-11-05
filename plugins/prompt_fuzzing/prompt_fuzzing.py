from flask import jsonify, current_app, render_template, request
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from oversight.utils.plugin_base import PluginBase
import json
import os
import logging
import random

class PromptFuzzingPlugin(PluginBase):
    """
    This plugin performs advanced prompt fuzzing to test various random and semi-random prompt modifications.
    It identifies unexpected or undesired model behaviors by introducing changing contexts or topics mid-prompt.
    """

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
        self._fuzzing_results = None

    def _load_model(self):
        loader_name = self._get_config_value('loader')
        model_name = self._get_system_config_value('llm_path')
        loader = self._get_loader(loader_name=loader_name, model_name=model_name)
        model, tokenizer = loader.load()
        model.eval()
        return model, tokenizer, loader

    def fuzz_prompt(self, input_text, tokenizer, model):
        fuzzed_prompts = self.generate_fuzzed_prompts(input_text)
        results = []
        for prompt in fuzzed_prompts:
            inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
            with torch.no_grad():
                outputs = model.generate(**inputs)
            results.append(tokenizer.decode(outputs[0], skip_special_tokens=True))
        return results

    def generate_fuzzed_prompts(self, input_text):
        """
        Generate more complex fuzzed prompts by introducing random modifications,
        conditional logic, and changing contexts.
        """
        fuzzed_prompts = []
        modifications = ["?", "!", "...", " suddenly", " unexpectedly", " without warning"]
        contexts = [" in a different language", " with a different tone", " in a formal style", " in a casual style"]

        for mod in modifications:
            fuzzed_prompts.append(input_text + mod)

        for context in contexts:
            fuzzed_prompts.append(input_text + context)

        # Conditional fuzzing
        if "error" in input_text.lower():
            fuzzed_prompts.append(input_text + " but with a different outcome")

        # Randomly shuffle words
        words = input_text.split()
        random.shuffle(words)
        fuzzed_prompts.append(" ".join(words))

        return fuzzed_prompts

    def analyze_fuzzing_results(self, results):
        """
        Analyze the fuzzing results to provide insights.
        """
        insights = {
            "total_prompts": len(results),
            "unique_responses": len(set(results)),
            "longest_response": max(results, key=len),
            "shortest_response": min(results, key=len)
        }
        return insights

    def register_routes(self):
        @self.bp.route('/default')
        def default():
            model_path = self._get_system_config_value('llm_path')
            if model_path and model_path != "":
                model, tokenizer, loader = self._load_model()
                input_text = str(self._get_system_config_value('ANALYSIS_TEXT'))
                self._fuzzing_results = self.fuzz_prompt(input_text, tokenizer, model)
                loader.unload()
                self.set_ready(True)
                insights = self.analyze_fuzzing_results(self._fuzzing_results)
            else:
                self.set_ready(False)
                insights = {}
            return self.render("prompt_fuzzing.html", model_path=model_path, fuzzing_results=self._fuzzing_results, insights=insights)

    def to_json(self):
        if not self._fuzzing_results:
            raise Exception("Fuzzing not complete")
        return {
            "plugin": self.name,
            "model_path": self._get_system_config_value('llm_path'),
            "fuzzing_results": self._fuzzing_results
        }
