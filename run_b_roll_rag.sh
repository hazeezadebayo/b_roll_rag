#!/bin/bash
# TLDR: Project Orchestration CLI.
# Logic: Manages container states. Explicitly injects HF_HOME environment variable 
# and binds local host cache into Docker to ensure model weights download strictly ONCE.

COMMAND=$1
MODEL_NAME=${2:-clip}
TOP_K=${3:-3}

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$PROJECT_DIR/b_roll_rag/data"
CACHE_DIR="$PROJECT_DIR/.hf_cache"

function show_help() {
    echo "b_roll_rag Orchestration CLI"
    echo "====================="
    echo "Usage: ./run_b_roll_rag.sh [COMMAND] [ARGS]"
    echo ""
    echo "Commands:"
    echo "  build - Build the Docker container"
    echo "  up    - Run pipeline. Args: [MODEL] [TOP_K] [FRAMES] [TRANSCRIPT] [MODE] [ASPECT] [VIDEO] [QUERY] [SCENARIO]"
    echo "  clean - Remove generated output mp4s"
    echo "  kill  - Stop running containers"
}

function build_image() {
    echo "Building b-roll-rag-app docker image..."
    cd "$PROJECT_DIR/docker" && docker build -t b-roll-rag-app .
    echo "Build complete."
}

function run_pipeline() {
    FRAMES=${4:-1}
    TRANSCRIPT=$5
    MODE=${6:-mixed}
    ASPECT_RATIO=${7:-original}
    VIDEO_NAME=${8:-None}
    QUERY=${9:-"person doing pushup"}
    SCENARIO=${10:-ALL}

    echo "Running Pipeline -> Model: $MODEL_NAME | Query: $QUERY | Scenario: $SCENARIO"
    mkdir -p "$CACHE_DIR"

    TRANSCRIPT_ARG=""
    if [ ! -z "$TRANSCRIPT" ] && [ "$TRANSCRIPT" != "None" ]; then
        TRANSCRIPT_ARG="--transcript $TRANSCRIPT"
    fi

    ENV_ARG=""
    if [ -f "$PROJECT_DIR/.env" ]; then
        ENV_ARG="--env-file $PROJECT_DIR/.env"
    elif [ ! -z "$PEXELS_API_KEY" ]; then
        ENV_ARG="-e PEXELS_API_KEY=$PEXELS_API_KEY"
    fi

    # CRUCIAL FIX: Inject HF_HOME so transformers library knows exactly where to look/save inside the bound volume
    docker run --rm \
        -v "$PROJECT_DIR:/app" \
        -v "$CACHE_DIR:/root/.cache/huggingface" \
        -e HF_HOME=/root/.cache/huggingface \
        -w /app \
        $ENV_ARG \
        b-roll-rag-app \
        python b_roll_rag/test/test_api.py \
            --model "$MODEL_NAME" \
            --top_k "$TOP_K" \
            --frames_per_scene "$FRAMES" \
            $TRANSCRIPT_ARG \
            --mode "$MODE" \
            --aspect_ratio "$ASPECT_RATIO" \
            --video "$VIDEO_NAME" \
            --query "$QUERY" \
            --scenario "$SCENARIO"
}

function clean_outputs() {
    echo "Cleaning generated outputs..."
    rm -f "$DATA_DIR"/*.mp4
    rm -f "$DATA_DIR"/report.txt
    echo "Cleaned."
}

function kill_containers() {
    echo "Killing running b-roll-rag-app containers..."
    container_ids=$(docker ps -q --filter ancestor=b-roll-rag-app)
    if [ -n "$container_ids" ]; then
        docker kill $container_ids
        echo "Containers killed."
    else
        echo "No running b-roll-rag-app containers found."
    fi
}

case $COMMAND in
    build) build_image ;;
    up) run_pipeline "$@" ;;
    clean) clean_outputs ;;
    kill) kill_containers ;;
    help|*) show_help ;;
esac