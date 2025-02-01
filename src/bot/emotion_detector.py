from llm.llm_api import LLMApi

llm_api = LLMApi()

def detect_emotion(text):
    emotion_prompt = f"Analyze this text for emotion: '{text}'"
    emotion_response = llm_api.generate_content(emotion_prompt)
    return emotion_response.strip().lower()
