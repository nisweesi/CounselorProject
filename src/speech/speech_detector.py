import pyaudio
import json
from vosk import Model, KaldiRecognizer

class SpeechDetector:
    def __init__(self, vosk_model_path, rate=16000, buffer_size=8192):
        """Initialize the speech detector with Vosk ASR Model"""
        self.model = Model(vosk_model_path)
        self.recognizer = KaldiRecognizer(self.model, rate)
        self.rate = rate
        self.buffer_size = buffer_size
        self.mic = pyaudio.PyAudio()
        self.stream = None

    def start_stream(self):
        self.stream = self.mic.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=self.rate,
                                    input=True,
                                    frames_per_buffer=self.buffer_size
                                    )
        self.stream.start_stream()

    def stop_stream(self):
        if self.stream.is_active():
            self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()

    def detect_speech(self):
        try:
            self.start_stream()
            print("Listening.. ")


            while True:
                data = self.stream.read(self.buffer_size, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    return text

        except KeyboardInterrupt:
            print("\nStopping detection.")
        finally:
            self.stop_stream()

vosk_model_path = "/Users/nadir/workspace/CounselorProject/data/vosk_model/vosk_model_en_us_0.42_gigaspeech"

if __name__ == "__main__":
    speech_detector = SpeechDetector(vosk_model_path)
    speech_detector.detect_speech()
