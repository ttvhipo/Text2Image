import os
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get API credentials from Railway environment variables
API_URL = os.getenv("API_URL", "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0")
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("Missing API_KEY! Set it in Railway environment variables.")

HEADERS = {"Authorization": f"Bearer {API_KEY}"}

@app.route('/')
def home():
    return "🚀 AI Image Generator API is running!"

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        print(f"🔹 Received prompt: {prompt}")

        # Send request to Hugging Face API
        response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt})

        print(f"🔹 API Response Status: {response.status_code}")
        print(f"🔹 API Response Content: {response.text[:500]}")

        if response.status_code == 200:
            image_path = "output.png"
            with open(image_path, "wb") as f:
                f.write(response.content)
            return send_file(image_path, mimetype="image/png")

        return jsonify({"error": response.text}), response.status_code

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
