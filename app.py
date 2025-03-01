import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Hugging Face API
API_URL = os.getenv("API_URL", "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0")
API_KEY = os.getenv("API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# imgbb API for image hosting (Replace with your API key from https://api.imgbb.com)
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

@app.route('/')
def home():
    return "AI Image Generator API is running!"

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        # Get prompt from request
        data = request.json
        prompt = data.get("prompt")

        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Send request to Hugging Face API
        response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt})

        if response.status_code == 200:
            image_path = "output.png"
            with open(image_path, "wb") as f:
                f.write(response.content)

            # Upload to imgbb
            with open(image_path, "rb") as f:
                res = requests.post("https://api.imgbb.com/1/upload", params={"key": IMGBB_API_KEY}, files={"image": f})
                res_json = res.json()

                if res.status_code == 200:
                    return jsonify({"image_url": res_json["data"]["url"]})
                else:
                    return jsonify({"error": "Image upload failed"}), 500

        return jsonify({"error": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
