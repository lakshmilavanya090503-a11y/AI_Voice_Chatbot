import os
import requests
import json
import time

def handler(request):
    try:
        body = request.get_json()
        user_message = body.get("message", "").strip()

        if not user_message:
            return {
                "statusCode": 200,
                "body": json.dumps({"reply": "Enter message"})
            }

        if len(user_message) > 300:
            return {
                "statusCode": 200,
                "body": json.dumps({"reply": "Too long"})
            }

        time.sleep(1)  # anti-spam

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
            reply = "API error"
        else:
            reply = response.json()["choices"][0]["message"]["content"]

        return {
            "statusCode": 200,
            "body": json.dumps({"reply": reply})
        }

    except Exception:
        return {
            "statusCode": 200,
            "body": json.dumps({"reply": "Server error"})
        }
