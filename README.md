# Dictatr

Local, offline push-to-talk dictation tool. Two-stage pipeline: speech-to-text via whisper.cpp, then cleanup via a local SLM (Qwen3 0.6B), then text injected as synthetic keystrokes system-wide.

## Prerequisites

- **whisper.cpp** — clone and build separately (not vendored):
  ```bash
  git clone https://github.com/ggerganov/whisper.cpp
  cd whisper.cpp
  cmake -B build && cmake --build build --config Release
  ./models/download-ggml-model.sh small.en
  ```
- **Ollama** serving a cleanup model (e.g. `qwen3:0.6b`)
- Python 3.12+ with `uv`

## Usage

```bash
# Terminal 1: Start whisper.cpp server (from your whisper.cpp directory)
./build/bin/whisper-server -m models/ggml-small.en.bin -t 8 --host 127.0.0.1 --port 8080

# Terminal 2: Ensure Ollama has the model loaded
ollama pull qwen3:0.6b

# Terminal 3: Run dictatr
LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 uv run python main.py
```

Hold **Right Ctrl** and speak. Release — cleaned text appears in the focused application.

## Architecture

```
[evdev hotkey listener] → [sounddevice audio capture]
    → [whisper.cpp STT] → [Ollama SLM cleanup]
    → [evdev UInput keystroke injection]
```

## Project layout

```
dictatr/
├── main.py                  # Entry point — orchestrates the pipeline
├── pyproject.toml           # Dependencies (evdev, numpy, ollama, requests, scipy, sounddevice)
├── src/
│   ├── hotkey_listener.py   # evdev keyboard discovery + push-to-talk
│   ├── audio_capture.py     # sounddevice 16kHz mono WAV capture
│   ├── stt_client.py        # whisper.cpp HTTP multipart upload
│   ├── cleanup_client.py    # Ollama-based filler/punctuation cleanup
│   └── inject.py            # UInput virtual keyboard for text injection
├── sample/                  # Test audio clips
├── config.toml              # Runtime configuration
├── HANDOFF.md               # Project history and architecture decisions
├── TODO.md                  # Future roadmap
└── WHISPER.md               # whisper-cli invocation reminder
```
