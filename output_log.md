### Command:
`find . -maxdepth 4 -not -path '*/.*'`

### Output:
```
.
./project_report.md
./docker
./docker/requirements.txt
./docker/Dockerfile
./run_ugc.sh
./ugc
./ugc/utils
./ugc/utils/broll_fetcher.py
./ugc/utils/ugc_avatar_studio_fallback.py
./ugc/utils/__pycache__
./ugc/utils/__pycache__/ugc_avatar_studio_fallback.cpython-310.pyc
./ugc/utils/__pycache__/transcript_parser.cpython-310.pyc
./ugc/utils/__pycache__/video_cutter.cpython-310.pyc
./ugc/utils/__pycache__/keyword_extractor.cpython-310.pyc
./ugc/utils/__pycache__/broll_fetcher.cpython-310.pyc
./ugc/utils/keyword_extractor.py
./ugc/utils/transcript_parser.py
./ugc/utils/video_cutter.py
./ugc/models
./ugc/models/siglip.py
./ugc/models/mobile_clip.py
./ugc/models/__init__.py
./ugc/models/__pycache__
./ugc/models/__pycache__/siglip.cpython-310.pyc
./ugc/models/__pycache__/base.cpython-310.pyc
./ugc/models/__pycache__/__init__.cpython-310.pyc
./ugc/models/__pycache__/mobile_clip.cpython-310.pyc
./ugc/models/__pycache__/xclip.cpython-310.pyc
./ugc/models/__pycache__/clip.cpython-310.pyc
./ugc/models/xclip.py
./ugc/models/clip.py
./ugc/models/base.py
./ugc/test
./ugc/test/test_api.py
./ugc/test/__pycache__
./ugc/test/__pycache__/test_fallback_avatar.cpython-310.pyc
./ugc/api
./ugc/api/main.py
./ugc/api/__pycache__
./ugc/api/__pycache__/main.cpython-310.pyc
./ugc/schema
./ugc/schema/api_models.py
./ugc/schema/__pycache__
./ugc/schema/__pycache__/api_models.cpython-310.pyc
./ugc/core
./ugc/core/search_engine.py
./ugc/core/__pycache__
./ugc/core/__pycache__/video_processor.cpython-310.pyc
./ugc/core/__pycache__/search_engine.cpython-310.pyc
./ugc/core/video_processor.py
./ugc/data
./ugc/data/didl_vid.mp4
./ugc/data/speed_test.gif
./ugc/data/dummy.srt
./ugc/data/t12s_vid.mp4
./ugc/data/avatar_studio.gif
./ugc/data/female_avatar.gif
./sample.env
./README.md
```

### Command:
`grep -rnwi "ugc" --exclude-dir={.hf_cache,__pycache__,data} .`

