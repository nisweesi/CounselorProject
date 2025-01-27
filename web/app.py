from flask import Flask, request, jsonify, render_template
from src.conversation_bot.conversation_bot import ConversationBot

app = Flask(__name__)
bot = ConversationBot()

@app.route("/")
def home():
    """Render the chat UI."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot responses and stores conversation in memory."""
    data = request.get_json()
    user_input = data.get("message", "")

    # Generate a response using the AI model
    ai_response = bot.generate_response(user_input)

    return jsonify({"response": ai_response})
    

@app.route("/speak", methods=["POST"])
def speak():
    """Make the chatbot speak a given text."""
    data = request.get_json()
    text_to_speak = data.get("message", "")
    
    bot.speak_text(text_to_speak)
    
    return jsonify({"status": "Speaking completed"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
