from dotenv import load_dotenv
from conversation_bot.conversation_bot import ConversationBot
from speech.speech_detector import SpeechDetector

def main():
    load_dotenv()  # Load environment variables
    
    # Vosk model paths
    vosk_model_path = "../data/vosk_model/vosk_model_en_us_0.42_gigaspeech"
    spk_model_path = "../data/vosk_model/vosk_model_spk_0.4"
    
    # Initialize Speech Detector and the Conversation Bot
    detector = SpeechDetector(vosk_model_path, spk_model_path)
    bot = ConversationBot(detector)  # Pass detector to bot if needed for interruption

    print("Starting conversation. Speak into the microphone to begin. Say 'goodbye' to end.")
    
    # Run the main conversation loop
    bot.main_loop()  # All logic, including interruptions and goodbye, is now handled in ConversationBot

if __name__ == "__main__":
    main()