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
<<<<<<< HEAD
genai.configure(api_key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
model = genai.GenerativeModel('gemini-pro')

recognizer = sr.Recognizer()

class ConversationBot:
    def __init__(self, detector):
        self.model = genai.GenerativeModel('gemini-pro')
        self.detector = detector
=======
# genai.configure(api_key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
# model = genai.GenerativeModel('gemini-pro')

class ConversationBot:
    def __init__(self):
>>>>>>> 11f12c4 (adding new LLMs and using VITs for speech)
        self.context = {}
        self.misunderstanding_count = 0
        self.character = {"traits": [], "background": ""}
        self.current_emotion = "neutral"
        self.conversation_history = []
        
        # Configure Gemini API
        genai.configure(api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize speech recognition and TTS
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        
        # Initialize character and role
        self.character_type = self.select_character()
        self.speaker_listener_role = random.choice(["speaker", "listener"])
<<<<<<< HEAD
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
=======
>>>>>>> 11f12c4 (adding new LLMs and using VITs for speech)
        
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
<<<<<<< HEAD
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
=======
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=20)
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except (sr.UnknownValueError, sr.RequestError):
                return None
>>>>>>> 11f12c4 (adding new LLMs and using VITs for speech)

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
<<<<<<< HEAD
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
=======
        personality_tone = {
            "pessimistic": "realistic but not overly negative",
            "optimistic": "positive and encouraging",
            "neutral": "balanced and objective"
        }
>>>>>>> 11f12c4 (adding new LLMs and using VITs for speech)

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

<<<<<<< HEAD
        # Limit response to 25 words
        words = response.split()
        if len(words) > 25 and not self.is_detailed_response_needed(user_input):
            response = ' '.join(words[:25])

        return response
=======
        Do not include any meta-text or explanations. Only provide the response statement itself.
        """
>>>>>>> 11f12c4 (adding new LLMs and using VITs for speech)

        response = self.model.generate_content(prompt)
        return response.text.strip()

    def speak_text(self, text):
        print(f"AI ({self.character_type}): {text}")
        self.engine.say(text)
<<<<<<< HEAD

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
=======
        self.engine.runAndWait()
>>>>>>> 11f12c4 (adding new LLMs and using VITs for speech)

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