### Output:
```
./project_report.md:1:# Project Report: UGC
./project_report.md:4:Project UGC is a production-grade, containerized Python application designed for video scene understanding and temporal segmentation. It enables natural language querying (e.g., "taking off shirt") against video content, retrieving relevant cut sections using semantic search.
./docker/Dockerfile:24:CMD ["uvicorn", "ugc.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
./run_ugc.sh:10:PROJECT_DIR="/home/azeez/ws/dev_env/py_code/projects/ugc"
./run_ugc.sh:11:DATA_DIR="$PROJECT_DIR/ugc/data"
./run_ugc.sh:15:    echo "UGC Orchestration CLI"
./run_ugc.sh:27:    echo "Building ugc-app docker image..."
./run_ugc.sh:28:    cd "$PROJECT_DIR/docker" && docker build -t ugc-app .
./run_ugc.sh:63:        ugc-app \
./run_ugc.sh:64:        python ugc/test/test_api.py \
./run_ugc.sh:84:    echo "Killing running ugc-app containers..."
./run_ugc.sh:85:    container_ids=$(docker ps -q --filter ancestor=ugc-app)
./run_ugc.sh:90:        echo "No running ugc-app containers found."
./ugc/utils/broll_fetcher.py:9:from ugc.utils.keyword_extractor import KeywordExtractor
./ugc/utils/broll_fetcher.py:60:    def fetch_videos(query: str, max_videos: int = 5, orientation: str = "portrait", output_dir: str = "/app/ugc/data/broll") -> List[str]:
./ugc/utils/ugc_avatar_studio_fallback.py:311:def generate_fallback_video(character="male1", duration=2.5, fps=30, output="ugc/data/avatar_studio.mp4", speech=False, speech_text=None):
./ugc/utils/ugc_avatar_studio_fallback.py:386:    parser.add_argument("--output", default="ugc/data/avatar_studio.mp4")
./ugc/test/test_api.py:10:from ugc.api.main import app, UPLOAD_DIR
./ugc/test/test_api.py:11:import ugc.api.main as api_main
./ugc/test/test_api.py:12:from ugc.models import get_model
./ugc/test/test_api.py:13:from ugc.core.video_processor import VideoProcessor
./ugc/test/test_api.py:14:from ugc.core.search_engine import SearchEngine
./ugc/test/test_api.py:29:        dummy_video_path = f"/app/ugc/data/{args.video}" 
./ugc/test/test_api.py:97:    parser = argparse.ArgumentParser(description="Test UGC API")
./ugc/api/main.py:7:from ugc.schema.api_models import QueryRequest, QueryResult
./ugc/api/main.py:8:from ugc.models import get_model
./ugc/api/main.py:9:from ugc.core.video_processor import VideoProcessor
./ugc/api/main.py:10:from ugc.core.search_engine import SearchEngine
./ugc/api/main.py:11:from ugc.utils.video_cutter import VideoCutter
./ugc/api/main.py:12:from ugc.utils.ugc_avatar_studio_fallback import generate_fallback_video
./ugc/api/main.py:14:app = FastAPI(title="UGC Video Semantic Search")
./ugc/api/main.py:66:            from ugc.utils.broll_fetcher import BRollFetcher
./ugc/core/search_engine.py:9:from ugc.models.base import EmbeddingModel
./ugc/core/search_engine.py:10:from ugc.core.video_processor import VideoProcessor
./ugc/core/video_processor.py:21:from ugc.models.base import EmbeddingModel
./ugc/core/video_processor.py:23:    from ugc.utils.transcript_parser import TranscriptParser
./README.md:1:# UGC Video RAG & API Engine: Engineer's Onboarding Guide
./README.md:3:Welcome! If you are a junior engineer or a new contributor joining the project, this guide will walk you through exactly how to build, test, and run the UGC (User Generated Content) multimodal semantic search engine.
./README.md:18:cd /home/azeez/ws/dev_env/py_code/projects/ugc
./README.md:22:*Note: This will tag the image as `ugc-app`.*
./README.md:40:Test the pipeline against a physical video file mounted in your `ugc/data/` folder. We will ask for 3 outputs, evaluating both text and visuals (`mixed`), and output them in TikTok format (`9:16`).
./README.md:49:*What happens: The AI will index `t12s_vid.mp4` and `dummy.srt`, find the highest mathematical match for "person doing pushup", and output the trimmed clips to `ugc/data/`.*
./README.md:81:docker run --rm --env-file /home/azeez/ws/dev_env/py_code/projects/ugc/.env -v "/home/azeez/ws/dev_env/py_code/projects/ugc:/app" -w /app ugc-app python ugc/test/test_api.py --scenario ALL
./README.md:98:docker run --rm -v "/home/azeez/ws/dev_env/py_code/projects/ugc:/app" -w /app ugc-app python ugc/utils/ugc_avatar_studio_fallback.py --speech-text "Hello junior engineer, welcome to the team!"
./README.md:105:docker run --rm -v "/home/azeez/ws/dev_env/py_code/projects/ugc:/app" -w /app ugc-app python ugc/utils/ugc_avatar_studio_fallback.py \
./README.md:108:  --output ugc/data/female_avatar.mp4
./README.md:115:If your `ugc/data/` folder is getting cluttered with generated MP4s, B-rolls, and reports, use the built-in clean command:
./README.md:126:ugc/
./README.md:136:└── ugc/
```

### Command:
`mv /home/azeez/ws/dev_env/py_code/projects/ugc /home/azeez/ws/dev_env/py_code/projects/b_roll_rag`

### Output:
*(Renamed outer directory successfully)*

### Command:
`mv /home/azeez/ws/dev_env/py_code/projects/b_roll_rag/ugc /home/azeez/ws/dev_env/py_code/projects/b_roll_rag/b_roll_rag`

