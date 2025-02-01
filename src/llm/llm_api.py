import google.generativeai as genai

class LLMApi:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key='AIzaSyB6xGpFdylTilpEJJOugCSrZvU26PfiMko')
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_content(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text

    def check_similarity(self, original, paraphrase):
        similarity_prompt = f"""
        Compare these statements and rate their similarity on a scale of 0 to 10:
        Original: {original}
        Paraphrase: {paraphrase}
        Consider partial matches and key concepts.
        Only respond with a number between 0 and 10.
        """
        similarity_check = self.generate_content(similarity_prompt)
        return float(similarity_check.strip())
