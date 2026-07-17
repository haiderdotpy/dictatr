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
- **Ollama** with the cleanup model installed:

  ```bash
  ollama pull qwen3:0.6b
  ```
- Python 3.12+ with `uv`

## Installation

Run the installer from the project root:

```bash
chmod +x install.sh
./install.sh
```

This installs the `dictatr` launcher into `~/.local/bin`.

> **Note:** Ensure `~/.local/bin` is in your `PATH`.

## Usage

Start Dictatr from any terminal:

```bash
dictatr
```

## Architecture

```
[evdev hotkey listener] → [sounddevice audio capture]
    → [whisper.cpp STT] → [Ollama SLM cleanup]
    → [evdev UInput keystroke injection]
```

## Project layout

```
Dictatr
├── main.py
├── pyproject.toml
├── README.md
├── install.sh
├── scripts
│   └── run.sh
├── src
│   ├── audio_capture.py
│   ├── cleanup_client.py
│   ├── hotkey_listener.py
│   ├── inject.py
│   └── stt_client.py
├── uv.lock
└── whisper.cpp
```
