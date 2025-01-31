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

    def start_stream(self, device_index=1):
        """Start the microphone stream with an explicit device index"""
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
        try:
            self.start_stream()
            print("Listening... ")

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
    vosk_model_path = "/Users/nadir/workspace/CounselorProject/data/vosk_model/vosk_model_en_us_0.42_gigaspeech"
    speech_detector = SpeechDetector(vosk_model_path)
    
    while True:
        recognized_text = speech_detector.detect_speech()
        if recognized_text:
            print(f"Recognized: {recognized_text}")