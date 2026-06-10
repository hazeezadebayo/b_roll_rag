# b_roll_rag Video RAG & API Engine: Engineer's Onboarding Guide

Welcome! If you are a junior engineer or a new contributor joining the project, this guide will walk you through exactly how to build, test, and run the b_roll_rag (User Generated Content / B-Roll RAG) multimodal semantic search engine.

Our system analyzes long-form videos (or dynamically fetches B-roll), indexes visual scenes and spoken transcripts using AI Vision models (like OpenAI's CLIP), and allows you to semantically search for footage using natural language (e.g., "person doing pushup"). If it finds what you need, it cuts it perfectly. **If it doesn't find what you need, it dynamically generates an AI Avatar to present a fallback video!**

The golden rule of this repo: **We do not pollute the host machine.** Everything runs perfectly inside an isolated Docker container.

---

## 🛠️ Step 1: Environment Setup

### Build the Docker Image

Before running any tests, you must build the container environment. This container comes pre-loaded with PyTorch, FAISS, FFmpeg, and all necessary dependencies.

```bash
cd path/to/b_roll_rag
./run_b_roll_rag.sh build
```

*Note: This will tag the image as `b-roll-rag-app`.*

---

## 🧪 Step 2: Running the RAG Pipeline (`test_api.py`)

The pipeline test is our core CLI orchestrator. It tests the end-to-end flow: from video loading, to FAISS indexing, to AI semantic searching, and finally to FFmpeg cutting.

We use the wrapper script `./run_b_roll_rag.sh up` to safely mount your directories and execute the pipeline inside Docker.

### Command Structure

```bash
./run_b_roll_rag.sh up [MODEL] [TOP_K] [FRAMES_PER_SCENE] [TRANSCRIPT] [MODE] [ASPECT_RATIO] [VIDEO_NAME_OR_NONE] [QUERY] [SCENARIO]
```

### Scenario A: Process a Local Video

Test the pipeline against a physical video file mounted in your `b_roll_rag/data/input/` folder. We will ask for 3 outputs, evaluating both text and visuals (`mixed`), and output them in TikTok format (`9:16`), with a strict similarity threshold of `1.3`.

```bash
./run_b_roll_rag.sh up clip 3 3 dummy.srt mixed 9:16 didl_vid.mp4 "making coffee" S1 1.3


./run_b_roll_rag.sh up siglip 3 3 dummy.srt mixed 9:16 t12s_vid.mp4 "person doing pushup" S1 1.3
```

*What happens: The AI will index `t12s_vid.mp4` and `dummy.srt`, find the highest mathematical match for "person doing pushup", and output the trimmed clips to `b_roll_rag/data/output/`. Any match with a score below `1.3` will be rejected.*

### Scenario B: AI B-Roll Fetcher

Pass `None` as the video. The system will autonomously download 10 videos from the Pexels API, rank them against your query locally, and output the winners.

```bash
# Provide PEXELS_API_KEY in the .env file or export it!
export PEXELS_API_KEY="your_api_key_here"

./run_b_roll_rag.sh up clip 3 1 None scene 9:16 None "neon cyberpunk streets" S2
```

### Scenario C: The Ultimate Fallback (No Matches!)

If the pipeline fails to find *any* matches or the Pexels API fails, it triggers the **Avatar Studio Fallback**.

```bash
./run_b_roll_rag.sh up clip 1 1 None scene 16:9 None "impossible query that does not exist" S3
```

*What happens: The pipeline catches the 0-match error, dynamically calculates mouth movements, and natively renders an `.mp4` of a geometric avatar speaking your exact query!*

---

## 🌐 Step 3: Testing the API Backend (`test_api.py`)

The pipeline logic is also exposed via a `FastAPI` server. We have a dedicated test script (`test_api.py`) that uses `TestClient` to ensure the API correctly handles video uploads, semantic searches, and—most importantly—fallback interception.

To run the API test suite inside the container:

```bash
docker run --rm --env-file .env -v "$PWD:/app" -w /app b-roll-rag-app python b_roll_rag/test/test_api.py --scenario ALL
```

**What this test does:**

1. **Test Case 1:** Deliberately queries the API without uploading a video. The API intercepts the error and returns a fully generated Fallback Video explaining the missing index, returning HTTP 200 instead of a crash!
2. **Test Case 2:** Uploads a dummy video and issues a mathematically impossible query. The API catches the empty semantic result and dynamically generates a personalized Fallback Video.

---

## 🎨 Step 4: Testing the Avatar Studio Directly

If you just want to generate high-quality fallback avatars directly (without running the full RAG pipeline or API), you can invoke the utility script via Docker.

**Basic Usage:**

```bash
docker run --rm -v "$PWD:/app" -w /app b-roll-rag-app python b_roll_rag/utils/ugc_avatar_studio_fallback.py --speech-text "Hello junior engineer, welcome to the team!"
```

**Customizing the Avatar:**
You can change the character preset and output explicitly:

```bash
docker run --rm -v "$PWD:/app" -w /app b-roll-rag-app python b_roll_rag/utils/ugc_avatar_studio_fallback.py \
  --character female2 \
  --speech-text "Testing the fallback generation with face paint." \
  --output b_roll_rag/data/output/female_avatar.mp4
```

---

## 🧹 Step 5: Cleanup

If your `b_roll_rag/data/output/` folder is getting cluttered with generated MP4s, B-rolls, and reports, use the built-in clean command:

```bash
./run_b_roll_rag.sh clean
```

---

## 📂 Architecture Overview

```text
b_roll_rag/
├── run_b_roll_rag.sh            # Your primary CLI orchestrator.
├── README.md                    # This document.
├── project_report.md            # Living technical architecture document for AI/Engineering.
├── output_log.md                # Verbatim execution history of bash commands.
│
├── docker/
│   ├── Dockerfile               # Defines the Python 3.10 + FFmpeg isolated environment.
│   └── requirements.txt         # Container dependencies (torch, transformers, faiss, etc).
│
└── b_roll_rag/
    ├── api/               
    │   └── main.py              # FastAPI entrypoint exposing the search engine over HTTP.
    │
    ├── core/
    │   ├── search_engine.py     # Executes multimodal FAISS queries and temporal deduplication.
    │   └── video_processor.py   # Handles scene detection, transcript mapping, and FAISS indexing.
    │
    ├── data/                    # The mounted directory for inputs (videos, .srt) and outputs.
    │
    ├── models/                  # Factory router for loading different Vision models (CLIP, SigLIP).
    │
    ├── schema/
    │   └── api_models.py        # Pydantic schemas for data validation.
    │
    ├── test/
    │   └── test_api.py          # End-to-end orchestrator and FastAPI endpoint fallback testing script.
    │
    └── utils/
        ├── broll_fetcher.py               # Reaches out to Pexels API.
        ├── transcript_parser.py           # Parses `.srt` and `.txt` files.
        ├── video_cutter.py                # FFmpeg zero-distortion cutting and blurred-padding.
        └── ugc_avatar_studio_fallback.py  # Zero-dependency, pure-math geometric avatar generator.
```

---

---
