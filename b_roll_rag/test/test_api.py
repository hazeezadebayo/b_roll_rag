import argparse
import os
import shutil
import sys
from fastapi.testclient import TestClient

# Add /app to PYTHONPATH to avoid import issues when running inside container
sys.path.append("/app")

from b_roll_rag.api.main import app, UPLOAD_DIR
import b_roll_rag.api.main as api_main
from b_roll_rag.models import get_model
from b_roll_rag.core.video_processor import VideoProcessor
from b_roll_rag.core.search_engine import SearchEngine

def setup_app(args):
    # Re-initialize models if a different model is requested
    print(f"Initializing app with model {args.model}...")
    api_main.model = get_model(args.model)
    api_main.processor = VideoProcessor(api_main.model)
    api_main.search_engine = SearchEngine(api_main.model, api_main.processor)

def test_upload_and_search(args):
    """
    Test Case S1: Orchestrate video upload and then search.
    """
    print(f"\n--- S1: Upload Video ({args.video}) and Search ('{args.query}') ---")
    with TestClient(app) as client:
        dummy_video_path = f"/app/b_roll_rag/data/input/{args.video}" 
        
        if args.video != "None" and os.path.exists(dummy_video_path):
            with open(dummy_video_path, "rb") as f:
                upload_res = client.post("/upload", files={"file": (args.video, f, "video/mp4")})
            
            assert upload_res.status_code == 200, f"Expected 200, got {upload_res.status_code}"
        else:
            print(f"Skipping actual upload, video {dummy_video_path} not found or None.")
        
        search_res = client.post("/search", json={"query": args.query, "top_k": args.top_k})
        assert search_res.status_code == 200
        
        data = search_res.json()
        assert len(data) > 0, "Expected search results"
        
        result = data[0]
        assert result["scene"]["scene_idx"] != -1, "Expected genuine match, not a fallback"
        assert result["video_url"].endswith(".mp4")
        assert os.path.exists(result["video_url"]), "Output video clip does not exist!"

def test_api_pexels_fallback_no_video(args):
    """
    Test Case S2: Search without any video indexed, with Pexels API key provided.
    """
    print(f"\n--- S2: Search without indexed video (Pexels fallback) ('{args.query}') ---")
    
    api_key = os.environ.get("PEXELS_API_KEY")
    assert api_key, "PEXELS_API_KEY environment variable must be set to run Scenario S2."
    
    with TestClient(app) as client:
        api_main.processor.scene_index = None
        
        response = client.post("/search", json={"query": args.query, "top_k": args.top_k})
        assert response.status_code == 200, f"Expected 200, got {response.status_code} - {response.text}"
        
        data = response.json()
        assert len(data) > 0, "Expected at least 1 result (the fallback)"
        fallback_result = data[0]
        
        print("Pexels Fallback generated at:", fallback_result["video_url"])
        assert fallback_result["scene"]["scene_idx"] != -1, "Expected a genuine scene match from Pexels, not an avatar fallback"
        assert "cut_" in fallback_result["video_url"]
        assert os.path.exists(fallback_result["video_url"]), "Fallback video file does not exist!"

def test_api_avatar_fallback_no_video(args):
    """
    Test Case S3: Search without any video indexed, WITHOUT Pexels API key provided.
    """
    print(f"\n--- S3: Search without indexed video (Avatar fallback) ('{args.query}') ---")
    with TestClient(app) as client:
        api_main.processor.scene_index = None
        
        # Remove pexels api key for this test
        if "PEXELS_API_KEY" in os.environ:
            del os.environ["PEXELS_API_KEY"]
            
        response = client.post("/search", json={"query": args.query, "top_k": args.top_k})
        assert response.status_code == 200, f"Expected 200, got {response.status_code} - {response.text}"
        
        data = response.json()
        assert len(data) > 0, "Expected at least 1 result (the fallback)"
        fallback_result = data[0]
        
        print("Avatar Fallback generated at:", fallback_result["video_url"])
        assert fallback_result["scene"]["scene_idx"] == -1
        assert "fallback_" in fallback_result["video_url"]
        assert os.path.exists(fallback_result["video_url"]), "Fallback video file does not exist!"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test b_roll_rag API")
    parser.add_argument("--model", type=str, default="clip")
    parser.add_argument("--top_k", type=int, default=3)
    parser.add_argument("--frames_per_scene", type=int, default=1)
    parser.add_argument("--transcript", type=str, default=None)
    parser.add_argument("--mode", type=str, default="mixed")
    parser.add_argument("--aspect_ratio", type=str, default="original")
    parser.add_argument("--video", type=str, default="t12s_vid.mp4")
    parser.add_argument("--query", type=str, default="person doing pushup")
    parser.add_argument("--scenario", type=str, default="ALL", choices=["S1", "S2", "S3", "ALL"])
    
    args = parser.parse_args()

    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    setup_app(args)
    
    if args.scenario in ["S1", "ALL"]:
        test_upload_and_search(args)
    if args.scenario in ["S2", "ALL"]:
        test_api_pexels_fallback_no_video(args)
    if args.scenario in ["S3", "ALL"]:
        test_api_avatar_fallback_no_video(args)
        
    print("\nSelected API tests completed successfully!")
