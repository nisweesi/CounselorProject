from llm.llm_api import LLMApi

<<<<<<< Updated upstream
def detect_emotion(text, provider="gemini"):
    """Analyze text for emotional tone with a selectable LLM provider."""
    llm_api = LLMApi(provider=provider)
    emotion_prompt = f"Analyze the following text for emotion and return JSON {{'emotion': ..., 'confidence': ...}}: '{text}'"
    
    emotion_response = llm_api.generate_response([{"role": "user", "content": emotion_prompt}])
    
    return emotion_response if emotion_response else {"emotion": "neutral", "confidence": 0.5}

=======
llm_api = LLMApi(provider="gemini")  # Uses Google Gemini API

def detect_emotion(text):
    """Analyze text for emotional tone."""
    emotion_prompt = f"Analyze this text for emotion: '{text}'"
    emotion_response = llm_api.generate_response([{"role": "user", "content": emotion_prompt}])
    
    return emotion_response.strip().lower() if emotion_response else "neutral"
>>>>>>> Stashed changes