### Output:
*(Renamed inner package directory successfully)*

### Command:
`mv /home/azeez/ws/dev_env/py_code/projects/b_roll_rag/run_ugc.sh /home/azeez/ws/dev_env/py_code/projects/b_roll_rag/run_b_roll_rag.sh`

### Output:
*(Renamed runner script successfully)*

### Command:
`grep -rnwi "ugc" --exclude=ugc_avatar_studio_fallback.py --exclude-dir={.hf_cache,__pycache__,data} /home/azeez/ws/dev_env/py_code/projects/b_roll_rag/b_roll_rag`

### Output:
*(Exit code 1: No matches found)*

### Command:
`./run_b_roll_rag.sh build`

### Output:
```
Building b-roll-rag-app docker image...
Build complete.
```

### Command:
`./run_b_roll_rag.sh up clip 3 1 None scene 16:9 None "impossible query" S3`

### Output:
```
Running Pipeline -> Model: clip | Query: impossible query | Scenario: S3
Initializing app with model clip...
Loading openai/clip-vit-base-patch32 on cpu...

--- S3: Search without indexed video (Avatar fallback) ('impossible query') ---
Initializing models...
Loading openai/clip-vit-base-patch32 on cpu...
Speech detected. Calculated duration: 7.80s
Rendering male1...
Frame 0/234...
Frame 10/234...
Frame 20/234...
Frame 30/234...
Frame 40/234...
Frame 50/234...
Frame 60/234...
Frame 70/234...
Frame 80/234...
Frame 90/234...
Frame 100/234...
Frame 110/234...
Frame 120/234...
Frame 130/234...
Frame 140/234...
Frame 150/234...
Frame 160/234...
Frame 170/234...
Frame 180/234...
Frame 190/234...
Frame 200/234...
Frame 210/234...
Frame 220/234...
Frame 230/234...
Done! Saved to /tmp/b_roll_rag_uploads/fallback_bc67e9c6-dbac-4a30-94e3-c51d68692ac6.mp4 and /tmp/b_roll_rag_uploads/fallback_bc67e9c6-dbac-4a30-94e3-c51d68692ac6.gif
Avatar Fallback generated at: /tmp/b_roll_rag_uploads/fallback_bc67e9c6-dbac-4a30-94e3-c51d68692ac6.mp4

Selected API tests completed successfully!
```

### Command:
`./run_b_roll_rag.sh up clip 3 1 None mixed 16:9 None "making coffee" S2`

### Output:
```
Running Pipeline -> Model: clip | Query: making coffee | Scenario: S2
Initializing app with model clip...
Loading openai/clip-vit-base-patch32 on cpu...

--- S2: Search without indexed video (Pexels fallback) ('making coffee') ---
Initializing models...
Loading openai/clip-vit-base-patch32 on cpu...
Original: 'making coffee' -> Optimized for Pexels: 'making+coffee'
Searching Pexels for query: 'making coffee'...
Starting concurrent download of 3 videos...
Successfully downloaded: making_coffee_rank1_7699724.mp4
Successfully downloaded: making_coffee_rank3_7487683.mp4
Successfully downloaded: making_coffee_rank2_28677016.mp4
Processing B-roll directory: /tmp/b_roll_rag_uploads/broll
Processing video: /tmp/b_roll_rag_uploads/broll/making_coffee_rank2_28677016.mp4 (Frames per scene: 1)
Detected 1 physical scenes. Extracting and embedding...
Video visual scenes processed and added to FAISS index.
Processing video: /tmp/b_roll_rag_uploads/broll/making_coffee_rank3_7487683.mp4 (Frames per scene: 1)
Detected 1 physical scenes. Extracting and embedding...
Video visual scenes processed and added to FAISS index.
Processing video: /tmp/b_roll_rag_uploads/broll/making_coffee_rank1_7699724.mp4 (Frames per scene: 1)
Detected 1 physical scenes. Extracting and embedding...
Video visual scenes processed and added to FAISS index.
Pexels Fallback generated at: /tmp/b_roll_rag_uploads/cut_ddd027c5-27c1-4694-893e-7d212ea3921d.mp4

Selected API tests completed successfully!
```
