import os, subprocess, zipfile, sys, shutil, time

launch_path = os.path.dirname(os.path.abspath(__file__))

try: os.mkdir(os.path.join(launch_path, "data"))
except Exception: pass
try: os.mkdir(os.path.join(launch_path, "download"))
except Exception: pass
try: os.mkdir(os.path.join(launch_path, "driver"))
except Exception: pass

proc = subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "requests", "pillow", "audiotsm", "scipy", "numpy", "pytube3"])

import requests

def dl_it(p, s):
    if(len(s) > 0):
        req = requests.get(s, stream = True)
        if req.status_code < 300:
            with open(p, "wb") as f: 
                for chunk in req.iter_content(chunk_size=64000):
                    f.write(chunk)
        else: print("Couldn't download '{0}'".format(s))

def dl_list(d, l):
    for i in l:
        p = os.path.join(launch_path, d, i.split("/")[-1])
        if d == "": p = os.path.join(launch_path, i.split("/")[-1])

        dl_it(p, i)
        if p.endswith(".zip"):
            with zipfile.ZipFile(p, 'r') as zip_ref:
                   zip_ref.extractall(os.path.dirname(p))
            os.unlink(p)
        if p.endswith(".tar.gz"):
            with tarfile.open(p, "r:gz") as tar:
                tar.extractall()
            with tarfile.open(p[:-3], "r:") as tar:
                tar.extractall()
            os.unlink(p)
            os.unlink(p[:-3])

script = "https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/procrastinatorScript100.organized.py"
util = "https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/selenium_util.py"
jumpcutter = "https://raw.githubusercontent.com/carykh/jumpcutter/master/jumpcutter.py"

dl_list("", [jumpcutter, script, util])


file_db = "https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/data/file_db"
sources_stream = "https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/data/sources_stream"
sources_sync = "https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/data/sources_sync"
last_updated = "https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/data/last_updated"

dl_list("data", [sources_stream, sources_sync, file_db, last_updated])


if os.name == "nt":
    launcher = "https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/start-windows.bat"
    jclauncher = "https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/start-jumpcutter.bat"
    dl_list("", [launcher, jclauncher])

    url_gecko = "https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-win64.zip"
    url_chrome = "https://chromedriver.storage.googleapis.com/83.0.4103.14/chromedriver_win32.zip"

    obs = "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-25.0.4-Full-Installer-x64.exe"
    try:
        ff = subprocess.Popen("ffmpeg")
        ff.terminate()

        dl_list("", [obs])
    except Exception:
        ffmpeg = "https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20200420-cacdac8-win64-static.zip"
        dl_list("", [ffmpeg, obs])
        shutil.move(os.path.join(launch_path, ffmpeg.split("/")[-1][:-4]), os.path.join(os.environ["ProgramW6432"], "ffmpeg"))
    try: subprocess.check_call([os.path.join(launch_path, obs.split("/")[-1])])
    except subprocess.CalledProcessError: pass
    os.unlink(os.path.join(launch_path, obs.split("/")[-1]))

else:
    url_gecko = "https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz"
    url_chrome = "https://chromedriver.storage.googleapis.com/83.0.4103.14/chromedriver_linux64.zip"
    subprocess.check_call(['add-apt-repository', "ppa:obsproject/obs-studio"], executable="/bin/bash")
    subprocess.check_call(['apt-get', 'install', '-y', 'ffmpeg', 'obs-studio'], executable="/bin/bash")

dl_list("driver", [url_gecko, url_chrome])
