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

openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2023-12-01-preview"

# Override OpenAI request session to disable SSL verification
openai.requestssession = requests.Session()
openai.requestssession.verify = False  # Disable SSL verification

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
        response = openai.ChatCompletion.create(
            deployment_id=AZURE_DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": user_input}],
            request_timeout=30
        )

        bot_reply = response["choices"][0]["message"]["content"]

        return jsonify({
            "response": bot_reply,
            "source_ip": source_ip,
            "destination_ip": destination_ip
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
