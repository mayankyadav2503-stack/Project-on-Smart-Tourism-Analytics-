from flask import Blueprint, request, jsonify
import json
from services.chatbot_service import TourismChatbot

chat_bp = Blueprint("chat", __name__)
chatbot = TourismChatbot()

@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    user_id = data.get("user_id")
    response = chatbot.process_message(message, user_id)
    return jsonify(response)

@chat_bp.route("/api/chat/context", methods=["POST"])
def set_context():
    data = request.json
    chatbot.context.update(data.get("context", {}))
    return jsonify({"message": "Context updated"})
