"""
TLDR: Parses videos and corresponding transcripts into searchable FAISS indices.
Logic: 
1. Uses `scenedetect` to slice videos into physical scenes and extracts keyframes.
2. Embeds the keyframes via the given EmbeddingModel into a visual FAISS index.
3. If provided, parses a text transcript, embeds the segments, and creates a parallel semantic FAISS index.
"""
import os
# CRITICAL: Suppress noisy FFmpeg h264 decoder warnings in the terminal
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "quiet"

import faiss
from typing import List, Dict, Any, Optional
from PIL import Image
import cv2

# scenedetect imports (Modern API to avoid VideoManager deprecation)
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector

from b_roll_rag.models.base import EmbeddingModel
try:
    from b_roll_rag.utils.transcript_parser import TranscriptParser
except ImportError:
    class TranscriptParser:
        @staticmethod
        def parse(path): return []

class VideoProcessor:
    def __init__(self, model: EmbeddingModel):
        self.model = model
        self.scene_index = None
        self.scene_metadata: List[Dict[str, Any]] = []
        self.transcript_index = None
        self.transcript_metadata: List[Dict[str, Any]] = []

    def _extract_keyframe(self, video_path: str, timestamp_sec: float) -> Optional[Image.Image]:
        """
        Extracts a specific frame at a given timestamp using OpenCV.
        We intentionally open and close the capture object here. While slower, 
        it guarantees absolute frame accuracy for H.264, ensuring perfect RAG embeddings.
        """
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_sec * 1000)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None
            
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)

    def process_video(self, video_path: str, frames_per_scene: int = 1, transcript_path: Optional[str] = None, video_type: str = "scene"):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print(f"Processing video: {video_path} (Frames per scene: {frames_per_scene})")
        
        # 1. Use modern open_video API (Removes deprecation warning)
        video = open_video(video_path)
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())
        
        # Optional: auto_downscale speeds up the scene detection math significantly
        scene_manager.auto_downscale = True 
        
        scene_manager.detect_scenes(video)
        scene_list = scene_manager.get_scene_list()
        
        if len(scene_list) == 0:
            try:
                duration = video.duration.get_seconds()
                if duration > 0:
                    class MockTimecode:
                        def __init__(self, seconds):
                            self.seconds = seconds
                        def get_seconds(self):
                            return self.seconds
                    scene_list = [(MockTimecode(0.0), MockTimecode(duration))]
            except Exception as e:
                print(f"Error getting video duration fallback: {e}")
        
        print(f"Detected {len(scene_list)} physical scenes. Extracting and embedding...")
        
        images, scene_meta = [], []
        
        # 2. Extract keyframes and build metadata
        for idx, scene in enumerate(scene_list):
            start_time = scene[0].get_seconds()
            end_time = scene[1].get_seconds()
            duration = end_time - start_time
            
            for i in range(1, frames_per_scene + 1):
                fraction = i / (frames_per_scene + 1)
                t_sec = start_time + (duration * fraction)
                
                img = self._extract_keyframe(video_path, t_sec)
                if img is not None:
                    images.append(img)
                    scene_meta.append({
                        "scene_idx": idx,
                        "start_time": start_time,
                        "end_time": end_time,
                        "type": video_type,
                        "video_path": video_path
                    })
        
        # 3. Embed Visual Data (Using L2 distance as in your working version)
        if images:
            embeddings = self.model.embed_image(images)
            if self.scene_index is None:
                dim = embeddings.shape[1]
                self.scene_index = faiss.IndexFlatL2(dim)
            
            self.scene_index.add(embeddings)
            self.scene_metadata.extend(scene_meta)
            print("Video visual scenes processed and added to FAISS index.")
        else:
            print("Warning: No visual scenes found or extracted.")

        # 4. Process Transcript
        if transcript_path and os.path.exists(transcript_path):
            print(f"Processing transcript file: {transcript_path}")
            segments = TranscriptParser.parse(transcript_path)
            
            if segments:
                texts = [seg["text"] for seg in segments]
                text_embeddings = self.model.embed_text(texts)
                
                if self.transcript_index is None:
                    dim = text_embeddings.shape[1]
                    self.transcript_index = faiss.IndexFlatL2(dim)
                
                self.transcript_index.add(text_embeddings)
                
                for seg in segments:
                    seg["type"] = "transcript"
                    if "scene_idx" not in seg:
                        seg["scene_idx"] = -1 
                        
                self.transcript_metadata.extend(segments)
                print("Transcript textual data processed and added to FAISS index.")
            else:
                print("Warning: No valid segments extracted from the transcript file.")
                
    def process_broll_directory(self, broll_dir: str, frames_per_scene: int = 1):
        if not os.path.exists(broll_dir):
            return
            
        print(f"Processing B-roll directory: {broll_dir}")
        for f in os.listdir(broll_dir):
            if f.endswith(".mp4"):
                video_path = os.path.join(broll_dir, f)
                self.process_video(video_path, frames_per_scene=frames_per_scene, video_type="broll")