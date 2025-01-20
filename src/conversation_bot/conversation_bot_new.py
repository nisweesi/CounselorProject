import speech_recognition as sr
import google.generativeai as genai
import pyttsx3
import time
from pydub import AudioSegment
import io
import numpy as np
import json
import random
from datetime import datetime
import pandas as pd

# Configure Gemini API
# genai.configure(api_key='AIzaSyB6xGpFdylTilpEJJOugCSrZvU26PfiMko')
# model = genai.GenerativeModel('gemini-pro')

class ConversationBot:
    def __init__(self):
        self.context = {}
        self.misunderstanding_count = 0
        self.character = {"traits": [], "background": ""}
        self.current_emotion = "neutral"
        self.conversation_history = []
        
        # Configure Gemini API
        genai.configure(api_key='AIzaSyB6xGpFdylTilpEJJOugCSrZvU26PfiMko')
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize speech recognition and TTS
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        
        # Initialize character and role
        self.character_type = self.select_character()
        self.speaker_listener_role = random.choice(["speaker", "listener"])
        
    def select_character(self):
        print("\nSelect Bots Character:")
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

    def listener_mode(self):
        try:
            # Welcome Message
            self.speak_text("Hello! I am Charisma Bot. You have the floor; I am listening.")
            
            while True:
                # Listen for Speaker Input
                user_input = self.listen_for_speech()
                
                # Handle exit condition
                if user_input is None:
                    self.speak_text("I didn't catch that. Could you please repeat?")
                    continue
                if self.is_goodbye(user_input):
                    self.speak_text("It was nice talking to you! Goodbye!")
                    self.save_conversation()
                    return False
                
                if self.is_confirmation(user_input):
                    self.speak_text(self.generate_follow_up_response())
                    continue
                
                # Detect Emotion
                self.current_emotion = self.detect_emotion(user_input)
                
                # Paraphrase Speaker Input
                paraphrase = self.paraphrase(user_input)

                if paraphrase:
                    self.speak_text(paraphrase)
                    if not self.is_confirmation(user_input):
                        self.speak_text("Did I understand correctly?")
                        confirmation = self.listen_for_speech()
                        
                        if self.is_confirmation(confirmation):
                            response = self.generate_response(user_input)
                            self.speak_text(response)
                            self.conversation_history.append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "speaker": "user",
                                "message": user_input,
                                "response": response,
                                "emotion": self.current_emotion
                            })
                        else:
                            self.speak_text("I apologize. Could you please repeat that?")
                
                # Save conversation periodically
                if len(self.conversation_history) % 5 == 0:
                    self.save_conversation()
                    
        except Exception as e:
            print(f"Error in listener mode: {e}")
            self.save_conversation()
            return False
            
        return True
    
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

    def speaker_mode(self):
        try:
            self.speak_text("Hello! I am Charisma Bot. I will talk first, and you will listen.")
            while True:
                # Generate and store current statement
                current_statement = self.generate_topic()
                self.speak_text(current_statement)
                user_response = self.listen_for_speech()

                if user_response is None:
                    self.speak_text("I didn't catch that. Could you please repeat?")
                    continue
                    
                # Handle goodbye consistently
                if any(word in user_response.lower() for word in ['goodbye', 'bye', 'ok bye']):
                    self.speak_text("It was nice talking to you!")
                    self.save_conversation()
                    return False

                # Validate paraphrase
                similarity_prompt = f"""
                Compare these statements and rate their similarity on a scale of 0 to 10:
                Original: {current_statement}
                Paraphrase: {user_response}
                Consider partial matches and key concepts.
                Only respond with a number between 0 and 10.
                """
                similarity_check = self.model.generate_content(similarity_prompt)
                similarity_score = float(similarity_check.text.strip())

                if similarity_score >= 5:
                    self.speak_text("That's correct! Let's continue our discussion.")
                    self.conversation_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "speaker": "bot",
                        "statement": current_statement,
                        "listener_paraphrase": user_response,
                        "emotion": self.current_emotion
                    })
                else:
                    self.speak_text("That's not quite what I said. Let me repeat:")
                    self.speak_text(current_statement)  # Only repeat the current statement
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

            # Check for role switch
            if random.random() < 0.5:  # 50% chance to switch roles
                self.speaker_listener_role = "speaker" if self.speaker_listener_role == "listener" else "listener"
                self.speak_text(f"Let's switch roles. I will now be the {self.speaker_listener_role}.")

            # Save conversation state
            self.save_conversation()

    # Helper methods
    def detect_emotion(self, text):
        emotion_prompt = f"Analyze this text for emotion: '{text}'"
        emotion_response = self.model.generate_content(emotion_prompt)
        return emotion_response.text.strip().lower()

    def listen_for_speech(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=20)
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except (sr.UnknownValueError, sr.RequestError):
                return None

    def generate_topic(self):
        
        personality_tone = {
            "pessimistic": "realistic but not overly negative",
            "optimistic": "positive and hopeful",
            "neutral": "balanced and objective"
            }
        
        prompt = f"""
        Generate a single meaningful statement (NOT a question) that is:
        1. Within 25 words
        2. Clear and simple thought-provoking
        3. Easy to understand and No complex vocabulary
        4. Natural and conversational
        5. Must be a declarative statement
        6. Aligns with a {personality_tone[self.character_type]} personality
        7. Never use question marks or interrogative forms
        Do not include any meta-text or explanations. Only provide the statement itself.
        """
        response = self.model.generate_content(prompt)
        statement = response.text.strip()
        
        # Additional validation to ensure no questions
        if '?' in statement or statement.lower().startswith(('what', 'why', 'how', 'when', 'where', 'who', 'which')):
            # Fallback to a safe statement
            return "Personal growth comes from understanding different perspectives and experiences."
        return statement

    def generate_statement(self):
        prompt = f"""
        Generate a single follow-up meaningful statement (NOT a question) that is:
        1. Within 25 words
        2. Clear and simple thought-provoking
        3. Easy to understand and No complex vocabulary
        4. Natural and conversational
        5. Must be a declarative statement builds on the previous discussion
        6. Aligns with a {self.character_type} personality
        7. Never use question marks or interrogative forms
        Do not include any meta-text or explanations. Only provide the statement itself.
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def process_response(self, response):
        prompt = f"Process this response in the context of the current conversation: {response}"
        processed = self.model.generate_content(prompt)
        return processed.text

    def paraphrase(self, text):
        prompt = f"Paraphrase this text while maintaining its meaning in third person, start with 'You said': {text}"
        response = self.model.generate_content(prompt)
        return response.text

    def generate_response(self, user_input):
        personality_tone = {
            "pessimistic": "realistic but not overly negative",
            "optimistic": "positive and encouraging",
            "neutral": "balanced and objective"
        }

        prompt = f"""
        Generate a single response statement (NOT a question) that:
        1. Is within 20 words
        2. Acknowledges the user's input: '{user_input}'
        3. Is clear, simple, and easy to understand
        4. Uses natural and conversational language
        5. Is a declarative statement
        6. Aligns with a {personality_tone[self.character_type]} personality
        7. Adds a relevant comment to continue the conversation
        8. Never uses question marks or interrogative forms

        Do not include any meta-text or explanations. Only provide the response statement itself.
        """

        response = self.model.generate_content(prompt)
        return response.text.strip()

    def speak_text(self, text):
        print(f"AI ({self.character_type}): {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def save_conversation(self):
        df = pd.DataFrame(self.conversation_history)
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"\nConversation saved to {filename}")

    def main_loop(self):
        self.integrated_mode()

if __name__ == "__main__":
    bot = ConversationBot()
    bot.main_loop()
