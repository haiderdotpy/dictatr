# Dictatr

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?logo=gnu)

Local, offline push-to-talk dictation tool. Two-stage pipeline: speech-to-text via whisper.cpp, then cleanup via a local SLM (Qwen3 0.6B), then text injected as synthetic keystrokes system-wide.

## Features

- Local-first; no cloud services required
- Streaming speech-to-text using `whisper.cpp`
- WebRTC Voice Activity Detection (VAD)
- Local transcript cleanup with Ollama (Qwen3 0.6B)
- System-wide push-to-talk input
- Works in any application via synthetic keyboard events

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

```text
                        Hold Right Ctrl
                              │
                              ▼
                    Global Hotkey Listener (evdev)
                              │
                              ▼
                    Audio Capture (sounddevice)
                              │
                 Audio callback (20 ms frames)
                              │
                              ▼
                        frame_queue (Queue)
                              │
                              ▼
                VAD Worker (WebRTC Voice Activity Detection)
                              │
             ┌────────────────┴────────────────┐
             │                                 │
      Speech continues                  End of speech
             │                                 │
             ▼                                 ▼
      Buffer current frame          Emit speech segment
                                            │
                                            ▼
                                 speech_queue (Queue)
                                            │
                                            ▼
                              Transcription Worker
                                            │
                                            ▼
                         whisper.cpp Server (Streaming)
                                            │
                                            ▼
                              transcript_chunks (list)
                                            │
                                            ▼
                      Join transcript after recording ends
                                            │
                                            ▼
                        LLM Cleanup (Qwen3 via Ollama)
                                            │
                                            ▼
                     System-wide Keyboard Injection
                                            │
                                            ▼
                            Active Application
```

### Pipeline

1. Hold **Right Ctrl** to begin recording.
2. `sounddevice` streams 20 ms audio frames from the microphone.
3. Each frame is pushed into a thread-safe `frame_queue`.
4. A dedicated VAD worker uses **WebRTC VAD** to detect speech boundaries.
5. Completed speech segments are emitted into a `speech_queue`.
6. A transcription worker streams each segment to the local `whisper.cpp` server.
7. Partial transcripts are accumulated while recording is still in progress.
8. When the hotkey is released, the remaining audio is flushed and the final transcript is assembled.
9. The complete transcript is cleaned up using a local language model served by **Ollama**.
10. The polished text is injected into the currently focused application via synthetic keyboard events.

## Project layout

```
Dictatr
├── install.sh
├── main.py
├── pyproject.toml
├── README.md
├── scripts
│   └── run.sh
├── src
│   ├── audio_capture.py
│   ├── cleanup_client.py
│   ├── hotkey_listener.py
│   ├── inject.py
│   ├── stt_client.py
│   ├── transcription_worker.py
│   └── vad_worker.py
├── uv.lock
└── whisper.cpp
```
