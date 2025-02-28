# 1. How to Obtain the Source Code

## Clone the Repository
    
    git clone https://github.com/nisweesi/CounselorProject.git
    cd CounselorProject

# 2. Directory Structure.

Our main project structure is the following (MVC-style structure):

```
CounselorProject/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
├── bot/
│   ├── __init__.py
│   ├── character_manager.py
│   ├── conversation_bot.py
│   ├── emotion_detector.py
│   ├── response_generator.py
├── llm/
│   ├── __init__.py
│   ├── llm_api.py
│   ├── test_chatgpt_openai.py
│   ├── test_deep_seek.py
│   ├── test_gemini_google.py
│   ├── test_grok_xai.py
├── speech/
│   ├── __init__.py
│   ├── speech_detector.py
│   ├── speech_handler.py
│   ├── speech_model.py
│   ├── speech_recognition_service.py
├── tests/
│   ├── test_conversation.py
│   ├── test_flask_api.py
│   ├── test_llm_api.py
│   ├── test_speech.py
├── config.py
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
└── CHANGELOG.md
```

# 3. How to build the software

### Install dependencies
`pip install -r requirements.txt`
### Running the backend
`python src/main.py`

# 4. How to test the software

Work in progress

## Summarization

Work in progress
