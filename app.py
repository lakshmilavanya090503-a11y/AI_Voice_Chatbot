from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import requests
import time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# 🔒 Restrict CORS (IMPORTANT)
CORS(app, resources={r"/chat": {"origins": "*"}})

# 🔒 Rate Limiter (CRITICAL)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per minute"]
)

chat_history = []

@app.route("/")
def home():
    return "Chatbot running 🚀"

def query_ai(user_message):
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            },
            timeout=10
        )

        if response.status_code != 200:
            return "⚠️ API error"

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception:
        return "⚠️ Server error"

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")   # 🔥 VERY IMPORTANT
def chat():
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Enter a message"})

    if len(user_message) > 300:   # 🔒 Prevent abuse
        return jsonify({"reply": "Message too long"})

    time.sleep(1)  # 🔒 Anti-spam delay

    ai_reply = query_ai(user_message)

    chat_history.append({
        "user": user_message,
        "ai": ai_reply
    })

    return jsonify({"reply": ai_reply})

@app.route("/clear", methods=["POST"])
def clear():
    chat_history.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
