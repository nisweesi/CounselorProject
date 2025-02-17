from TTS.api import TTS
import sounddevice as sd
import numpy as np
import logging

# Logging setup
logging.basicConfig(filename="tts_logs.txt",
                    filemode="a",
                    level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

def speech_model(text):
    """Generate speech from text using VITS model"""
    
    # Load VITS model
    tts = TTS(model_name="tts_models/en/vctk/vits").to("cpu")

    # Generate audio
    audio_output = tts.tts(text, speed=1, speaker='p228')
    
    logging.info("Speech generation completed successfully.")

    # Play audio in real-time
    response_spoken = sd.play(np.array(audio_output), samplerate=22050)
    sd.wait()
    return response_spoken

if __name__ == "__main__":
    speech_model("You are doing great! Keep going.")
