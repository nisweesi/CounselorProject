from .conversation_bot import ConversationBot
from .character_manager import select_character, get_personality_tone
from .emotion_detector import detect_emotion
from .response_generator import generate_response, paraphrase, generate_topic

__all__ = [
    'ConversationBot',
    'select_character',
    'get_personality_tone',
    'detect_emotion',
    'generate_response',
    'paraphrase',
    'generate_topic'
]
