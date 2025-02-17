import unittest
from llm.llm_api import LLMApi

class TestLLMApi(unittest.TestCase):

    def setUp(self):
        """Initialize LLM API instances"""
        self.openai_api = LLMApi(provider="openai")
        self.deepseek_api = LLMApi(provider="deepseek")
        self.grok_api = LLMApi(provider="grok")
        self.gemini_api = LLMApi(provider="gemini")

    def test_generate_response_openai(self):
        """Test OpenAI response generation"""
        messages = [{"role": "user", "content": "Hello, how are you?"}]
        response = self.openai_api.generate_response(messages)
        self.assertIsInstance(response, str)

    def test_generate_response_deepseek(self):
        """Test DeepSeek response generation"""
        messages = [{"role": "user", "content": "Tell me a joke."}]
        response = self.deepseek_api.generate_response(messages)
        self.assertIsInstance(response, str)

    def test_generate_response_grok(self):
        """Test Grok response generation"""
        messages = [{"role": "user", "content": "What is AI?"}]
        response = self.grok_api.generate_response(messages)
        self.assertIsInstance(response, str)

    def test_generate_response_gemini(self):
        """Test Google Gemini response generation"""
        messages = [{"role": "user", "content": "What is reinforcement learning?"}]
        response = self.gemini_api.generate_response(messages)
        self.assertIsInstance(response, str)

if __name__ == "__main__":
    unittest.main()
