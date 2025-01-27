import pyttsx3

def test_tts():
    engine = pyttsx3.init()
    for i in range(3):
        text = f"This is test number {i+1}"
        print(f"Speaking: {text}")
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    print("TTS test completed!")

test_tts()

