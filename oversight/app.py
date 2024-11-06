# app.py
from flask import Flask, render_template, request, jsonify, session, send_file
from oversight.config import Config
from oversight.utils.session_state import SessionState  # Updated to relative import
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, logging as hf_logging
import torch
import os
import json
import importlib
import inspect
from oversight.utils import PluginBase  
from datetime import datetime
import oversight.utils.loader_runner as loader_runner
import webbrowser
from threading import Timer


# Suppress unnecessary warnings
hf_logging.set_verbosity_error()

app = Flask(
    __name__,
    template_folder='templates',  # Specify the templates folder
    static_folder='static'        # Specify the static folder
)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY  # Ensure secret key is set
app.config["PLUGIN_FOLDER"] = os.path.join(app.root_path, "plugins")  # Add this line

# Reset the session state JSON if the debug flag is set
if app.config['DEBUG']:
    with open(Config.SESSION_STATE_FILE, 'w') as f:
        json.dump({}, f)

session_state = SessionState(Config.SESSION_STATE_FILE)
app.config['session_state'] = session_state  # Add this line

def load_plugins(app, session_state):
    plugin_folder = Config.PLUGIN_FOLDER
    print("Loading plugins from:", plugin_folder)
    plugins_with_priority = []
    base_module = plugin_folder
    for root, dirs, files in os.walk(plugin_folder):
        for file in files:
            if file.endswith(".py"):
                rel_path = os.path.relpath(os.path.join(root, file), plugin_folder)
                module_name = os.path.splitext(rel_path)[0].replace(os.sep, '.')
                full_module_name = f"{base_module}.{module_name}"
                print("Loading plugin:", full_module_name)
                module = importlib.import_module(full_module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj is not PluginBase:
                        plugin_instance = obj(app, session_state)
                        plugin_config = session_state.get_plugin_config(plugin_instance.bp.name)
                        if not plugin_config.get("hidden", False):
                            priority = plugin_config.get("priority", float('inf'))
                            plugins_with_priority.append((priority, plugin_instance))
    # Sort plugins by priority
    plugins_with_priority.sort(key=lambda x: x[0])
    plugins = []
    for priority, plugin_instance in plugins_with_priority:
        plugins.append(plugin_instance)
        app.register_blueprint(plugin_instance.bp)  # Register in priority order
        print(f"Registered plugin: {plugin_instance.bp.name}, priority: {priority}, template folder: {plugin_instance.template_folder}")
    return plugins


# Automatically load all plugins in the plugins folder
plugins = load_plugins(app, session_state)

# Print loaded plugins
print("Loaded plugins:", [plugin.__class__.__name__ for plugin in plugins])

@app.route('/check_plugin')
def check_plugin():
    plugin_downloaded = session.get('plugin_downloaded', False)
    return jsonify({'plugin_downloaded': plugin_downloaded})

@app.route('/download_plugin', methods=['POST'])
def download_plugin():
    data = request.get_json()
    llm_path = data.get('llm_path')
    if (llm_path != ""):
        loader = loader_runner.run_loader(loader_name="HuggingFaceLoader", model_name=llm_path)
        model, tokenizer = loader.load()
        # Optionally, save the model and tokenizer locally
        save_path = llm_path
        #os.makedirs(save_path, exist_ok=True)
        #model.save_pretrained(save_path)
        #tokenizer.save_pretrained(save_path)

        # Clean up to free memory
        del model
        del tokenizer
        torch.cuda.empty_cache()
        loader.unload()
        # Update session state with the llm_path
        session_state.state['llm_path'] = save_path  # Use the local save path

        session_state.save_state()

        # Set session flag to indicate plugin has been downloaded
        session['plugin_downloaded'] = True
        session.modified = True
        return jsonify({'status': 'success'}), 200

    else:
        return jsonify({'status': 'error', 'message': 'No LLM path provided'}), 400

@app.route('/reset_state', methods=['POST'])
def reset_state():
    try:
        # Reset the session state JSON
        with open(Config.SESSION_STATE_FILE, 'w') as f:
            json.dump({}, f)
        
        # Clear session data
        session.clear()
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/check_report_ready', methods=['GET'])
def check_report_ready():
    try:
        all_ready = all(plugin.is_ready() for plugin in plugins)
        return jsonify({'ready': all_ready}), 200
    except Exception as e:
        return jsonify({'ready': False, 'error': str(e)}), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        # Check if all plugins are ready
        if not all(plugin.is_ready() for plugin in plugins):
            return jsonify({
                'status': 'error',
                'message': 'Some plugins are still processing. Please wait until all analyses are complete.'
            }), 400
            
        data = request.get_json()
        report_name = data.get('report_name', f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        # Collect data from all plugins
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'plugins': {}
        }
        
        for plugin in plugins:
            try:
                plugin_data = plugin.to_json()
                report_data['plugins'][plugin.name] = plugin_data
            except Exception as e:
                report_data['plugins'][plugin.name] = {
                    'error': str(e)
                }
        
        # Ensure the reports directory exists
        reports_dir = os.path.join(app.root_path, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Save the report
        report_path = os.path.join(reports_dir, f'{report_name}.json')
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Send the file
        return send_file(
            report_path,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'{report_name}.json'
        )
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/")
def home():
    plugins_by_subheading = {}
    plugins_without_subheading = []
    for plugin in plugins:
        plugin_name = plugin.bp.name
        plugin_config = session_state.get_plugin_config(plugin_name)
        plugin_size = plugin_config.get("size", "small")
        plugin_endpoint = f"{plugin.bp.name}.default"
        plugin_priority = plugin_config.get("priority", float('inf'))
        plugin_card = {
            "name": plugin_name,
            "endpoint": plugin_endpoint,
            "size": plugin_size,
            "data": plugin_config.get("data", {}),
            "config": plugin_config,
            "priority": plugin_priority,
        }
        subheading = plugin_config.get("subheading")
        if (subheading):
            if subheading not in plugins_by_subheading:
                plugins_by_subheading[subheading] = []
            plugins_by_subheading[subheading].append(plugin_card)
        else:
            plugins_without_subheading.append(plugin_card)
    # Sort plugins within each subheading by priority
    for subheading in plugins_by_subheading:
        plugins_by_subheading[subheading].sort(key=lambda x: x['priority'])
    # Sort subheadings by the lowest priority of their plugins
    sorted_subheadings = sorted(
        plugins_by_subheading.items(),
        key=lambda x: min(plugin['priority'] for plugin in x[1])
    )
    # Sort plugins without subheading by priority
    plugins_without_subheading.sort(key=lambda x: x['priority'])
    return render_template(
        "index.html",
        plugins_by_subheading=sorted_subheadings,
        plugins_without_subheading=plugins_without_subheading
    )

if __name__ == "__main__":
    app.run(debug=True)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

def main():
    Timer(1, open_browser).start()  # Delay to allow the server to start before opening the browser
    app.run(host='127.0.0.1', port=5000, debug=True)
