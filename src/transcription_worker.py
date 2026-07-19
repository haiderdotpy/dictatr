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
        chunk = speech_queue.get()

        if chunk is None:
            break

        wav = pcm_to_wav(chunk)
        transcript = speechtotext(wav)

        if transcript is not None:
            transcript_chunks.append(transcript)
