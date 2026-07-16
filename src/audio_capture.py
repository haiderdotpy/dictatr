import sounddevice as sd
import numpy as np
import io
from scipy.io.wavfile import write as write_wav

SAMPLE_RATE = 16000 
CHANNELS = 1

_frames = []
_stream = None

def _callback(indata, frames, time, status):
    if status:
        print(status) 
    _frames.append(indata.copy())

def start_capture():
    global _frames, _stream
    _frames = []
    _stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        callback=_callback,
    )
    _stream.start()

def stop_capture() -> io.BytesIO:
    global _stream
    _stream.stop()
    _stream.close()
    _stream = None

    audio = np.concatenate(_frames, axis=0)

    buffer = io.BytesIO()
    write_wav(buffer, SAMPLE_RATE, audio)
    buffer.seek(0)
    return buffer