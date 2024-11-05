import os
import importlib
from oversight.utils.loader_base import LoaderBase
from oversight.config import Config

def find_loaders():
    loaders = []
    loaders_dir = Config.LOADER_FOLDER
    for filename in os.listdir(loaders_dir):
        if filename.endswith('.py') and filename not in ['__init__.py', 'loader_base.py', 'loader_runner.py']:
            module_name = filename[:-3]
            module = importlib.import_module(f'loaders.{module_name}')
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
