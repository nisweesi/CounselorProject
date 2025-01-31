from TTS.api import TTS
import sounddevice as sd
import numpy as np
import logging


logging.basicConfig(filename="tts_logs.txt",
                    filemode="a",
                    level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

def speech_model(text):
    
    # Load VITS model
    tts = TTS(model_name="tts_models/en/vctk/vits").to("cpu")

    # Generate audio
    audio_output = tts.tts(text, speed=1, speaker = 'p228')
    
    logging.info("Speech generation completed successfully.")

    # Play audio in real-time
    response_spoken = sd.play(np.array(audio_output), samplerate=22050)
    sd.wait()
    return response_spoken


if __name__ == "__main__":
    speech_model("I want you to know that you're not alone. I'm here to listen, and together, we can find a way forward.")