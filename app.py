import os
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)  # Enable CORS
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket

API_URL = os.getenv("API_URL", "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0")
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("Missing API_KEY! Set it in Railway environment variables.")

HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Store chat messages
chat_messages = []

@app.route('/')
def home():
    return "🚀 AI Image Generator API & Chat is running!"

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt})

        if response.status_code == 200:
            image_path = "output.png"
            with open(image_path, "wb") as f:
                f.write(response.content)
            return send_file(image_path, mimetype="image/png")

        return jsonify({"error": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# WebSocket event for handling chat messages
@socketio.on("send_message")
def handle_message(data):
    username = data.get("username", "Anonymous")
    message = data.get("message", "")

    if message:
        chat_messages.append({"username": username, "message": message})
        emit("receive_message", {"username": username, "message": message}, broadcast=True)  # Send to all clients

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), allow_unsafe_werkzeug=True)
