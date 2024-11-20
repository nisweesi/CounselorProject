import pyaudio
import json
import numpy as np
from vosk import Model, KaldiRecognizer, SpkModel
from sklearn.cluster import DBSCAN

class SpeechDetector:
    def __init__(self, vosk_model_path, spk_model_path, rate=16000, buffer_size=8192):
        self.model = Model(vosk_model_path)
        self.spk_model = SpkModel(spk_model_path)
        self.recognizer = KaldiRecognizer(self.model, rate, self.spk_model)
        self.rate = rate
        self.buffer_size = buffer_size
        self.mic = pyaudio.PyAudio()
        self.stream = None
        self.embeddings = []

    def start_stream(self):
        self.stream = self.mic.open(format=pyaudio.paInt16, channels=1, rate=self.rate,
                                    input=True, frames_per_buffer=self.buffer_size)
        self.stream.start_stream()

    def stop_stream(self):
        if self.stream.is_active():
            self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()

    def detect_speech(self):
        try:
            self.start_stream()
            while True:
                data = self.stream.read(self.buffer_size, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if 'spk' in result:
                        embedding = np.array(result['spk'])
                        self.embeddings.append(embedding)
                        print(f"Captured Text: {result.get('text', '')}")
        except KeyboardInterrupt:
            print("Stopping detection.")
        finally:
            self.stop_stream()

    def analyze_speakers(self):
        clustering = DBSCAN(eps=0.5, min_samples=1).fit(self.embeddings)
        return len(set(clustering.labels_))