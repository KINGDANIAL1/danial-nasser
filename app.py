# path: webhook_service.py

import os
import re
import time
import requests
from flask import Flask, request
from threading import Thread
from random import uniform, choice

# Constants for user-agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5735.110 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5043.102 Mobile Safari/537.36",
    # Add more user agents as needed
]

# Retrieve environment variables
API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 5000))

# Validate environment variables
if not API_TOKEN or not WEBHOOK_URL:
    raise ValueError("API_TOKEN and WEBHOOK_URL must be set as environment variables.")

app = Flask(__name__)

def set_webhook():
    """Setup Telegram webhook."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    payload = {"url": f"{WEBHOOK_URL}/{API_TOKEN}"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Webhook successfully set: {WEBHOOK_URL}/{API_TOKEN}")
    except requests.exceptions.RequestException as e:
        print(f"Error setting webhook: {e}")

def send_message(chat_id, text):
    """Send a message to Telegram user."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")

def get_video_duration(video_url):
    """Simulate fetching video duration."""
    return 300  # Replace with actual API or algorithm if needed.

def human_like_delay(base_time, variance=0.2):
    """Introduce human-like random delay."""
    time.sleep(uniform(base_time * (1 - variance), base_time * (1 + variance)))

def create_account_for_viewer(chat_id):
    """Simulate creating an account for viewing."""
    human_like_delay(2)  # Simulates human account creation
    send_message(chat_id, "Account successfully created. Enjoy viewing!")

def increase_views(video_url, views_count, chat_id):
    """Simulate increasing video views with human-like patterns."""
    for i in range(views_count):
        try:
            headers = {"User-Agent": choice(USER_AGENTS)}
            create_account_for_viewer(chat_id)
            response = requests.get(video_url, headers=headers)
            if response.status_code == 200:
                print(f"View {i + 1}/{views_count} successful.")
                send_message(chat_id, f"View {i + 1} completed.")
                human_like_delay(get_video_duration(video_url))
            else:
                print(f"Failed to view video. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error during view {i + 1}: {e}")

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    """Handle Telegram webhook."""
    data = request.get_json()
    if not data or "message" not in data:
        return "Invalid data", 400

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    if text.startswith("/start"):
        send_message(chat_id, "Welcome! Send the video URL and desired view count in the format:\n`<video_url> <view_count>`")
    elif re.match(r"(https?://)?(www\.)?(instagram\.com/p/|youtu\.be/|youtube\.com/watch\?v=)[\w-]+", text):
        try:
            video_url, views_count = text.rsplit(maxsplit=1)
            views_count = int(views_count)
            if views_count <= 0:
                raise ValueError("Views count must be positive.")
            send_message(chat_id, f"Starting to increase views for:\n{video_url}\nTarget: {views_count} views.")
            Thread(target=increase_views, args=(video_url, views_count, chat_id)).start()
        except Exception as e:
            send_message(chat_id, f"Error processing request: {e}")
    else:
        send_message(chat_id, "Invalid input! Please send a valid video URL and view count.")

    return "OK", 200

if __name__ == "__main__":
    print(f"Starting app on port {PORT}...")
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)
