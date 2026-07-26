from src.hotkey_listener import wait_for_recording
from src.stt_client import speechtotext
from src.cleanup_client import cleanup_transcript
from src.inject import type_text
from src.vad_worker import vad_worker
from src.transcription_worker import transcription_worker
from queue import Queue
import time
import threading
import wave
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--stt-workers",
    type=int,
    default=3
)

args = parser.parse_args()

FRAME_DURATION_MS = 20
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2
CHANNELS = 1
SPEED = 1
TRANSCRIPT_WORKERS = args.stt_workers

AUDIO_FILES = [
    'test_audio/001.wav',
    'test_audio/002.wav',
    'test_audio/003.wav',
    'test_audio/004.wav',
]

def feed_wav(path, frame_queue): 
    print(f"\n[TEST]  Playing {path}")

    with wave.open(path, "rb") as wav:
        assert wav.getframerate() == SAMPLE_RATE
        assert wav.getsampwidth() == SAMPLE_WIDTH
        assert wav.getnchannels() == CHANNELS

        frame_size = int(SAMPLE_RATE*FRAME_DURATION_MS/1000); 

        print("channels:", wav.getnchannels())
        print("sample width:", wav.getsampwidth())
        print("sample rate:", wav.getframerate())
        print("frames:", wav.getnframes())
        print("duration:", wav.getnframes() / wav.getframerate())

        while True: 
            frame = wav.readframes(frame_size)

            if not frame:
                break

            if len(frame) < frame_size * SAMPLE_WIDTH * CHANNELS:
                frame += b"\x00" * (frame_size * SAMPLE_WIDTH * CHANNELS - len(frame))

            frame_queue.put(frame)

            time.sleep(FRAME_DURATION_MS / 1000)

def feed_silence(frame_queue, duration_ms=500):
    frame_size = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
    silence = b"\x00" * (frame_size * SAMPLE_WIDTH * CHANNELS)

    for _ in range(duration_ms // FRAME_DURATION_MS):
        frame_queue.put(silence)
        time.sleep((FRAME_DURATION_MS / 1000) / SPEED)

def main():
    print("Dictatr ready.")

    for i, audio_file in enumerate(AUDIO_FILES):

        frame_queue = Queue()
        speech_queue = Queue()
        transcript_chunks = []

        vad_thread = threading.Thread(target=vad_worker, args=(frame_queue, speech_queue))
        transcript_threads = [
            threading.Thread(target=transcription_worker, args=(speech_queue, transcript_chunks))
            for _ in range(TRANSCRIPT_WORKERS)
        ]

        vad_thread.start()
        for transcript_thread in transcript_threads:
            transcript_thread.start()

        start = time.perf_counter()

        # wait_for_recording(frame_queue)
        
        feed_wav(audio_file, frame_queue=frame_queue)
        if i < len(AUDIO_FILES) - 1:
            feed_silence(frame_queue, 500)

        frame_queue.put(None)
        vad_thread.join()

        for _ in range(TRANSCRIPT_WORKERS):
            speech_queue.put(None)
        for transcript_thread in transcript_threads:
            transcript_thread.join()

        transcript_chunks.sort(key=lambda x: x[0])
        transcript = " ".join(
            chunk_indexed[1] for chunk_indexed in transcript_chunks if chunk_indexed is not None
        )

        stt_time = time.perf_counter() - start

        if not transcript:
            print("STT failed, skipping.")
            continue

        start = time.perf_counter()

        cleaned = cleanup_transcript(transcript)
        cleanup_time = time.perf_counter() - start

        print(transcript)
        print("→", cleaned)

        # start = time.perf_counter()
        # type_text(f"[TEST INDEX {i}]\n[TRANSCRIPTION]\n{cleaned}\n\n")
        # typing_time = time.perf_counter() - start

        with wave.open(audio_file, "rb") as wav: 
            duration = wav.getnframes() / wav.getframerate()

        print(f"[STT]               {stt_time:.2f}s")
        print(f"[STT LATENCY]       {stt_time-duration:.2f}s")
        print(f"[CLEANUP]           {cleanup_time:.2f}s")
        # print(f"[TYPING]            {typing_time:.2f}s")
        print(f"[TOTAL]             {(stt_time + cleanup_time):.2f}s") # 
        print(f"[E2E LATENCY]       {(stt_time + cleanup_time)-duration:.2f}s") # 
        print(f"[STT RTF]           {(stt_time)/duration:.2f}")
        print(f"[TOTAL RTF]         {(stt_time + cleanup_time)/duration:.2f}") # 


if __name__ == "__main__":
    main()