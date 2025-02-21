import speech_recognition as sr
from speech.speech_detector import SpeechDetector
from config import VOSK_MODEL_PATH, VOSK_SPEAKER_MODEL_PATH

recognizer = sr.Recognizer()
speech_detector = SpeechDetector(vosk_model_path=VOSK_MODEL_PATH)

def listen_for_speech():
    """Capture speech input with VOSK as primary and Google Speech as fallback."""
    print("Listening for speech...")

    # Try VOSK first
    recognized_text = speech_detector.detect_speech()
    if recognized_text:
        print(f"VOSK detected speech: {recognized_text}")
        return recognized_text

    # Fallback to Google Speech Recognition
    try:
        with sr.Microphone() as source:
            print("Switching to Google Speech Recognition...")
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=30)
            text = recognizer.recognize_google(audio)
            print(f"Google detected speech: {text}")
            return text
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return None