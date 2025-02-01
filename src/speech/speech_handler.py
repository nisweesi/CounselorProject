import speech_recognition as sr
import pyttsx3

recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def listen_for_speech():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=20)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except (sr.UnknownValueError, sr.RequestError):
            return None

def speak_text(text):
    print(f"AI: {text}")
    engine.say(text)
    engine.runAndWait()
