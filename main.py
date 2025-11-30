import subprocess
import psutil
import time
import os
import urllib.request
import tarfile

# ----------------- الإعدادات -----------------
xmrig_url = "https://github.com/xmrig/xmrig/releases/download/v6.25.0/xmrig-6.25.0-linux-x64.tar.gz"
xmrig_dir = os.path.expanduser("~/xmrig")
wallet_address = "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e"
pools = [
    "pool.supportxmr.com:443"
]
threads_per_instance = 1

# ----------------- تحميل وفك ضغط XMRig إذا لم يكن موجود -----------------
if not os.path.exists(xmrig_dir):
    os.makedirs(xmrig_dir, exist_ok=True)
    print("تحميل XMRig...")
    tar_path = os.path.join(xmrig_dir, "xmrig.tar.gz")
    urllib.request.urlretrieve(xmrig_url, tar_path)
    print("فك ضغط XMRig...")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=xmrig_dir)
    os.remove(tar_path)

# البحث عن ملف التشغيل
xmrig_exe = None
for root, dirs, files in os.walk(xmrig_dir):
    for f in files:
        if f == "xmrig":
            xmrig_exe = os.path.join(root, f)
            break
    if xmrig_exe:
        break

if not xmrig_exe:
    raise FileNotFoundError("ملف XMRig لم يتم العثور عليه بعد التحميل.")

# التأكد من صلاحيات التشغيل
os.chmod(xmrig_exe, 0o755)

# ----------------- إعداد وتشغيل النسخ -----------------
total_threads = psutil.cpu_count(logical=True)
print(f"عدد الخيوط المنطقية: {total_threads}")

processes = []
instances = len(pools)  # عدد النسخ يساوي عدد المنافذ

for i in range(instances):
    start_thread = i * threads_per_instance
    end_thread = start_thread + threads_per_instance - 1

    if start_thread >= total_threads:
        print(f"تحذير: لا توجد خيوط كافية للنسخة {i+1}")
        break

    pool = pools[i]

    cmd = [
        xmrig_exe,
        "-o", pool,
        "-u", wallet_address,
        "-k",
        "--cpu-priority", "5",
        f"--cpu-affinity={start_thread}-{end_thread}"
    ]

    print(f"تشغيل النسخة {i+1} على الخيط {start_thread} بمنفذ {pool}")
    p = subprocess.Popen(cmd)
    processes.append(p)

    time.sleep(1)  # مهلة بسيطة

print("تم تشغيل جميع النسخ.")


