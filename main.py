import os
import random
import time
import tempfile
import json
from datetime import datetime
from instagrapi import Client
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# جلب متغيرات البيئة
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")

if not (IG_USERNAME and IG_PASSWORD and SERVICE_ACCOUNT_JSON):
    raise Exception("❌ يرجى تعيين المتغيرات IG_USERNAME و IG_PASSWORD و SERVICE_ACCOUNT_JSON في البيئة")

# إنشاء ملف JSON مؤقت لحساب Google Service
with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_file:
    tmp_file.write(SERVICE_ACCOUNT_JSON)
    tmp_file.flush()
    SERVICE_ACCOUNT_FILE = tmp_file.name

# إعداد Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

POSTED_LOG = "posted_from_drive.txt"

POST_CAPTIONS = [
    "🚀 انطلق بقوة كل يوم!",
    "🎯 هذا الفيديو فيه درس كبير.",
    "💡 شاركنا رأيك في التعليقات!",
    "🔥 محتوى مميز جدًا!"
]

STORY_CAPTIONS = [
    "✨ شاهد هذا الآن!",
    "🔥 لحظات لا تفوّت!",
    "🚀 المحتوى مستمر!",
    "📌 شوف الستوري الجديد!"
]

def load_posted():
    if not os.path.exists(POSTED_LOG):
        return set()
    with open(POSTED_LOG, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_posted(filename):
    with open(POSTED_LOG, "a", encoding="utf-8") as f:
        f.write(filename + "\n")

def get_videos_from_drive():
    query = "mimeType contains 'video/' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

def download_video(file):
    request = drive_service.files().get_media(fileId=file['id'])
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        downloader = MediaIoBaseDownload(tmp, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return tmp.name

def publish_post(client, file):
    caption = random.choice(POST_CAPTIONS)
    tmp_path = download_video(file)
    try:
        print(f"⬆️ نشر ريلز: {file['name']} مع وصف: {caption}")
        client.clip_upload(tmp_path, caption)
        save_posted(file['name'])
    except Exception as e:
        print(f"❌ فشل نشر {file['name']}: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def publish_story(client, file):
    caption = random.choice(STORY_CAPTIONS)
    tmp_path = download_video(file)
    try:
        print(f"⬆️ نشر ستوري: {file['name']} مع وصف: {caption}")
        client.video_upload_to_story(tmp_path, caption)
        save_posted(file['name'])
    except Exception as e:
        print(f"❌ فشل ستوري: {file['name']}: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def pick_available_videos(posted, n=1):
    all_files = get_videos_from_drive()
    available = [f for f in all_files if f['name'].lower().endswith('.mp4') and f['name'] not in posted]
    random.shuffle(available)
    return available[:n]

def main():
    print("🔐 تسجيل الدخول...")
    client = Client()
    client.login(IG_USERNAME, IG_PASSWORD)
    posted = load_posted()

    print("⏳ انتظار دقيقتين قبل بدء النشر...")
    time.sleep(240)

    files = pick_available_videos(posted, 3)
    if not files:
        print("🚫 لا توجد فيديوهات متاحة.")
        return

    print("🟢 بدء النشر بعد الانتظار...")

    try:
        # نشر ستوري
        publish_story(client, files[0])
        posted.add(files[0]['name'])

        # نشر 2 ريلز
        for file in files[1:]:
            publish_post(client, file)
            posted.add(file['name'])
            time.sleep(random.randint(30, 60))

    except Exception as e:
        print(f"❌ خطأ أثناء النشر: {e}")

    print("✅ تم تنفيذ النشر.")

if __name__ == "__main__":
    main()
