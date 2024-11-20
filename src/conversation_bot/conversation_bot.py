import os
import threading
import speech_recognition as sr
import google.generativeai as genai
import pyttsx3
import time
from pydub import AudioSegment
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

        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower():  # Or specify a language/accent preference here
                self.engine.setProperty('voice', voice.id)
                break  # Stop after setting the first female voice found (or customize as needed)

        # Set speech rate
        self.engine.setProperty('rate', 180)

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
        print(f"Welcome to the Advanced Interactive Conversation Bot!")
        print("Speak to start the conversation. Say 'goodbye' to end.")

        while True:
            user_input = self.listen_for_speech()
            
            if user_input is None:
                continue
            
            if user_input.lower() == 'goodbye':
                self.speak_text("It was nice talking to you. Here's a summary of our conversation:")
                summary = self.summarize_conversation()
                self.speak_text(summary)
                self.speak_text("Goodbye!")
                break
            
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

if __name__ == "__main__":
    bot = ConversationBot()
    bot.main_loop()