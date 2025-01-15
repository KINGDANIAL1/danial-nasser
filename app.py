import os
import re
import time
import requests
from flask import Flask, request
from threading import Thread

# تعيين القيم من متغيرات البيئة
API_TOKEN = os.getenv("API_TOKEN")  # يجب وضع توكن البوت في متغير البيئة
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # رابط الويب هوك العام (HTTPS مطلوب)
PORT = int(os.getenv("PORT", 5000))  # المنفذ الافتراضي 5000

# التأكد من وجود API_TOKEN و WEBHOOK_URL
if not API_TOKEN or not WEBHOOK_URL:
    raise ValueError("يجب تحديد API_TOKEN و WEBHOOK_URL في متغيرات البيئة.")

app = Flask(__name__)

def set_webhook():
    """إعداد Webhook للبوت على Telegram."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/setWebhook"
    payload = {"url": f"{WEBHOOK_URL}/{API_TOKEN}"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ تم إعداد Webhook بنجاح: {WEBHOOK_URL}/{API_TOKEN}")
    except requests.exceptions.RequestException as e:
        print(f"❌ فشل في إعداد Webhook: {e}")

def send_message(chat_id, text):
    """إرسال رسالة إلى مستخدم Telegram."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ فشل في إرسال الرسالة: {e}")

def get_video_duration(video_url):
    """محاكاة الحصول على مدة الفيديو."""
    return 300  # مدة الفيديو بالثواني (5 دقائق)

def create_account_for_viewer(chat_id):
    """محاكاة إنشاء حساب لكل مشاهدة."""
    # هنا يتم إضافة منطق إنشاء حساب جديد
    print(f"🔑 إنشاء حساب جديد للمستخدم {chat_id}...")
    # يمكنك هنا إضافة المزيد من التفاصيل حول عملية إنشاء الحساب
    send_message(chat_id, "✅ تم إنشاء حسابك بنجاح! استمتع بمشاهدتك.")

def increase_views(video_url, views_count, chat_id):
    """محاكاة زيادة المشاهدات على فيديو YouTube."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    video_duration = get_video_duration(video_url)
    for i in range(views_count):
        try:
            # محاكاة إنشاء حساب للمستخدم عند أول مشاهدة
            create_account_for_viewer(chat_id)
            response = requests.get(video_url, headers=headers)
            if response.status_code == 200:
                print(f"✅ تمت مشاهدة الفيديو ({i + 1}/{views_count})")
                time.sleep(video_duration)  # الانتظار لمدة الفيديو
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
        send_message(chat_id, "مرحبًا! أرسل رابط الفيديو وعدد المشاهدات المطلوبة بصيغة:\n`رابط_الفيديو عدد_المشاهدات`\nمثال:\n`https://www.youtube.com/watch?v=example 100`")
    elif "youtube.com" in text or "youtu.be" in text:
        try:
            # استخدام regex للتحقق من صحة الرابط
            parts = text.split(maxsplit=1)
            if len(parts) != 2:
                raise ValueError("صيغة غير صحيحة! تأكد من إرسال الرابط مع عدد المشاهدات.")

            video_url, views_count = parts
            if not re.match(r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+", video_url):
                raise ValueError("الرابط غير صالح! تأكد من استخدام رابط يوتيوب صحيح.")

            views_count = int(views_count)
            if views_count <= 0:
                raise ValueError("عدد المشاهدات يجب أن يكون رقمًا صحيحًا أكبر من 0.")

            send_message(chat_id, f"✅ تم بدء زيادة المشاهدات على الفيديو:\n{video_url}\n📈 العدد المطلوب: {views_count}")

            # تشغيل عملية المشاهدات في Thread لتجنب تعليق الخادم
            Thread(target=increase_views, args=(video_url, views_count, chat_id)).start()
        except ValueError as ve:
            send_message(chat_id, f"❌ خطأ في الصيغة: {ve}")
        except Exception as e:
            send_message(chat_id, f"❌ حدث خطأ: {e}")
    else:
        send_message(chat_id, "❌ صيغة غير صحيحة! أرسل رابط الفيديو وعدد المشاهدات المطلوبة.")

    return "OK", 200

if __name__ == "__main__":
    print(f"✅ بدء تشغيل التطبيق على المنفذ {PORT}...")
    set_webhook()  # إعداد Webhook عند بدء التشغيل
    app.run(host="0.0.0.0", port=PORT)
