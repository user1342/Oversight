import os
import sys
import importlib
from oversight.utils.loader_base import LoaderBase
from oversight.config import Config

def find_loaders():
    loaders = []
    loaders_dir = Config.LOADER_FOLDER

    # Add the loader directory to sys.path if not already present
    if loaders_dir not in sys.path:
        sys.path.insert(0, loaders_dir)

    # Iterate over Python files in the loaders directory
    for filename in os.listdir(loaders_dir):
        if filename.endswith('.py') and filename not in ['__init__.py', 'loader_base.py', 'loader_runner.py']:
            module_name = filename[:-3]
            module_path = os.path.join(loaders_dir, filename)

            # Load the module from the file path
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find and add valid loader classes
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, LoaderBase) and obj is not LoaderBase:
                    loaders.append(obj)
    return loaders

def run_loader(loader_name, *args, **kwargs):
    loaders = find_loaders()
    for loader in loaders:
        name = loader.__name__
        if name == loader_name:
            instance = loader(*args, **kwargs)
            return instance
    raise ValueError(f"No loader found with the name {loader_name}")
