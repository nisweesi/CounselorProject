# src/llm/llm_api.py
import google.generativeai as genai

class LLMApi:
    def __init__(self, model_name):
        self.model_name = model_name

    def generate_response(self, prompt):
        response = genai.generate_text(model=self.model_name, prompt=prompt)
        return response.result  
