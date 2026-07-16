from src.hotkey_listener import wait_for_recording
from src.stt_client import speechtotext
from src.cleanup_client import cleanup_transcript
from src.inject import type_text


def main():
    print("Dictatr ready. Hold Right Ctrl to dictate.")

    while True:
        audio = wait_for_recording()

        transcript = speechtotext(audio)
        if transcript is None:
            print("STT failed, skipping.")
            continue

        cleaned = cleanup_transcript(transcript)

        print(transcript)
        print("→", cleaned)

        type_text(cleaned)


if __name__ == "__main__":
    main()