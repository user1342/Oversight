<p align="center">
    <img width=100% src="logo.png">
  </a>
</p>
<p align="center"> 🤖 LLM Disassembler ⚔️ </p>


Welcome to **Oversight**! This tool allows reverse engineering and in-depth analysis of large language models (LLMs). Oversight provides a suite of utilities to inspect LLMs for vulnerabilities and behavioral patterns, enabling adversarial testing, prompt fuzzing, response evasion, and more. Designed for researchers, developers, and enthusiasts, Oversight is modular and extensible via plugins.

## Features ✨
- **Plugin-Based Architecture**: Extend Oversight’s capabilities with custom plugins.
- **Comprehensive Analysis**: Supports adversarial testing, response evasion, prompt fuzzing, etc.
- **User-Friendly Interface**: Intuitive web interface powered by Flask.
- **Detailed Reports**: Generate and download comprehensive reports.

<p align="center">
    <img width=50% src="demo.gif">
  </a>
</p>

## Installation 🛠️

### Requirements
- **Python 3.8+**
- **CUDA (for GPU acceleration)**: Ensure that CUDA is installed and configured on your system.
- **Python Libraries**:
  - Flask
  - Transformers
  - Torch

### Steps

1. **Clone the Repository**:
   ```
   git clone https://github.com/your-repo/oversight.git
   cd oversight
   ```
Install Dependencies: Install the required libraries using pip:

```
pip install flask transformers torch
```
Configure CUDA: Ensure your system’s CUDA configuration matches your GPU. Install CUDA if you haven't already:

## Check CUDA version
```
nvcc --version
```
Run the Application: Start the Flask app from the app.py file:

```
python app.py
```
Access the Web Interface: Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

# Usage
Once the app is running, you can navigate through different analysis modules in the web interface. Each module (e.g., Adversarial Testing, Prompt Fuzzing) performs specific tests on the loaded LLM and displays insights in a user-friendly format.

# Creating Your Own Plugin 🧩
Creating a plugin in Oversight is straightforward. Follow these steps to add your custom plugin:

## Step 1: Create a New Plugin File
Navigate to the plugins directory and create a new folder for your plugin. Inside this folder, create a Python file (e.g., my_plugin.py).

## Step 2: Define Your Plugin Class
Your plugin class should inherit from PluginBase. Here’s a basic template:

```
from oversight.utils.plugin_base import PluginBase
from flask import jsonify

class MyPlugin(PluginBase):
    def __init__(self, app, session_state):
        config = self._get_config()
        super().__init__(app, session_state, name=config['name'], import_name=__name__, url_prefix=f"/{config['name']}", template_folder='templates')

    def register_routes(self):
        @self.bp.route('/default')
        def default():
            return jsonify({"message": "Hello from MyPlugin!"})

    def to_json(self):
        return {"plugin": self.name, "data": "example_data"}
```

## Step 3: Create a Template
Inside your plugin folder, create a templates folder and add an HTML file (e.g., my_plugin.html). This file defines the front-end interface for your plugin.

## Step 4: Update Configuration
Ensure your plugin’s configuration is added to the config.json file in your plugin folder. The configuration file should include necessary settings like the plugin name and loader. Example:

```
{
    "name": "My Custom Plugin",
    "size": "small",
    "data": "This plugin demonstrates a custom feature.",
    "hidden": false,
    "loader": "HuggingFaceLoader",
    "priority": 5
}
```

## Step 5: Register Your Plugin
Your plugin will be automatically discovered by Oversight. Just restart the application, and your plugin should be ready to use!

# Contributing 🤝
We welcome contributions! Feel free to fork the repository, make changes, and submit a pull request. Contributions can include bug fixes, new features, or improvements to documentation.
