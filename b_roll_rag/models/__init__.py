"""
TLDR: Factory pattern for model instantiation.
Logic: Provides a clean `get_model` interface to instantiate the correct model class based on a string literal.
"""
from .clip import ClipModel
from .siglip import SigLipModel
from .xclip import XClipModel
from .mobile_clip import MobileCLIPModel

def get_model(model_name: str, device: str = None):
    model_map = {
        "clip": ClipModel,
        "siglip": SigLipModel,
        "xclip": XClipModel,
        "mobileclip": MobileCLIPModel
    }
    if model_name.lower() not in model_map:
        raise ValueError(f"Model '{model_name}' not supported. Choose from {list(model_map.keys())}")
    return model_map[model_name.lower()](device=device)

if __name__ == "__main__":
    model = get_model("clip", "cpu")
    print(f"Successfully loaded model factory: {type(model)}")