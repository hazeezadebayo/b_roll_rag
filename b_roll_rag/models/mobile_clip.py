"""
TLDR: Implementation of Apple MobileCLIP.
Logic: Relies on `open_clip_torch` since HuggingFace's native `transformers` doesn't fully support MobileCLIP natively.
Provides fast and lightweight embedding ideal for edge devices or rapid processing.
"""
from typing import List, Union
import torch
import numpy as np
from PIL import Image
from .base import EmbeddingModel

class MobileCLIPModel(EmbeddingModel):
    def __init__(self, model_name: str = "MobileCLIP-S2", device: str = None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading {model_name} via open_clip on {self.device}...")
        try:
            import open_clip
        except ImportError:
            raise ImportError("MobileCLIP requires 'open_clip_torch'. Run `pip install open_clip_torch`.")
        
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('MobileCLIP-S2', pretrained='datacompxl')
        self.model = self.model.to(self.device)
        self.model.eval()
        self.tokenizer = open_clip.get_tokenizer('MobileCLIP-S2')

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        if isinstance(text, str):
            text = [text]
        inputs = self.tokenizer(text).to(self.device)
        with torch.no_grad():
            embeddings = self.model.encode_text(inputs)
            embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        return embeddings.cpu().numpy()

    def embed_image(self, images: Union[Image.Image, List[Image.Image]]) -> np.ndarray:
        if not isinstance(images, list):
            images = [images]
        inputs = torch.stack([self.preprocess(img) for img in images]).to(self.device)
        with torch.no_grad():
            embeddings = self.model.encode_image(inputs)
            embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        return embeddings.cpu().numpy()

if __name__ == "__main__":
    try:
        model = MobileCLIPModel(device="cpu")
        img = Image.new('RGB', (224, 224), color = 'blue')
        print("Text embedding shape:", model.embed_text("A blue square").shape)
        print("Image embedding shape:", model.embed_image(img).shape)
    except ImportError as e:
        print(e)