"""
TLDR: Multi-modal Semantic Search Engine.
Logic: Embeds text queries and searches across visual scenes and/or text transcripts 
using FAISS. It aggregates results based on the chosen mode ("scene", "transcript", or "mixed"), 
sorts them by semantic proximity (L2 distance), and rigorously deduplicates them to prevent 
temporal overlaps.
"""
from typing import Dict, Any, List
from b_roll_rag.models.base import EmbeddingModel
from b_roll_rag.core.video_processor import VideoProcessor

class SearchEngine:
    def __init__(self, model: EmbeddingModel, processor: VideoProcessor):
        """
        Initializes the SearchEngine with a configured model and an indexed VideoProcessor.
        """
        self.model = model
        self.processor = processor

    def _deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters out redundant results that occupy the same temporal space in the video.
        Keeps the highest-scoring (lowest L2 distance) segment.
        """
        deduped = []
        for res in results:
            start = res["scene"]["start_time"]
            end = res["scene"]["end_time"]
            
            # Check if this segment overlaps temporally with an approved segment FROM THE SAME VIDEO
            is_overlap = any(
                (start < approved["scene"]["end_time"] and 
                 end > approved["scene"]["start_time"] and 
                 res["scene"].get("video_path") == approved["scene"].get("video_path"))
                for approved in deduped
            )
            
            if not is_overlap:
                deduped.append(res)
                
        return deduped

    def search(self, query: str, mode: str = "mixed", top_k: int = 1, min_distance_threshold: float = 1.40) -> List[Dict[str, Any]]:
        """
        Executes a semantic search against the FAISS indices.
        Filters out individual items below the threshold. If zero items survive,
        returns an empty list to trigger Pexels fallback.
        """
        if mode not in ["scene", "transcript", "mixed"]:
            raise ValueError("Mode must be one of: 'scene', 'transcript', 'mixed'")

        query_embedding = self.model.embed_text(query)
        all_results = []

        # 1. Search Visual Scenes
        if mode in ["scene", "mixed"] and self.processor.scene_index is not None and self.processor.scene_index.ntotal > 0:
            search_k = min(self.processor.scene_index.ntotal, top_k * 3)
            distances, indices = self.processor.scene_index.search(query_embedding, search_k)
            for dist, idx in zip(distances[0], indices[0]):
                if idx != -1:
                    all_results.append({
                        "score": float(dist),
                        "scene": dict(self.processor.scene_metadata[idx])
                    })

        # 2. Search Transcript
        if mode in ["transcript", "mixed"] and self.processor.transcript_index is not None and self.processor.transcript_index.ntotal > 0:
            search_k = min(self.processor.transcript_index.ntotal, top_k * 3)
            distances, indices = self.processor.transcript_index.search(query_embedding, search_k)
            for dist, idx in zip(distances[0], indices[0]):
                if idx != -1:
                    all_results.append({
                        "score": float(dist),
                        "scene": dict(self.processor.transcript_metadata[idx])
                    })

        # Sort Descending (Highest Cosine Similarity = Best)
        all_results.sort(key=lambda x: x["score"], reverse=True)

        # --- NEW ELEMENT-BY-ELEMENT FILTER ---
        # Keep only the items that meet your real-world quality standard (>= 1.4)
        valid_results = [item for item in all_results if item["score"] >= min_distance_threshold]
        
        dropped_count = len(all_results) - len(valid_results)
        if dropped_count > 0:
            print(f"🧹 Filtered out {dropped_count} local match(es) falling below quality threshold ({min_distance_threshold}).")

        # If absolutely nothing local survived the quality filter, trigger Pexels fallback
        if not valid_results:
            print(f"❌ Zero local matches met the quality threshold. Triggering Pexels fallback...")
            return []
        # -------------------------------------

        # Deduplicate and slice only the surviving valid results
        deduped_results = self._deduplicate(valid_results)
        final_results = deduped_results[:top_k]

        # Apply padding and text cross-referencing
        for res in final_results:
            scene_info = res["scene"]
            
            if scene_info.get("type") == "transcript":
                padding = 2.0
                scene_info["start_time"] = max(0.0, scene_info["start_time"] - padding)
                scene_info["end_time"] = scene_info["end_time"] + padding

            if scene_info.get("type") == "scene":
                overlapping_text = []
                for t_meta in self.processor.transcript_metadata:
                    if (t_meta["start_time"] < scene_info["end_time"] and 
                        t_meta["end_time"] > scene_info["start_time"]):
                        overlapping_text.append(t_meta["text"])
                
                scene_info["text"] = " ".join(overlapping_text) if overlapping_text else "[No dialogue detected]"

        return final_results

if __name__ == "__main__":
    print("SearchEngine loaded. Instantiate with a valid EmbeddingModel and hydrated VideoProcessor.")








