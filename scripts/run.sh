#!/usr/bin/env bash

set -e

cleanup() {
    echo
    echo "Shutting down..."

    kill "$WHISPER_PID" 2>/dev/null || true

    exit
}

trap cleanup SIGINT SIGTERM

echo "Starting whisper.cpp server..."

./whisper.cpp/build/bin/whisper-server \
    -m ./whisper.cpp/models/ggml-small.en.bin \
    -t 8 \
    --host 127.0.0.1 \
    --port 8080 &

WHISPER_PID=$!

sleep 2

echo "Starting Dictatr..."

LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 \
uv run python main.py

cleanup