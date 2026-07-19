import sounddevice as sd
import numpy as np
import io
from scipy.io.wavfile import write as write_wav

SAMPLE_RATE = 16000 
CHANNELS = 1

_frames = []
_stream = None
_frame_queue = None

def _callback(indata, frames, time, status):
    if status:
        print(status) 
    _frames.append(indata.copy())
    if _frame_queue is not None:
        _frame_queue.put(indata.copy().tobytes())

def start_capture(frame_queue):
    global _frames, _stream, _frame_queue
    _frames = []
    _frame_queue = frame_queue
    _stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=320,
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