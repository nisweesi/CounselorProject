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
genai.configure(api_key='AIzaSyB6xGpFdylTilpEJJOugCSrZvU26PfiMko')
model = genai.GenerativeModel('gemini-pro')

recognizer = sr.Recognizer()

class ConversationBot:
    def __init__(self, detector):
        self.model = genai.GenerativeModel('gemini-pro')
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
                    "Let me share something uplifting with you!",
                    "I believe there's always a silver lining.",
                    "Here's a positive way to look at this situation."
                ],
                'listener_phrases': [
                    "I'm here to listen and find the bright side together.",
                    "Please share your thoughts. I’m sure we can find something good in this.",
                    "I’d love to hear your perspective and help you see the positives!"
                ],
                'affirmations': [
                    "You're doing an amazing job handling this!",
                    "That’s such a thoughtful way to approach things!",
                    "I can see how much effort you’re putting into this. Keep it up!"
                ]
            },
            'neutral': {
                'rate': 160,
                'volume': 0.8,
                'speaker_phrases': [
                    "Let’s look at this from a balanced perspective.",
                    "Here’s a neutral way of approaching this topic.",
                    "Let’s discuss this objectively and see where it leads us."
                ],
                'listener_phrases': [
                    "I’m here to understand your point of view without judgment.",
                    "Please share your thoughts. I’d like to understand better.",
                    "I’m listening carefully to what you’re saying."
                ],
                'affirmations': [
                    "That’s a fair point. Thank you for sharing.",
                    "I can see where you’re coming from.",
                    "You’ve explained that really well."
                ]
            },
            'pessimistic': {
                'rate': 150,
                'volume': 0.7,
                'speaker_phrases': [
                    "Let me share what concerns me about this situation.",
                    "Here’s something that might be worth worrying about.",
                    "I feel there are some challenges we need to address."
                ],
                'listener_phrases': [
                    "I’m listening, even if things feel tough right now.",
                    "Please share your concerns. I know it’s not easy to talk about these things.",
                    "I’m here to hear what’s on your mind, even if it’s difficult."
                ],
                'affirmations': [
                    "It’s okay to feel uncertain—these situations are tough.",
                    "You’re handling this better than most would in such circumstances.",
                    "It’s normal to feel overwhelmed sometimes. You’re doing your best."
                ]
            }
        }

        # Set speech rate and volume based on personality
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
            prompt = (
                f"As a listener practicing Speaker-Listener Technique (SLT), "
                f"paraphrase what you heard from the speaker in a clear, empathetic way. "
                f"Focus on reflecting both content and emotion without adding new information "
                f"or your own opinions. Speaker's text: '{text}'"
                f"Current detected emotion: {self.current_emotion}"
            )
            response = self.model.generate_content(prompt)
            return f"Let me reflect what I heard: {response.text}"
        except Exception:
            return None


    def generate_response(self, user_input):
        prompt = (
            f"Given the following conversation context:\n"
            f"{json.dumps(self.context, indent=2)}\n"
            f"User: {user_input}\n"
            f"Current task: {self.current_task}\n"
            f"Bot's character: {json.dumps(self.character, indent=2)}\n"
            f"User's current emotion: {self.current_emotion}\n"
            f"Provide a concise response of around 25 words or fewer, unless additional detail is necessary to fully address the user's request."
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

        # Limit response to 25 words
        words = response.split()
        if len(words) > 25 and not self.is_detailed_response_needed(user_input):
            response = ' '.join(words[:25])

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
        self.speak_text("Welcome to the Charisma Conversation Bot!")
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

            # Always paraphrase in listener role
            if self.speaker_listener_role == "listener":
                try:
                    paraphrase = self.paraphrase(user_input)
                    self.speak_text(f"Let me reflect what I heard: {paraphrase}")
                    self.speak_text("Did I capture that correctly?")
                except Exception as e:
                    print(f"Error in paraphrasing: {e}")
                    continue
                    
                # Append to conversation history
                self.conversation_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "speaker": "user",
                    "message": user_input,
                    "response": paraphrase
                })
                
            # Only switch roles occasionally when appropriate    
            if not user_input.endswith('?') and random.random() < 0.3:
                self.speak_text(self.switch_role()) 

    def save_conversation(self):
        df = pd.DataFrame(self.conversation_history)
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"\nConversation saved to {filename}")

if __name__ == "__main__":
    bot = ConversationBot()
    bot.main_loop()