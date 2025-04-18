# src/speech/speech_handler.py

import speech_recognition as sr
import time
import os
from datetime import timedelta, datetime
import threading
from queue import Queue, Empty

recognizer = sr.Recognizer()
stop_listening = False
mutex = threading.Lock()
audio_data = Queue(maxsize=1000)
time_queue = Queue(maxsize=1000)

EXIT_KEYWORD = "fire extinguisher"

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (to use it as subtitles later)"""
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{td.microseconds//1000:03d}"

def listen_1(input=None):
    if input == None:
        try:
            input = sr.Microphone()  # Initialize only when the function is called
        except OSError:
            print("No default input device available.")
            return None
    global stop_listening, audio_data, time_queue
    with input as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        while not stop_listening:
            mutex.acquire()
            print("THREAD 1 AQURIED")
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=60)
            mutex.release()
            print("THREAD 1 ENDED")
            audio_data.put(audio)
            time_queue.put(time.time())

def listen_2(input=None):
    if input == None:
        try:
            input = sr.Microphone()  # Initialize only when the function is called
        except OSError:
            print("No default input device available.")
            return None
    global stop_listening, audio_data, time_queue
    with input as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        while not stop_listening:
            mutex.acquire()
            print("THREAD 2 AQURIED")
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=60)
            mutex.release()
            print("THREAD 2 ENDED")
            audio_data.put(audio)
            time_queue.put(time.time())



def listen_for_speech():
    global stop_listening, audio_data, time_queue
    transcript_segments = []
    
    try:
        with sr.Microphone() as source:
            # listen ambient noise duration to 1 second for faster startup
            recognizer.adjust_for_ambient_noise(source, duration=1)

            start_time = time.time()
            segment_start_time = start_time
            segment_number = 1

            mic_thread1 = threading.Thread(target=listen_1)
            mic_thread2 = threading.Thread(target=listen_2)
            mic_thread1.start()
            mic_thread2.start()

            while not stop_listening:
                try:
                    audio = audio_data.get()
                    text = recognizer.recognize_google(audio)
                    yield {"text": text}  # send updates immediately

                    if EXIT_KEYWORD.lower() in text.lower():
                        stop_listening = True
                        break

                    current_time = time_queue.get()
                    segment = {
                        'number': segment_number,
                        'start_time': format_timestamp(segment_start_time - start_time),
                        'end_time': format_timestamp(current_time - start_time),
                        'text': text
                    }
                    
                    transcript_segments.append(segment)
                    print(f"Transcribed: {text}")
                    
                    segment_start_time = current_time
                    segment_number += 1

                except sr.RequestError as e:
                    print(f"Speech recognition service error: {e}")
                    continue
                except sr.WaitTimeoutError:
                    print("No speech detected, continuing to listen...")
                    continue
                except Exception as e:
                    print(f"Unexpected error during transcription: {e}")
                    continue
            mic_thread1.join()
            mic_thread2.join()
        if transcript_segments:
            save_transcript(transcript_segments)
            return " ".join(segment['text'] for segment in transcript_segments)
            
    except Exception as e:
        print(f"Error in speech recognition setup: {e}")
    
    return None

def start_recording():
    """Reset the stop_listening flag"""
    global stop_listening
    stop_listening = False
    print("Starting transcription...")
    print("Listening for speech...")
    listen_for_speech()

def stop_recording():
    """Set the stop_listening flag"""
    global stop_listening
    stop_listening = True

def get_flag():
    global stop_listening
    return stop_listening