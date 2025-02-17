import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

LLM_CONFIG = {
    "openai": {
        "api_key": os.getenv("CHATGPT_API"),
        "model": "gpt-4o-latest"
    },
    "deepseek": {
        "api_key": os.getenv("DEEPSEEKAPI"),
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat"
    },
    "grok": {
        "api_key": os.getenv("GROK_API"),
        "base_url": "https://api.x.ai/v1",
        "model": "grok-2-latest"
    },
    "gemini": {
        "api_key": os.getenv("GEMINI_API"),
        "model": "gemini-pro"
    }
}
