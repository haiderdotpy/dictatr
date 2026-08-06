from src.hotkey_listener import wait_for_recording
from src.stt_client import speechtotext
from src.cleanup_client import cleanup_transcript
from src.inject import type_text
from src.vad_worker import vad_worker
from src.transcription_worker import transcription_worker
from queue import Queue
import time
import threading
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--stt-workers",
    type=int,
    default=3
)

parser.add_argument(
    "--cleanup-model",
    type=str,
    default=None
)

args = parser.parse_args()

TRANSCRIPT_WORKERS = args.stt_workers
CLEANUP_MODEL = args.cleanup_model

def main():
    print(f"""
        ██████╗ ██╗ ██████╗████████╗ █████╗ ████████╗██████╗
        ██╔══██╗██║██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗
        ██║  ██║██║██║        ██║   ███████║   ██║   ██████╔╝
        ██║  ██║██║██║        ██║   ██╔══██║   ██║   ██╔══██╗
        ██████╔╝██║╚██████╗   ██║   ██║  ██║   ██║   ██║  ██║
        ╚═════╝ ╚═╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
""")
    print("Dictatr ready. Hold Right Ctrl to dictate.")
    if CLEANUP_MODEL is not None:
        print(f"Using {CLEANUP_MODEL} for transcript cleanup.")

    while True:

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

        wait_for_recording(frame_queue)

        start = time.perf_counter()

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

        cleaned = cleanup_transcript(transcript, CLEANUP_MODEL)
        cleanup_time = time.perf_counter() - start

        print(transcript)
        print("→", cleaned)

        start = time.perf_counter()
        type_text(cleaned)
        typing_time = time.perf_counter() - start

        print(f"[STT]     {stt_time:.2f}s (perceived)")
        print(f"[CLEANUP] {cleanup_time:.2f}s")
        print(f"[TYPING]  {typing_time:.2f}s")
        print(f"[TOTAL]   {stt_time + cleanup_time + typing_time:.2f}s")


if __name__ == "__main__":
    main()
