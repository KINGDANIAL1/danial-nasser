import os
import re
import time
import requests
from flask import Flask, request
from threading import Thread

API_TOKEN = os.getenv("API_TOKEN", "YOUR_BOT_API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-application-url.com")
PORT = int(os.getenv("PORT", 5000))

app = Flask(__name__)
active_views = {}

def set_webhook():
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    payload = {"url": f"{WEBHOOK_URL}/{API_TOKEN}"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ Webhook set successfully: {WEBHOOK_URL}/{API_TOKEN}")
    except Exception as e:
        print(f"❌ Failed to set Webhook: {e}")

def send_message(chat_id, text, reply_markup=None):
    if not text or not text.strip():
        print("❌ Empty message text.")
        return
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "reply_markup": reply_markup}
    
    # إضافة سجل لتتبع البيانات المرسلة
    print(f"Sending message to chat_id {chat_id} with payload: {payload}")  # سجل لعرض البيانات المرسلة
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Message sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

def get_video_duration(video_url):
    return 600

def skip_advertisement():
    print("⏩ Skipping advertisement...")
    time.sleep(30)

def increase_views(video_url, views_count, chat_id):
    headers = {"User-Agent": "Mozilla/5.0"}
    video_duration = get_video_duration(video_url)

    for i in range(views_count):
        if active_views.get(chat_id) == "stopped":
            send_message(chat_id, "❌ Process stopped by the user.")
            return
        try:
            response = requests.get(video_url, headers=headers)
            if response.status_code == 200:
                print(f"✅ Video viewed ({i + 1}/{views_count})")
                skip_advertisement()
                time.sleep(video_duration)
            else:
                print(f"❌ Failed to load video. Status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error during view increase ({i + 1}): {e}")

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "No message data", 400

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    if text.startswith("/start"):
        send_message(chat_id, "مرحبًا! أرسل رابط الفيديو وعدد المشاهدات المطلوبة بصيغة:\n`رابط_الفيديو عدد_المشاهدات`\nمثال:\n`https://www.youtube.com/watch?v=example 100`")
    elif "youtube.com" in text or "youtu.be" in text:
        try:
            parts = text.split(maxsplit=1)
            if len(parts) != 2:
                raise ValueError("صيغة غير صحيحة! تأكد من إرسال الرابط مع عدد المشاهدات.")
            
            video_url, views_count = parts
            if not re.match(r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]+$", video_url):
                raise ValueError("الرابط غير صالح! تأكد من استخدام رابط يوتيوب صحيح.")

            views_count = int(views_count)
            if views_count <= 0:
                raise ValueError("عدد المشاهدات يجب أن يكون رقمًا صحيحًا أكبر من 0.")
            
            active_views[chat_id] = "active"
            send_message(chat_id, f"✅ بدء عملية زيادة المشاهدات:\n{video_url}\n📈 العدد المطلوب: {views_count}")

            Thread(target=increase_views, args=(video_url, views_count, chat_id)).start()

        except ValueError as ve:
            send_message(chat_id, f"❌ صيغة خاطئة: {ve}")
        except Exception as e:
            send_message(chat_id, f"❌ حدث خطأ: {e}")
    elif text.lower() == "stop":
        active_views[chat_id] = "stopped"
        send_message(chat_id, "✅ تم إيقاف العملية.")
    else:
        send_message(chat_id, "❌ صيغة غير صحيحة!")

    return "OK", 200

if __name__ == "__main__":
    print(f"✅ Starting app on port {PORT}...")
    set_webhook()
    app.run(host="0.0.0.0", port=PORT)
