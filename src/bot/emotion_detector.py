from llm.llm_api import LLMApi

llm_api = LLMApi(provider="gemini")  # Uses Google Gemini API

def detect_emotion(text):
    """Analyze text for emotional tone."""
    emotion_prompt = f"Analyze this text for emotion: '{text}'"
    emotion_response = llm_api.generate_response([{"role": "user", "content": emotion_prompt}])
    
    return emotion_response.strip().lower() if emotion_response else "neutral"
