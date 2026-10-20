#!/usr/bin/env bash

WHISPER_THREADS=${1:-2}
STT_WORKERS=${2:-3}
MODEL=${3:-ggml-base.en}
OLLAMA=${4}

echo "Dictatr Test"
if [[ -n "$4" ]]; then echo "Cleanup model:    $OLLAMA"; fi
echo "Model:            $MODEL"
echo "Whisper threads:  $WHISPER_THREADS"
echo "STT workers:      $STT_WORKERS"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

cleanup() {
    echo
    echo "Shutting down..."

    if [[ -n "${WHISPER_PID:-}" ]]; then
        kill "$WHISPER_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "Starting whisper.cpp server..."

./whisper.cpp/build/bin/whisper-server \
    -m ./whisper.cpp/models/${MODEL}.bin \
    -t ${WHISPER_THREADS} \
    --host 127.0.0.1 \
    --port 8080 &

WHISPER_PID=$!

sleep 2

echo "Starting Dictatr..."

MODEL_ARGS=()

if [[ -n "$4" ]]; then
    MODEL_ARGS+=(--cleanup-model "$4")
fi

LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 \
uv run python test.py \
    --stt-workers "$STT_WORKERS" \
    "${MODEL_ARGS[@]}"
