import random
from datetime import datetime
import pandas as pd

from bot.character_manager import select_character
from bot.emotion_detector import detect_emotion
from bot.response_generator import generate_response, paraphrase, generate_topic
from speech.speech_handler import listen_for_speech, speak_text
from llm.llm_api import LLMApi

class ConversationBot:
    def __init__(self):
        self.context = {}
        self.misunderstanding_count = 0
        self.character = {"traits": [], "background": ""}
        self.current_emotion = "neutral"
        self.conversation_history = []
        self.llm_api = LLMApi()
        self.character_type = select_character()
        self.speaker_listener_role = random.choice(["speaker", "listener"])

    def listener_mode(self):
        try:
            speak_text("Hello! I am Charisma Bot. Can you please share your experience of this Human Robot Interaction Retreat? You have the floor; I am listening.")
            while True:
                user_input = listen_for_speech()
                if user_input is None:
                    speak_text("I didn't catch that. Could you please repeat?")
                    continue
                if self.is_goodbye(user_input):
                    speak_text("It was nice talking to you! Goodbye!")
                    self.save_conversation()
                    return False
                if self.is_confirmation(user_input):
                    speak_text(self.generate_follow_up_response())
                    continue

                self.current_emotion = detect_emotion(user_input)
                paraphrased = paraphrase(user_input)
                if paraphrased:
                    speak_text(paraphrased)
                    if not self.is_confirmation(user_input):
                        speak_text("Did I understand correctly?")
                        confirmation = listen_for_speech()
                        if self.is_confirmation(confirmation):
                            response = generate_response(user_input, self.character_type)
                            speak_text(response)
                            self.conversation_history.append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "speaker": "user",
                                "message": user_input,
                                "response": response,
                                "emotion": self.current_emotion
                            })
                        else:
                            speak_text("I apologize. Could you please repeat that?")

                if len(self.conversation_history) % 5 == 0:
                    self.save_conversation()
        except Exception as e:
            print(f"Error in listener mode: {e}")
            self.save_conversation()
            return False
        return True

    def speaker_mode(self):
        try:
            speak_text("Hello! I am Charisma Bot. I will talk first, and you will listen. You may share your experience of this Human Robot Meditation Retreat")
            while True:
                current_statement = generate_topic(self.character_type)
                speak_text(current_statement)
                user_response = listen_for_speech()
                if user_response is None:
                    speak_text("I didn't catch that. Could you please repeat?")
                    continue
                if self.is_goodbye(user_response):
                    speak_text("It was nice talking to you!")
                    self.save_conversation()
                    return False

                similarity_score = self.llm_api.check_similarity(current_statement, user_response)
                if similarity_score >= 5:
                    speak_text("That's correct! Let's continue our discussion.")
                    self.conversation_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "speaker": "bot",
                        "statement": current_statement,
                        "listener_paraphrase": user_response,
                        "emotion": self.current_emotion
                    })
                else:
                    speak_text("That's not quite what I said. Let me repeat:")
                    speak_text(current_statement)
                    break
        except Exception as e:
            print(f"Error in speaker mode: {e}")
            self.save_conversation()
            return False
        return True

    def integrated_mode(self):
        while True:
            if self.speaker_listener_role == "listener":
                if not self.listener_mode():
                    break
            else:
                if not self.speaker_mode():
                    break
            if random.random() < 0.5:
                self.speaker_listener_role = "speaker" if self.speaker_listener_role == "listener" else "listener"
                speak_text(f"Let's switch roles. I will now be the {self.speaker_listener_role}.")
            self.save_conversation()

    def is_confirmation(self, text):
        return text.lower() in ['yes', 'correct', 'right', 'that is correct', 'yes that is correct']

    def is_goodbye(self, text):
        return any(word in text.lower() for word in ['goodbye', 'bye', 'ok bye'])

    def generate_follow_up_response(self):
        prompts = [
            "Please continue sharing your thoughts.",
            "I'd love to hear more about it.",
            "Feel free to elaborate on that.",
            "Please go on, I'm listening attentively."
        ]
        return random.choice(prompts)

    def save_conversation(self):
        df = pd.DataFrame(self.conversation_history)
        filename = f"data/conversations/conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"\nConversation saved to {filename}")

    def main_loop(self):
        self.integrated_mode()

if __name__ == "__main__":
    bot = ConversationBot()
    bot.main_loop()
