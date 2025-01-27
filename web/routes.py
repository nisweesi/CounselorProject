from flask import Blueprint, request, jsonify
from src.conversation_bot import chat_with_ai

routes = Blueprint("routes", __name__)

@routes.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    response = chat_with_ai(user_input)
    return jsonify({"response": response})