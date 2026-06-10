# Project Report: b_roll_rag

## 1. Introduction and Purpose
Project b_roll_rag is a production-grade, containerized Python application designed for video scene understanding and temporal segmentation. It enables natural language querying (e.g., "taking off shirt") against video content, retrieving relevant cut sections using semantic search.

## 2. Technical and Architectural Breakdown
- **Temporal Segmentation**: `scenedetect` is used to divide videos into logical scenes.
- **Scene Representation**: Keyframes are extracted from scenes and embedded into a vector space.
- **Embedding Model**: `apple/MobileCLIP2-S2` is used for multimodal (text and image) encoding. The system uses an Object-Oriented architecture to support swapping this for other models (e.g., `xclip`, `siglip`).
- **Vector Search**: `FAISS` (Facebook AI Similarity Search) is used for fast, memory-efficient vector searching.
- **Video Slicing**: `ffmpeg` is used to cut the video based on the timestamps of the matched scene.

## 3. High-Level Flow
1. **Upload**: User uploads a video.
2. **Segmentation**: `scenedetect` identifies scenes and start/end timestamps.
3. **Extraction & Embedding**: For each scene, a representative keyframe is extracted, embedded via MobileCLIP, and inserted into a FAISS index along with the scene's timestamps.
4. **Query**: User submits a text query.
5. **Search**: The text is embedded and queried against the FAISS index.
6. **Result**: The top matching scene is identified, and `ffmpeg` extracts the corresponding clip for the user.

## 4. Current State
- [x] Initial design and architecture planning.
- [x] Directory structure setup.
- [ ] Docker environment setup.
- [ ] Core OOP implementation.

## 5. Next Steps
- Implement the base `EmbeddingModel` and `MobileCLIPModel`.
- Integrate `scenedetect` and `FAISS`.
