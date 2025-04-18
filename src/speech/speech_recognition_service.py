import speech_recognition as sr
import time
from datetime import timedelta, datetime

recognizer = sr.Recognizer()

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format to let users sink it with videoa aferward, like movies"""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{td.microseconds//1000:03d}"


def listen_for_speech():

    with sr.Microphone() as source:
        # listen to the background noise for X duration, and then try to to minimize the noise
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
                print(f"No speech was detected for more than 10 seconds")
                
    return None

if __name__ == "__main__":
    listen_for_speech()
