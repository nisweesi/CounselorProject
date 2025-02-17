import unittest
from speech.speech_detector import SpeechDetector
from speech.speech_recognition_service import listen_for_speech
from speech.speech_model import speech_model

class TestSpeechRecognition(unittest.TestCase):

    def setUp(self):
        """Set up SpeechDetector instance"""
        self.speech_detector = SpeechDetector(vosk_model_path="data/vosk_model")

    def test_detect_speech(self):
        """Test VOSK speech recognition"""
        result = self.speech_detector.detect_speech()
        self.assertIsInstance(result, str)
    
    def test_listen_for_speech(self):
        """Test Google Speech Recognition"""
        result = listen_for_speech()
        self.assertIsInstance(result, str)

class TestSpeechSynthesis(unittest.TestCase):

    def test_speech_model(self):
        """Test VITS speech synthesis"""
        response = speech_model("Hello, how are you?")
        self.assertIsNotNone(response)

if __name__ == "__main__":
    unittest.main()
