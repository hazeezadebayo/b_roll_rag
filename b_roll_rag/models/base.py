"""
TLDR: Abstract base class for the embedding models.
Logic: Defines the contract (interface) that all embedding models (CLIP, SigLIP, etc.) must follow. 
It ensures that any swapped-in model will reliably process text and images into numpy arrays.
"""
from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np
from PIL import Image

class EmbeddingModel(ABC):
    """
    Abstract base class for all embedding models.
    Ensures that any model can be swapped in seamlessly.
    """
    @abstractmethod
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Embeds one or more text queries into vector space.
        Returns a numpy array of shape (N, embedding_dim).
        """
        pass

    @abstractmethod
    def embed_image(self, images: Union[Image.Image, List[Image.Image]]) -> np.ndarray:
        """
        Embeds one or more images into vector space.
        Returns a numpy array of shape (N, embedding_dim).
        """
        pass

if __name__ == "__main__":
    print("This is an abstract base class and cannot be instantiated directly.")