import webrtcvad

class VADSegmenter: 
    def __init__(self):
        self.vad = webrtcvad.Vad(2);
        self.current_chunk = []
        self.silent_frames = 0
        self.in_speech = False
    
    def process_frame(self, frame_bytes, sample_rate=16000):
        speech = self.vad.is_speech(frame_bytes, sample_rate)
        if speech: 
            self.current_chunk.append(frame_bytes)
            self.silent_frames = 0
            self.in_speech = True
        else:
            if self.in_speech:
                self.silent_frames += 1
                if self.silent_frames > 5: 
                    # End of speech segment
                    segment = b''.join(self.current_chunk)
                    self.current_chunk = []
                    self.silent_frames = 0
                    self.in_speech = False
                    return segment
    
    def flush(self):
        if self.current_chunk:
            segment = b''.join(self.current_chunk)
            self.current_chunk = []
            self.silent_frames = 0
            self.in_speech = False
            return segment
        return None
    
def vad_worker(frame_queue, speech_queue):
    vad = VADSegmenter()

    while True:
        frame = frame_queue.get()

        if frame is None:
            break

        chunk = vad.process_frame(frame)

        if chunk is not None: 
            speech_queue.put(chunk)

    chunk = vad.flush()
    if chunk is not None: 
        speech_queue.put(chunk)
        
    speech_queue.put(None)