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

def _close_stream():
    global _stream

    if _stream is None:
        return

    try:
        _stream.stop()
    finally:
        try:
            _stream.close()
        except Exception:
            pass
        _stream = None

def start_capture(frame_queue):
    global _frames, _stream, _frame_queue

    abort_capture()

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
    global _frames, _frame_queue

    _close_stream()

    if _frames:
        audio = np.concatenate(_frames, axis=0)
    else:
        audio = np.empty((0, CHANNELS), dtype=np.int16)

    buffer = io.BytesIO()
    write_wav(buffer, SAMPLE_RATE, audio)
    buffer.seek(0)
    _frames = []
    _frame_queue = None
    return buffer

def abort_capture():
    global _frames, _frame_queue

    try:
        _close_stream()
    except Exception:
        pass

    _frames = []
    _frame_queue = None
