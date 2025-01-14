import os
import requests
from flask import Flask, request
from threading import Thread

# تعيين القيم من متغيرات البيئة أو وضع القيم مباشرة
API_TOKEN = os.getenv("API_TOKEN", "ضع_التوكن_هنا")  # يجب وضع توكن البوت هنا
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app-url.com")  # رابط الويب هوك العام (HTTPS مطلوب)
PORT = int(os.getenv("PORT", 5000))  # المنفذ الافتراضي 5000

app = Flask(__name__)

def set_webhook():
    """إعداد Webhook للبوت على Telegram."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    payload = {"url": f"{WEBHOOK_URL}/{API_TOKEN}"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ تم إعداد Webhook بنجاح: {WEBHOOK_URL}/{API_TOKEN}")
    except Exception as e:
        print(f"❌ فشل في إعداد Webhook: {e}")

def send_message(chat_id, text):
    """إرسال رسالة إلى مستخدم Telegram."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ فشل في إرسال الرسالة: {e}")

def increase_views(video_url, views_count):
    """محاكاة زيادة المشاهدات على فيديو YouTube."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for i in range(views_count):
        try:
            response = requests.get(video_url, headers=headers)
            if response.status_code == 200:
                print(f"✅ تمت مشاهدة الفيديو ({i + 1}/{views_count})")
            else:
                print(f"❌ فشل تحميل الفيديو. رمز الحالة: {response.status_code}")
        except Exception as e:
            print(f"❌ خطأ أثناء زيادة المشاهدات ({i + 1}): {e}")

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    """معالجة الرسائل الواردة من Telegram."""
    data = request.get_json()
    if not data or "message" not in data:
        return "No message data", 400

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").strip()

    if text.startswith("/start"):
        send_message(chat_id, "مرحبًا! أرسل رابط الفيديو وعدد المشاهدات المطلوبة بصيغة:\n`رابط_الفيديو عدد_المشاهدات`")
    elif "youtube.com" in text or "youtu.be" in text:
        try:
            # تقسيم النص إلى الرابط وعدد المشاهدات
            parts = text.split()
            if len(parts) != 2:
                raise ValueError("صيغة غير صحيحة!")

            video_url, views_count = parts
            views_count = int(views_count)

            send_message(chat_id, f"✅ تم بدء زيادة المشاهدات على الفيديو:\n{video_url}\n📈 العدد المطلوب: {views_count}")

            # تشغيل عملية المشاهدات في Thread لتجنب تعليق الخادم
            Thread(target=increase_views, args=(video_url, views_count)).start()
        except Exception as e:
            send_message(chat_id, f"❌ حدث خطأ: {e}")
    else:
        send_message(chat_id, "❌ صيغة غير صحيحة! أرسل رابط الفيديو وعدد المشاهدات المطلوبة.")

    return "OK", 200

if __name__ == "__main__":
    print(f"✅ بدء تشغيل التطبيق على المنفذ {PORT}...")
    set_webhook()  # إعداد Webhook عند بدء التشغيل
    app.run(host="0.0.0.0", port=PORT)
