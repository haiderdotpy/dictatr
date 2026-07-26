#!/usr/bin/env bash

WHISPER_THREADS=${1:-2}
STT_WORKERS=${2:-3}
MODEL=${3:-ggml-base.en}

echo "Dictatr Test"
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

    kill "$WHISPER_PID" 2>/dev/null || true

    exit
}

trap cleanup SIGINT SIGTERM

echo "Starting whisper.cpp server..."

./whisper.cpp/build/bin/whisper-server \
    -m ./whisper.cpp/models/${MODEL}.bin \
    -t ${WHISPER_THREADS} \
    --host 127.0.0.1 \
    --port 8080 &

WHISPER_PID=$!

sleep 2

echo "Starting Dictatr..."

LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 \
uv run python test.py \
    --stt-workers "$STT_WORKERS"

cleanup