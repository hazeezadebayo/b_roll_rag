from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import shutil
import os
import uuid

from b_roll_rag.schema.api_models import QueryRequest, QueryResult
from b_roll_rag.models import get_model
from b_roll_rag.core.video_processor import VideoProcessor
from b_roll_rag.core.search_engine import SearchEngine
from b_roll_rag.utils.video_cutter import VideoCutter
from b_roll_rag.utils.ugc_avatar_studio_fallback import generate_fallback_video

app = FastAPI(title="b_roll_rag Video Semantic Search")

# Global instances (in a real app, use proper dependency injection or lifespan events)
model = None
processor = None
search_engine = None
UPLOAD_DIR = "/tmp/b_roll_rag_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
def startup_event():
    global model, processor, search_engine
    print("Initializing models...")
    model = get_model("clip")
    processor = VideoProcessor(model)
    search_engine = SearchEngine(model, processor)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Uploads a video, runs scene detection, and indexes it.
    """
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # We index it globally for simplicity
        processor.process_video(file_path)
        # Keep track of the current video path globally (for demo purposes)
        app.state.current_video = file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"message": "Video processed and indexed successfully."}

@app.post("/search", response_model=list[QueryResult])
async def search_video(req: QueryRequest):
    """
    Searches the indexed video for the given text query and returns the cut clip.
    """
    # Check if index exists and has items
    if search_engine is None or processor.scene_index is None or processor.scene_index.ntotal == 0:
        results = []
    else:
        results = search_engine.search(req.query, top_k=req.top_k)
        
    # Trigger fallback if no video is indexed or search yields 0 results
    if not results:
        # Check if Pexels API key is present
        api_key = os.environ.get("PEXELS_API_KEY")
        if api_key:
            from b_roll_rag.utils.broll_fetcher import BRollFetcher
            broll_dir = os.path.join(UPLOAD_DIR, "broll")
            if os.path.exists(broll_dir):
                shutil.rmtree(broll_dir)
            
            # Fetch a few videos to process and rank
            fetched_videos = BRollFetcher.fetch_videos(query=req.query, max_videos=3, orientation="landscape", output_dir=broll_dir)
            if fetched_videos:
                processor.process_broll_directory(broll_dir)
                results = search_engine.search(req.query, top_k=req.top_k)
                
        # Avatar fallback if Pexels fails, key not provided, or still no results
        if not results:
            fallback_path = os.path.join(UPLOAD_DIR, f"fallback_{uuid.uuid4()}.mp4")
            generate_fallback_video(
                character="male1",
                speech_text=f"I couldn't find exactly what you were looking for, but here is a presentation about {req.query}",
                output=fallback_path)
                
            return [{"score": 0.0, "scene": {"scene_idx": -1, "start_time": 0.0, "end_time": 0.0}, "video_url": fallback_path}]
    
    response = []
    for res in results:
        scene = res["scene"]
        start_time = scene["start_time"]
        end_time = scene["end_time"]
        
        output_path = os.path.join(UPLOAD_DIR, f"cut_{uuid.uuid4()}.mp4")
        
        try:
            source_video = scene.get("video_path", getattr(app.state, "current_video", None))
            if not source_video:
                raise ValueError("No source video found for this scene.")
                
            VideoCutter.cut_video(
                source_video, 
                start_time, 
                end_time, 
                output_path
            )
            res["video_url"] = output_path
        except Exception as e:
            print(f"Error cutting video: {e}")
            res["video_url"] = None
            
        response.append(res)
        
    return response

@app.get("/download")
async def download_clip(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="video/mp4")
