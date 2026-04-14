from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

chat_history = []

@app.route("/")
def home():
    return render_template("index.html")

def query_ai(user_message):

    try:
        api_key = os.getenv("OPENROUTER_API_KEY")

        print("KEY START:", api_key[:10] if api_key else "None") 

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
            timeout=15 
        )

        print("STATUS:", response.status_code)
        print("TEXT:", response.text)

        if response.status_code != 200:
            return f"⚠️ API Error {response.status_code}"

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return "⚠️ Server error"
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
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
