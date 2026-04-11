from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

chat_history = []

@app.route("/")
def home():
    return render_template("index.html")

def query_ai(user_message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
        )

        data = response.json()
        print("DEBUG:", data)

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            print("API ERROR:", data)
            return "⚠️ API error, check terminal"

    except Exception as e:
        print("🔥 OpenRouter error:", e)
        return "⚠️ Error getting response"

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a message"})

    ai_reply = query_ai(user_message)

    chat_history.append({
        "user": user_message,
        "ai": ai_reply
    })

    return jsonify({"reply": ai_reply})

@app.route("/retry", methods=["POST"])
def retry():
    if not chat_history:
        return jsonify({"reply": "No previous message to retry."})

    last_user = chat_history[-1]["user"]
    ai_reply = query_ai(last_user)

    chat_history[-1]["ai"] = ai_reply

    return jsonify({"reply": ai_reply})

@app.route("/undo", methods=["POST"])
def undo():
    if chat_history:
        chat_history.pop()
        return jsonify({"status": "ok"})
    return jsonify({"status": "empty"})

@app.route("/clear", methods=["POST"])
def clear():
    chat_history.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)
