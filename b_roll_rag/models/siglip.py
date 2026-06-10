"""
TLDR: Implementation of Google SigLIP.
Logic: Uses HuggingFace `AutoProcessor` and `AutoModel`. SigLIP computes pairwise similarities efficiently 
without a global softmax, often resulting in better performance on zero-shot tasks.
"""
from typing import List, Union
import torch
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModel
from .base import EmbeddingModel

class SigLipModel(EmbeddingModel):
    def __init__(self, model_name: str = "google/siglip-base-patch16-224", device: str = None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading {model_name} on {self.device}...")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        if isinstance(text, str):
            text = [text]
        # SigLIP requires specific padding strategies
        inputs = self.processor(text=text, return_tensors="pt", padding="max_length", truncation=True).to(self.device)
        with torch.no_grad():
            outputs = self.model.get_text_features(**inputs)
            embeddings = outputs / outputs.norm(dim=-1, keepdim=True)
        return embeddings.cpu().numpy()

    def embed_image(self, images: Union[Image.Image, List[Image.Image]]) -> np.ndarray:
        if not isinstance(images, list):
            images = [images]
        inputs = self.processor(images=images, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)
            embeddings = outputs / outputs.norm(dim=-1, keepdim=True)
        return embeddings.cpu().numpy()

if __name__ == "__main__":
    model = SigLipModel(device="cpu")
    img = Image.new('RGB', (224, 224), color = 'green')
    print("Text embedding shape:", model.embed_text("A green square").shape)
    print("Image embedding shape:", model.embed_image(img).shape)