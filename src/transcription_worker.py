from src.stt_client import speechtotext
import io
import wave

def pcm_to_wav(pcm_bytes, sample_rate=16000):
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)      # int16 = 2 bytes
        wav.setframerate(sample_rate)
        wav.writeframes(pcm_bytes)

    buffer.seek(0)
    return buffer

def transcription_worker(speech_queue, transcript_chunks):
    while True:
        item = speech_queue.get()

        if item is None:
            break

        index, chunk = item

        # print(f"[STT] starting chunk {index}; queue={speech_queue.qsize()}")

        wav = pcm_to_wav(chunk)
        transcript = speechtotext(wav)

        if transcript is not None:
            transcript_chunks.append((index, transcript))
