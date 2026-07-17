from src.hotkey_listener import wait_for_recording
from src.stt_client import speechtotext
from src.cleanup_client import cleanup_transcript
from src.inject import type_text
import time


def main():
    print("Dictatr ready. Hold Right Ctrl to dictate.")

    while True:
        audio = wait_for_recording()

        start = time.perf_counter()
        transcript = speechtotext(audio)
        stt_time = time.perf_counter() - start

        if transcript is None:
            print("STT failed, skipping.")
            continue

        start = time.perf_counter()
        cleaned = cleanup_transcript(transcript)
        cleanup_time = time.perf_counter() - start

        print(transcript)
        print("→", cleaned)

        start = time.perf_counter()
        type_text(cleaned)
        typing_time = time.perf_counter() - start

        print(f"[STT]      {stt_time:.2f}s")
        print(f"[CLEANUP] {cleanup_time:.2f}s")
        print(f"[TYPING]  {typing_time:.2f}s")
        print(f"[TOTAL]   {stt_time + cleanup_time + typing_time:.2f}s")


if __name__ == "__main__":
    main()