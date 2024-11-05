# hugging_face_loader.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import threading
from oversight.utils.loader_base import LoaderBase

class HuggingFaceLoader(LoaderBase):
    # Class-level lock to ensure exclusivity across load and unload
    _class_lock = threading.Lock()

    def __init__(self, model_name, quantization=False):
        self.model_name = model_name
        self.quantization = quantization
        self.model = None
        self.tokenizer = None
        self._is_locked = False

    def load(self):
        """
        Loads the model and tokenizer in a thread-safe manner and keeps the lock
        until unload is called, ensuring no concurrent access.

        Returns:
            Tuple[AutoModelForCausalLM, AutoTokenizer]: The loaded model and tokenizer.
        """
        # Acquire the class-level lock before loading
        HuggingFaceLoader._class_lock.acquire()
        self._is_locked = True
        try:
            # Unload CUDA memory explicitly before loading the model
            self.unload(pre_load=True)  # Unload any previously loaded model if present
            torch.cuda.empty_cache()

            # Load model with or without quantization
            if self.quantization:
                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.bfloat16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type='nf4',
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=quant_config,
                    torch_dtype=torch.bfloat16,
                    device_map={"": "cuda:0"},  # Force all layers onto GPU
                    low_cpu_mem_usage=True  # Reduce CPU memory usage, if available
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.bfloat16,
                    device_map={"": "cuda:0"},  # Force all layers onto GPU
                    low_cpu_mem_usage=True
                )

            # Load tokenizer and move it to the GPU if necessary
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, padding_side="left")
            if self.tokenizer.pad_token_id is None:
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id or 0



        except Exception as e:
            # Release the lock if an exception occurs
            self._release_lock()
            raise e
        # Ensure the model is fully on GPU
        self.model.to("cuda:0")
        return self.model, self.tokenizer

    def unload(self, pre_load=False):
        """
        Unloads the model and tokenizer from memory to free up GPU/CPU resources.
        Releases the lock to allow subsequent loading.

        """
        # Delete the model and tokenizer to free up memory
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        self.model, self.tokenizer = None, None
        torch.cuda.empty_cache()

        # Release the lock after unloading is complete if not pre-loading
        if not pre_load:
            self._release_lock()

    def _release_lock(self):
        """
        Helper function to release the class-level lock safely.
        """
        if self._is_locked:
            HuggingFaceLoader._class_lock.release()
            self._is_locked = False
