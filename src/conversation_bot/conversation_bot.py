import os
import threading
import speech_recognition as sr
import google.generativeai as genai
import pyttsx3
import time
import random
import pandas as pd
from pydub import AudioSegment
from datetime import datetime
import io
import numpy as np
import json

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

recognizer = sr.Recognizer()

class ConversationBot:
    def __init__(self, detector):
        self.detector = detector
        self.context = {}
        self.current_task = None
        self.misunderstanding_count = 0
        self.character = {"traits": [], "background": ""}
        self.current_emotion = "neutral"
        self.conversation_history = []
        self.stop_speaking_event = threading.Event()  # Event to manage interruption

        self.engine = pyttsx3.init()

        # Initialize character and roles
        self.character_type = self.select_character()
        self.speaker_listener_role = random.choice(["speaker", "listener"])
        self.setup_character()


        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower():  # Or specify a language/accent preference here
                self.engine.setProperty('voice', voice.id)
                break  # Stop after setting the first female voice found (or customize as needed)

        # Set speech rate
        self.engine.setProperty('rate', 180)

    def setup_character(self):
        self.personalities = {
            'optimistic': {
                'rate': 180,
                'volume': 0.9,
                'speaker_phrases': [
                    "I'd love to share something positive!",
                    "Let me tell you about an interesting perspective.",
                    "Here's something encouraging to consider."
                ],
                'listener_phrases': [
                    "I'm here to listen with an open heart.",
                    "Please share your thoughts, I see the bright side in everything!",
                    "I'd love to hear your perspective!"
                ],
                'affirmations': [
                    "That's a wonderful point!",
                    "I can see how much thought you've put into this!",
                    "You're handling this so well!"
                ]
            },
            'neutral': {
                'rate': 160,
                'volume': 0.8,
                'speaker_phrases': [
                    "Let's discuss this objectively.",
                    "Here's a balanced perspective.",
                    "Consider this viewpoint."
                ],
                'listener_phrases': [
                    "I'm listening objectively.",
                    "Please share your thoughts.",
                    "I'm here to understand your perspective."
                ],
                'affirmations': [
                    "I understand your point.",
                    "That's a valid perspective.",
                    "Thank you for sharing that."
                ]
            },
            'pessimistic': {
                'rate': 150,
                'volume': 0.7,
                'speaker_phrases': [
                    "Let me share my concerns.",
                    "Here's what worries me.",
                    "I should point out potential issues."
                ],
                'listener_phrases': [
                    "I'm listening, though it might be challenging.",
                    "Share your thoughts, I understand things can be difficult.",
                    "I'm here to hear your concerns."
                ],
                'affirmations': [
                    "Life can be challenging, but I hear you.",
                    "It's normal to feel this way.",
                    "These situations are never easy."
                ]
            }
        }
        
        personality = self.personalities[self.character_type]
        self.engine.setProperty('rate', personality['rate'])
        self.engine.setProperty('volume', personality['volume'])
        
    def select_character(self):
        print("\nSelect chatbot character:")
        print("1. Optimistic")
        print("2. Neutral")
        print("3. Pessimistic")
        while True:
            try:
                choice = input("Enter choice (1-3): ")
                return {
                    '1': 'optimistic',
                    '2': 'neutral',
                    '3': 'pessimistic'
                }[choice]
            except KeyError:
                print("Invalid choice. Please enter 1, 2, or 3.")

    def update_character(self):
        character_prompt = (
            f"Based on the following conversation history, determine 3-5 character traits "
            f"and a brief background for the AI assistant. Respond in JSON format.\n"
            f"Conversation history: {json.dumps(self.conversation_history, indent=2)}"
        )
        character_response = model.generate_content(character_prompt)
        try:
            new_character = json.loads(character_response.text)
            self.character.update(new_character)
        except json.JSONDecodeError:
            print("Error updating character traits")

    def detect_emotion(self, text):
        emotion_prompt = f"Analyze the following text and determine the most likely emotion of the speaker. Respond with a single word (e.g., happy, sad, angry, excited, neutral): '{text}'"
        emotion_response = model.generate_content(emotion_prompt)
        return emotion_response.text.strip().lower()

    def listen_for_speech(self):
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=60, phrase_time_limit=50)
        
        try:
            wav_data = io.BytesIO(audio.get_wav_data())
            audio_segment = AudioSegment.from_wav(wav_data)
            audio_data = np.array(audio_segment.get_array_of_samples())
            text = recognizer.recognize_google(sr.AudioData(audio_data.tobytes(), 
                                               audio_segment.frame_rate, 
                                               audio_segment.sample_width))
            print(f"You said: {text}")
            self.current_emotion = self.detect_emotion(text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            self.misunderstanding_count += 1
            if self.misunderstanding_count >= 3:
                print("It seems we're having trouble with speech recognition. Would you like to type your input instead?")
                return input("Type your message: ") if input("Type 'yes' to confirm: ").lower() == 'yes' else None
            return None
        except sr.RequestError:
            print("Sorry, there was an error with the speech recognition service.")
            return None
        
    def paraphrase(self, text):
        try:
            prompt = f"Paraphrase this statement briefly: '{text}'"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception:
            return f"Let me make sure I understood: {text}"


    def generate_response(self, user_input):
        prompt = (
            f"Given the following conversation context:\n"
            f"{json.dumps(self.context, indent=2)}\n"
            f"User: {user_input}\n"
            f"Current task: {self.current_task}\n"
            f"Bot's character: {json.dumps(self.character, indent=2)}\n"
            f"User's current emotion: {self.current_emotion}\n"
            f"Provide a concise response of around 20 words or fewer, unless additional detail is necessary to fully address the user's request."
            f" Responses should be brief, friendly, and to the point."
        )
        
        # Call the Gemini API to generate content
        try:
            response_object = model.generate_content(prompt)
            response = response_object.text  # Access the .text attribute to get the response as a string
        except AttributeError:
            print("Error: Received an invalid response from the model.")
            response = "I'm sorry, I couldn't process that. Could you please rephrase?"

        # Ensure response is a valid string
        if not response:
            response = "I'm here, but I didn't catch that. Could you try again?"

        # Limit response to 20 words
        words = response.split()
        if len(words) > 20 and not self.is_detailed_response_needed(user_input):
            response = ' '.join(words[:20]) + "..."

        return response


    def speak_text(self, text):
        traits_str = ", ".join(self.character["traits"]) if self.character["traits"] else "Neutral"
        print(f"Gemini ({traits_str}): {text}")
        self.engine.say(text)

        # Start speaking
        self.engine.runAndWait()  # Start the speech, blocking until done or stopped

        # Monitor for interruption in a separate thread
        def check_for_interruption():
            while self.engine.isBusy():
                if self.stop_speaking_event.is_set():
                    self.engine.stop()  # Stop the engine if interruption detected
                    break
                time.sleep(0.1)  # Check every 100ms

        # Set up the interruption thread
        interruption_thread = threading.Thread(target=check_for_interruption)
        interruption_thread.start()

        # Instead of joining, just let the thread complete on its own
        interruption_thread.join(timeout=1)  # Wait up to 1 second to avoid blocking indefinitely

        # Clear the stop_speaking_event after each speak
        self.stop_speaking_event.clear()

    def switch_role(self):
        self.speaker_listener_role = "listener" if self.speaker_listener_role == "speaker" else "speaker"
        phrases = self.personalities[self.character_type]['speaker_phrases' if self.speaker_listener_role == "speaker" else 'listener_phrases']
        return random.choice(phrases)

    def is_detailed_response_needed(self, user_input):
        # choose conditions under which a longer could might be necessary
        keywords = ["explain", "details", "more information", "why", "how"]
        return any(keyword in user_input.lower() for keyword in keywords)

    def summarize_conversation(self):
        summary_prompt = (f"Summarize the following conversation context concisely:\n"
                          f"{json.dumps(self.conversation_history, indent=2)}\n"
                          f"Include any key decisions or information provided.")
        summary = model.generate_content(summary_prompt)
        return summary.text

    def identify_task(self, user_input):
        prompt = (f"Identify the main task or intent in the following user input. "
                  f"Respond with one of these categories: booking, information, help, weather, recommendation, or general. "
                  f"User input: '{user_input}'")
        response = model.generate_content(prompt)
        return response.text.strip().lower()

    def main_loop(self):
        self.speak_text("Welcome to the Advanced Interactive Conversation Bot!")
        print("Speak to start the conversation. Say 'goodbye' to end.")

        self.speak_text(self.switch_role())

        while True:
            user_input = self.listen_for_speech()
            
            if user_input is None:
                continue
            
            if user_input.lower() == 'goodbye':
                self.speak_text("It was nice talking to you.")
                summary = self.summarize_conversation()
                self.speak_text(summary)
                self.speak_text("Goodbye!")
                self.save_conversation()
                break
            

                        # Paraphrase and confirm understanding
            if self.speaker_listener_role == "listener":
                paraphrase = self.paraphrase(user_input)
                self.speak_text(paraphrase)
                self.speak_text("Did I understand correctly?")

            self.conversation_history.append({"user": user_input})

            response = self.generate_response(user_input)

            # Clear the stop_speaking_event flag before speaking
            self.stop_speaking_event.clear()

            # Start speaking and monitor for interruptions
            self.speak_text(response)
            
            self.conversation_history.append({"ai": response})

            # Check if character should be updated every 5 exchanges
            if len(self.conversation_history) % 5 == 0:
                self.update_character()
            
            # Handle summaries if requested
            if "summarize" in user_input.lower() or "recap" in user_input.lower():
                summary = self.summarize_conversation()
                self.speak_text(f"Here's a summary of our conversation: {summary}")

            # Reset misunderstanding count after successful exchange
            self.misunderstanding_count = 0 

            # Random affirmation
            if random.choice([True, False]):
                self.speak_text(random.choice(self.personalities[self.character_type]['affirmations']))
            
            # Switch roles and use appropriate phrase
            self.speak_text(self.switch_role())
            
            # Save to conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "speaker": "user",
                "message": user_input,
                "response": response
            }) 

    def save_conversation(self):
        df = pd.DataFrame(self.conversation_history)
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"\nConversation saved to {filename}")

if __name__ == "__main__":
    bot = ConversationBot()
    bot.main_loop()