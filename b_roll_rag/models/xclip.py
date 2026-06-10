"""
TLDR: Implementation of Microsoft X-CLIP for frames.
Logic: X-CLIP is inherently a video model. To process single frames for scene detection, 
we artificially expand the image tensor to simulate a 1-frame video payload.
"""
from typing import List, Union
import torch
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModel
from .base import EmbeddingModel

class XClipModel(EmbeddingModel):
    def __init__(self, model_name: str = "microsoft/xclip-base-patch32", device: str = None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading {model_name} on {self.device}...")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
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
        
        embeddings_list = []
        with torch.no_grad():
            for img in images:
                # X-CLIP processor expects videos (list of frames). We pass a 1-frame "video".
                inputs = self.processor(videos=[img], return_tensors="pt").to(self.device)
                outputs = self.model.get_video_features(**inputs)
                emb = outputs / outputs.norm(dim=-1, keepdim=True)
                embeddings_list.append(emb)
                
        final_embeddings = torch.cat(embeddings_list, dim=0)
        return final_embeddings.cpu().numpy()

if __name__ == "__main__":
    model = XClipModel(device="cpu")
    img = Image.new('RGB', (224, 224), color = 'yellow')
    print("Text embedding shape:", model.embed_text("A yellow square").shape)
    print("Image embedding shape:", model.embed_image([img, img]).shape)