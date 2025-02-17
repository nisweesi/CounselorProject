import speech_recognition as sr
import time
from datetime import timedelta

recognizer = sr.Recognizer()

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,MS)"""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{td.microseconds//1000:03d}"

def listen_for_speech():
    """Capture speech input and return transcribed text"""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

        while True:
            try:
                print("Listening...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=None)
                text = recognizer.recognize_google(audio)
                if text:
                    return text
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("Sorry, there was an error with the speech recognition service.")
            except sr.WaitTimeoutError:
                print("No speech detected for more than 10 seconds")
    return None

if __name__ == "__main__":
    listen_for_speech()
