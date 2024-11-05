from abc import ABC

class LoaderBase(ABC):
    def __init__(self):
        pass
    
    def load(self):
        raise NotImplementedError("load method must be implemented by subclasses")
    
    def unload(self):
        raise NotImplementedError("load method must be implemented by subclasses")
