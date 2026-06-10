"""
TLDR: Implementation of standard OpenAI CLIP.
Logic: Uses HuggingFace's transformers to load `openai/clip-vit-base-patch32`. 
Embeds text and images into a normalized vector space for semantic comparison.
"""
import warnings
# Suppress the harmless HuggingFace FutureWarnings to keep the terminal clean
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub.file_download")

from typing import List, Union
import torch
import numpy as np
from PIL import Image
from transformers import AutoProcessor, CLIPModel as HFClipModel
from .base import EmbeddingModel

class ClipModel(EmbeddingModel):
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", device: str = None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading {model_name} on {self.device}...")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = HFClipModel.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        if isinstance(text, str):
            text = [text]
        inputs = self.processor(text=text, return_tensors="pt", padding=True, truncation=True).to(self.device)
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
    model = ClipModel(device="cpu")
    img = Image.new('RGB', (224, 224), color = 'red')
    print("Text embedding shape:", model.embed_text("A red square").shape)
    print("Image embedding shape:", model.embed_image(img).shape)