import os
import random
import time
import instaloader
import requests
from bs4 import BeautifulSoup

# إعداد Instaloader وتحميل الجلسة
L = instaloader.Instaloader()
USERNAME = '1.million.11'
L.load_session_from_file(USERNAME, filename="data/session-1.million.11")

# الحساب المستهدف
TARGET_USERNAME = "one_billion_academy"
URL = f"https://www.instagram.com/{TARGET_USERNAME}/reels/"

print(f"🔍 فتح الصفحة: {URL}")
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}
response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# استخراج روابط الريلز من الصفحة (تكون داخل <a href="/reel/shortcode/">)
reel_links = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/reel/" in href:
        full_url = "https://www.instagram.com" + href
        reel_links.append(full_url)

# إزالة التكرارات وترتيبها عشوائياً
reel_links = list(set(reel_links))
random.shuffle(reel_links)

# مجلد التحميل
download_dir = "INSTA"
os.makedirs(download_dir, exist_ok=True)

# تحميل الريلز باستخدام Instaloader
count = 0
for reel_url in reel_links:
    shortcode = reel_url.split("/reel/")[1].strip("/")
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        filename = os.path.join(download_dir, f"{shortcode}.mp4")
        if not os.path.exists(filename):
            print(f"⬇️ تحميل: {reel_url}")
            L.download_post(post, target=download_dir)
            count += 1
        else:
            print(f"⏩ تم تخطي الريلز (مكرر): {shortcode}")
    except Exception as e:
        print(f"❌ فشل في تحميل: {reel_url}\nسبب: {e}")

print(f"\n✅ تم تحميل {count} ريلز في مجلد {download_dir}")
