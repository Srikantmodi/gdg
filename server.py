from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable CORS for frontend communication
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Configure rate limiting (fixed issue)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["5 per minute"])

# Rasa Server URL
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

# Suppress aiohttp warnings (temporary workaround)
logging.getLogger("aiohttp").setLevel(logging.CRITICAL)


@app.route("/chat", methods=["POST"])
@limiter.limit("5 per minute")  # Prevent spam requests
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = requests.post(RASA_URL, json={"message": user_message})

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to get response from Rasa"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
