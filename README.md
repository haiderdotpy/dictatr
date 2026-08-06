![Cover](./assets/Dictatr.png)

![Platform](https://img.shields.io/badge/platform-Linux-blue)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python\&logoColor=white)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?logo=gnu)

# Dictatr

Local, offline push-to-talk dictation tool. Dictatr uses a streaming pipeline built around `whisper.cpp`, WebRTC VAD, and a configurable pool of transcription workers. A local language model served through Ollama then cleans up the resulting transcript before injecting it system-wide as synthetic keyboard input.

## Features

* Local-first; no cloud services required
* Streaming speech-to-text using `whisper.cpp`
* WebRTC Voice Activity Detection (VAD)
* Configurable Whisper thread count and transcription worker count
* Local transcript cleanup with Ollama
* Automatically selects the smallest installed Ollama model by default to minimize cleanup latency
* Optional manual selection of the Ollama cleanup model
* System-wide push-to-talk input
* Works in any application via synthetic keyboard events
* Built-in benchmarking mode for testing performance on different hardware

## Prerequisites

* **whisper.cpp** — clone and build separately (not vendored):

  ```bash
  git clone https://github.com/ggerganov/whisper.cpp
  cd whisper.cpp
  cmake -B build && cmake --build build --config Release
  ./models/download-ggml-model.sh base.en
  ```

* **Ollama** with at least one local model installed:

  ```bash
  ollama pull qwen3:0.6b
  ```

  Dictatr can use any installed Ollama model for transcript cleanup.

* Python 3.12+ with `uv`

> **Note:** Dictatr supports different Whisper models. Download the model you want to use and pass its filename to `dictatr` or `test.sh`. For example, `ggml-tiny.en`, `ggml-base.en`, or a quantized model such as `ggml-base.en-q5_0`.

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

Hold **Right Ctrl** while speaking, then release it to transcribe and inject the text into the currently focused application.

> **Note:** The whisper.cpp server writes its logs to `logs/whisper.log` instead of the terminal.

### Configuring Dictatr

The launcher accepts up to four optional arguments:

```bash
dictatr <whisper_threads> <stt_workers> <whisper_model> <ollama_model>
```

For example:

```bash
dictatr 2 2 ggml-tiny.en qwen3:0.6b
```

This runs Whisper with 2 threads, uses 2 transcription workers, loads the Tiny English model, and uses `qwen3:0.6b` for transcript cleanup.

The Ollama cleanup model is optional. If it is not specified, Dictatr queries Ollama for the locally installed models and automatically selects the smallest one. This is intended to minimize cleanup latency while still allowing users to explicitly choose a model when desired.

For example:

```bash
dictatr 2 2 ggml-tiny.en
```

will automatically select the smallest installed Ollama model.

If no arguments are provided, the defaults are:

```text
Whisper threads: 2
STT workers:     3
Whisper model:   ggml-base.en
Ollama model:    smallest installed model
```

The optimal configuration depends heavily on the hardware the application is running on. More threads or workers do not necessarily mean lower latency, and a smaller Ollama model does not necessarily provide the best cleanup quality.

## Benchmarking

Dictatr includes a separate test/benchmark mode for evaluating the pipeline without manually speaking into the microphone.

```bash
./scripts/test.sh <whisper_threads> <stt_workers> <whisper_model> [ollama_model]
```

For example:

```bash
./scripts/test.sh 2 2 ggml-base.en
```

If no Ollama model is specified, the benchmark automatically selects the smallest locally installed model.

To explicitly benchmark a particular cleanup model:

```bash
./scripts/test.sh 2 2 ggml-base.en qwen3:0.6b
```

The benchmark feeds recorded WAV files into the same 20 ms frame → VAD → transcription pipeline used by Dictatr. This allows different Whisper models, thread counts, transcription worker counts, and Ollama cleanup models to be compared reproducibly.

Unlike normal Dictatr operation, **the benchmark does not type the resulting transcript into the active application**. It reports metrics such as:

* STT processing time
* STT latency relative to the duration of the speech
* Cleanup latency
* End-to-end latency
* STT real-time factor (RTF)
* Total pipeline RTF

Example:

```text
[STT]               21.85s
[STT LATENCY]        1.60s
[CLEANUP]            2.62s
[TYPING]             0.90s
[TOTAL]             25.37s
[E2E LATENCY]        5.12s
[STT RTF]            1.08
[TOTAL RTF]          1.25
```

The benchmark is particularly useful for finding a configuration that works well on your own machine. For example, a faster machine may be able to run a larger Whisper model while maintaining acceptable latency, while a lower-powered CPU may benefit from a smaller or quantized model.

### Benchmarking different configurations

Try different combinations of Whisper threads, STT workers, Whisper models, and Ollama cleanup models:

```bash
./scripts/test.sh 1 2 ggml-tiny.en
./scripts/test.sh 2 2 ggml-tiny.en
./scripts/test.sh 2 3 ggml-base.en
./scripts/test.sh 2 2 ggml-base.en-q5_0
./scripts/test.sh 2 2 ggml-base.en qwen3:0.6b
```

The goal is not simply to maximize throughput. A good configuration should keep the transcription queue from continuously growing while maintaining acceptable transcription quality and latency.

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
                         ┌──────────────────┴──────────────────┐
                         │                  │                 │
                         ▼                  ▼                 ▼
                  STT Worker 1       STT Worker 2       STT Worker N
                         │                  │                 │
                         └──────────────────┬──────────────────┘
                                            │
                                            ▼
                               whisper.cpp Server
                                            │
                                            ▼
                              transcript_chunks
                                            │
                              sort by chunk index
                                            │
                                            ▼
                         Join transcript after recording ends
                                            │
                                            ▼
                       LLM Cleanup (Ollama)
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
5. Completed speech segments are assigned a sequential index and emitted into a `speech_queue`.
6. Multiple transcription workers consume speech segments from the shared queue.
7. Each worker sends its segment to the local `whisper.cpp` server.
8. Transcripts retain their original chunk indices so that parallel processing does not change the order of the final transcript.
9. When the hotkey is released, remaining audio is flushed and the transcript chunks are assembled in their original order.
10. The complete transcript is cleaned up using a local language model served by **Ollama**.
11. If no Ollama model was explicitly configured, Dictatr selects the smallest installed model before performing cleanup.
12. The polished text is injected into the currently focused application via synthetic keyboard events.

## Project layout

```text
Dictatr
├── install.sh
├── logs
│   └── whisper.log
├── main.py
├── pyproject.toml
├── README.md
├── scripts
│   ├── run.sh
│   └── test.sh
├── src
│   ├── audio_capture.py
│   ├── cleanup_client.py
│   ├── hotkey_listener.py
│   ├── inject.py
│   ├── stt_client.py
│   ├── transcription_worker.py
│   └── vad_worker.py
├── test.py
├── test_audio
│   ├── 001.wav
│   ├── 002.wav
│   ├── 003.wav
│   └── 004.wav
├── uv.lock
└── whisper.cpp
```
