import importlib.util
import sys
from pathlib import Path
from typing import Callable

def load_callback(callback_module: str) -> Callable:
    try:
        module_path, func_name = callback_module.split(":")
    except ValueError:
        raise ValueError("callback_module must be in the format '/path/to/module.py:function_name'")
    
    module_path = Path(module_path).resolve()
    if not module_path.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")

    module_name = f"_dynamic_module_{module_path.stem}"

    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore

    if not hasattr(module, func_name):
        raise AttributeError(f"Module '{module_path}' has no function '{func_name}'")

    func = getattr(module, func_name)
    if not callable(func):
        raise TypeError(f"'{func_name}' in module '{module_path}' is not callable")
    
    return func