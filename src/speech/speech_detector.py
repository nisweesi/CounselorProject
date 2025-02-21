import os
import vosk
import json
<<<<<<< Updated upstream
import pyaudio
from config import VOSK_MODEL_PATH

class SpeechDetector:
    def __init__(self, vosk_model_path=VOSK_MODEL_PATH):
        if not os.path.exists(vosk_model_path):
            raise FileNotFoundError(f"VOSK Model not found at {vosk_model_path}. Ensure it is downloaded correctly.")

        self.model = vosk.Model(vosk_model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)

    def detect_speech(self):
        """Capture and process speech using VOSK."""
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
        stream.start_stream()

        print("Listening...")
        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if len(data) == 0:
                break
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                return result.get("text", "")

        return None
=======
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

    def start_stream(self, device_index=1):
        """Start the microphone stream"""
        if self.stream is not None:
            return
        try:
            self.stream = self.mic.open(format=pyaudio.paInt16,
                                        channels=1,
                                        rate=self.rate,
                                        input=True,
                                        input_device_index=device_index,
                                        frames_per_buffer=self.buffer_size)
            print(f"Using input device {device_index}: {self.mic.get_device_info_by_index(device_index)['name']}")
        except OSError as e:
            print(f"Error initializing audio stream: {e}")

    def stop_stream(self):
        """Stop and close the microphone stream"""
        if self.stream:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.mic:
            self.mic.terminate()

    def detect_speech(self):
        """Recognizes speech and converts it to text"""
        try:
            self.start_stream()
            print("Listening...")
            while True:
                try:
                    data = self.stream.read(self.buffer_size, exception_on_overflow=False)
                except IOError as e:
                    print(f"Stream read error: {e}")
                    continue 

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        return text
        except KeyboardInterrupt:
            print("\nStopping detection.")
        finally:
            self.stop_stream()

if __name__ == "__main__":
    vosk_model_path = "data/vosk_model"
    speech_detector = SpeechDetector(vosk_model_path)
    while True:
        recognized_text = speech_detector.detect_speech()
        if recognized_text:
            print(f"Recognized: {recognized_text}")
>>>>>>> Stashed changes
