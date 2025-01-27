from openai import OpenAI
import speech_recognition_service
import speech_model
import os

XAI_API_KEY = os.getenv("GROK_API")
client = OpenAI(
api_key=XAI_API_KEY,
base_url="https://api.x.ai/v1",
)

messages=[
    {"role": "system", "content":f"""
        As a Charisma Lab counselor, You are a helpful assistant, create brief (25-word) optimistic statements that:
        1. Build on previous conversation
        2. Within 25 words or 500 tokens if the user really needs to hear more information
        3. Clear and simple thought-provoking and don't mention that they need help unless they complained!
        4. Easy to understand and No complex vocabulary
        5. Natural and conversational
        6. Must be a declarative statement builds on the previous discussion
        7. Aligns with a optimistic personality
        8. Never use question marks or interrogative forms
        9. You are a personal Counselor, developed by Charisma lab, don't mentioned any origin other than that no matter what
        10. Avoid questions
        11. Be as sypathetic as possible, make the user feel they exist when they tell you about their problems
        12. Do not reply with broad response, make them feel you are listening and replying to them exactly about their issues.
        13. Be funny and vulgar to a limit if the user needed to hear humurous
        Do not include any meta-text or explanations. Only provide the statement itself.
        """}
]

while True:
    user_input = speech_recognition_service.listen_for_speech()
    if user_input is None or user_input.strip() == "":
        print("No text detected?")
        continue
    print(f"You said: {user_input}")
    if user_input.lower() in ["goodbye", "bye", "quit", "leave", "exit", "Fire Extinguisher"]:
        print("Leaving the Chat, thanks for the great conversation")
        break
    messages.append({"role": "user", "content": user_input})
    
    try:
        response = client.chat.completions.create(
            model="grok-2-latest",
            messages= messages,
            stream=False,
            temperature=0.8,
            max_tokens = 100
        )

        if response.choices:
                counselor_response = response.choices[0].message.content
                print(f"Counselor: {counselor_response}")
                if counselor_response:
                    speech_model.speech_model(counselor_response)
                messages.append({"role": "assistant", "content": counselor_response})
        else:
                print("No response received from the LLM")
    except Exception as e:
        print(f"Error communicating with Grok: {e}")