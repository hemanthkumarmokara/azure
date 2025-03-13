import openai
import os
import certifi
import re
import requests
import urllib3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Use latest SSL certificates
os.environ["SSL_CERT_FILE"] = certifi.where()

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Azure OpenAI API Details
AZURE_OPENAI_ENDPOINT = "https://hemanthazazureopnai.openai.azure.com/"
AZURE_OPENAI_API_KEY = ""  # Replace with actual key
AZURE_DEPLOYMENT_NAME = "gpt-4"

# Create an OpenAI client
client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2023-12-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Function to extract IP addresses
def extract_ips(text):
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    ips = re.findall(ip_pattern, text)
    return ips[:2]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "Message cannot be empty"}), 400

    extracted_ips = extract_ips(user_input)
    source_ip = extracted_ips[0] if len(extracted_ips) > 0 else "N/A"
    destination_ip = extracted_ips[1] if len(extracted_ips) > 1 else "N/A"

    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,  # Use "model" instead of "deployment_id"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            timeout=30
        )

        bot_reply = response.choices[0].message.content

        return jsonify({
            "response": bot_reply,
            "source_ip": source_ip,
            "destination_ip": destination_ip
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # Allows external access
