import os
import random
import instaloader
import json

SAVE_DIR = "INSTA"
SESSION_FILE = "data/session-1.million.11"
LOG_FILE = "data/posted.json"
TARGET_ACCOUNTS = ["one_billion_academy", "arabtrillionaire", "the.millionaire.man1"]

# إنشاء مجلد التحميل
os.makedirs(SAVE_DIR, exist_ok=True)

# تحميل سجل المنشورات السابقة
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        posted = set(json.load(f))
else:
    posted = set()

# تحميل الجلسة
L = instaloader.Instaloader(dirname_pattern=SAVE_DIR, save_metadata=False, download_comments=False)
USERNAME = "1.million.11"
L.load_session_from_file(USERNAME, filename=SESSION_FILE)

# تحميل ريلزات عشوائية من الحسابات
random.shuffle(TARGET_ACCOUNTS)
count = 0

for account in TARGET_ACCOUNTS:
    print(f"📥 تحميل من @{account}...")
    try:
        profile = instaloader.Profile.from_username(L.context, account)
        posts = list(profile.get_posts())
        random.shuffle(posts)

        for post in posts:
            if not post.is_video or post.typename != "GraphVideo":
                continue  # تخطي الصور والمنشورات غير الفيديو

            shortcode = post.shortcode
            if shortcode in posted:
                continue

            # تحميل المنشور
            L.download_post(post, target=os.path.join(SAVE_DIR, account))
            posted.add(shortcode)
            count += 1

            # حفظ التحديثات
            with open(LOG_FILE, "w") as f:
                json.dump(list(posted), f)

            print(f"✅ تم تحميل: {shortcode}")
            break

    except Exception as e:
        print(f"⚠️ خطأ في @{account}: {e}")

print(f"\n✅ تم تحميل {count} ريلز في مجلد {SAVE_DIR}")
