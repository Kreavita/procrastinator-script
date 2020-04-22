#------------------------------------------------
# Note: 
# -install 'Mozilla Firefox' and 'OBS Studio' for optimal compatibility and functionality (Chrome should work too)
# -Set Up OBS to save videos as .mkv, as the jumpcutter only takes mpeg videos and mp4 files can corrupt when OBS gets terminated by the script
# -The Jumpcutter Module only works with Python 3 (command: 'python3' on linux or 'python' on windows)
# 
# Install these Python Libraries: ('pip3 install' for Python 3 on Linux or 'pip install' for Windows & Python2 on Linux)
# core:         selenium requests
# jumpcutter:   pillow audiotsm scipy numpy pytube3
# 
# Install ffmpeg and add it to your PATH Variable
# 
# Script config:
#------------------------------------------------
STREAM_RECORDING = False # Do you wish to record scheduled streams? (True/False)
STREAM_DURATION = 1 # Duration of a Streaming session (in minutes)
OBS_OUTPUT = "C://User/name/Videos" # Path to the OBS recordings, you need to change this!
OBS_FPS = 60 # The framerate of your recordings. Set it to 0 and the script tries to detect it, but it wont always work
PATH_OBS = "C://Program Files/obs-studio/bin/64bit" # - Path to the obs64 executable, the screen recorder, you shouldnt change this on windows after a normal OBS installation

SYNC_ON_START = True # Do you wish to synchronize your local Directory when you start this Script? (True/False)
AUTO_JUMPCUT = False # Do you wish to automatically shorten video material by removing the silence parts ?

SCHEDULE_SYNC = True # Do you wish to schedule a daily sync of your local Directory and the specified Sources? (True/False)
SYNC_HOUR = 6 # The hour of the scheduled sync
SYNC_MINUTE = 00 # The minute of the scheduled sync

TUD_NAME = "Firstname Lastname" # Your Full name when connecting to bigbluebutton
TUD_USER = "username" # Your TU username to log in into OPAL / bigbluebutton
TUD_PASS = "password" # Your TU password

OTHER_LOGINS = [["user","pass"]] # If some of your 'other_sources' use HTTP Authentication, add the login credentials to this list

PROJECT_DIR = "My Uni Semester" # The Directory name where all Media Files will be organized
#------------------------------------------------
# Here begins the script
#------------------------------------------------
import os, time, re, requests, sys, subprocess, shutil
from selenium import webdriver, common as sel
from selenium_util import Util
from datetime import datetime, timedelta
from threading import Timer
requests.packages.urllib3.disable_warnings()
py2 = False

try:
    import _thread as thread  #Py3
    pass
except:
    import thread  #Py2
    reload(sys)
    sys.setdefaultencoding('UTF-8')
    py2 = True
    pass

launch_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(launch_path, PROJECT_DIR)

exe = ""
python = "python3"

if os.name == "nt": 
    exe = ".exe"
    python = "py"

util = Util(5)

sync_urls = []
sync_labels = []

stream_urls = []
stream_timestamps = []
stream_labels = []

file_db = {}
last_updated = 0

def main():
    global file_db, last_updated
    refresh_sources()
    for line in util.file_read(os.path.join(launch_path, 'data', 'last_updated')):
        try:
            last_updated = int(line)
        except:
            pass
    for line in util.file_read(os.path.join(launch_path, 'data', 'file_db')):
        if len(line) > 4:
            try:
                file_db[line.split(";")[0].strip()].append(line.split(";")[1].strip())
            except:
                file_db[line.split(";")[0].strip()] = [line.split(";")[1].strip()]

    if not os.path.exists(project_path):
        os.makedirs(project_path)
    for label in stream_labels + sync_labels:
        if not os.path.exists(os.path.join(project_path, *label.split("/"))):
            os.makedirs(os.path.join(project_path, *label.split("/")))
        if not label in file_db:
            file_db[label] = []

    if STREAM_RECORDING: thread.start_new_thread (stream_timer, ())
    if SCHEDULE_SYNC and not SYNC_ON_START: thread.start_new_thread (sync_timer, ())
    if SYNC_ON_START: sync_job()

    print("script init completed.")
    while STREAM_RECORDING or SCHEDULE_SYNC:
        if STREAM_RECORDING or SCHEDULE_SYNC: time.sleep(3600)
    
def refresh_sources():
    global sync_labels, sync_urls, stream_labels, stream_urls, stream_timestamps

    sync_labels = []
    sync_urls = []

    for line in util.file_read(os.path.join(launch_path, 'data', 'sources_sync')):
        if len(line) > 4:
            sync_labels.append(line.split(";")[0].strip())
            sync_urls.append(line.split(";")[1].strip())
    
    stream_labels = []
    stream_urls= []
    stream_timestamps = []
    
    for line in util.file_read(os.path.join(launch_path, 'data', 'sources_stream')):
        if len(line) > 4:
            stream_labels.append(line.split(";")[0].strip())
            stream_urls.append(line.split(";")[1].strip())
            stream_timestamps.append(time.mktime(datetime.strptime(line.split(";")[2].strip(), "%d.%m.%Y %H:%M:%S").timetuple()))

def stream_timer():
    i = 0
    cycle = True
    while  (i < len(stream_timestamps)) and cycle:
        if time.time() > stream_timestamps[i]:
            i = i + 1
        else:
            cycle = False
            print("Stream Timer: next Stream is scheduled at {0}".format(time.ctime(stream_timestamps[i])))
            delta_t = stream_timestamps[i] - time.time()

            t = Timer(delta_t, stream_runner, args=[i])
            t.start()
    if i == len(stream_timestamps): print("Stream Timer: no new upcoming stream found.")

def stream_runner(i):
    print("Stream Runner: starting stream record at: {0}".format(time.ctime(time.time())))

    with util.get_driver(False) as driver:
        driver.get(stream_urls[i])

        selenium_login(driver)
        try:
            driver.find_element_by_name("username").send_keys(TUD_NAME)
        except:
            print("Stream Runner: selenium: stream name skipped")
        try:
            driver.find_element_by_class_name("submit_btn").click()
        except:
            print("Stream Runner: selenium: stream name submit skipped")
        try:
            driver.find_element_by_class_name("icon-bbb-listen").click()
        except:
            print("Stream Runner: selenium: join button skipped")

        #time.sleep(STREAM_DURATION * 60)
        obs_record(STREAM_DURATION * 60)
    
    if os.path.exists(OBS_OUTPUT):
        vid = util.newest_file(OBS_OUTPUT)
        if vid.lower().endswith(".mkv") and os.path.getctime(vid) > stream_timestamps[i]:
            convert.append([vid, re.sub(".mkv", "_edit.mp4", vid, flags=re.IGNORECASE)])
            if AUTO_JUMPCUT: jumpcut_job(OBS_FPS)
    else:
        print("Stream Runner: WARNING: The OBS_OUTPUT directory could not be found, you have to manage the OBS Recording manually.")
    refresh_sources()
    stream_timer()

def selenium_login(driver):
    try:
        driver.find_element_by_name("j_username").send_keys(TUD_USER)
        driver.find_element_by_name("j_password").send_keys(TUD_PASS)
        driver.find_element_by_name("_eventId_proceed").click()
        driver.find_element_by_name("_eventId_proceed").click()
        time.sleep(2)
    except:
        print("selenium: stream login skipped")

def obs_record(duration):
    path_old = os.getcwd()
    os.chdir(PATH_OBS)

    obs = subprocess.Popen(["obs64" + exe, "--startrecording", "--scene \"Fullscreen\"", "--minimize-to-tray"])
    time.sleep(duration)
    obs.terminate()
    
    os.chdir(path_old)

convert = []

def jumpcut_job(fixedFPS):
    if not py2:
        global convert
        print("Jumpcut Job: {0} videos in the queue.".format(len(convert)))
        old_dir = os.getcwd()
        failed = 0
        os.chdir(launch_path)
        for vid in convert:
            prtstr = "Jumpcut Job: jumpcutting {0} of {1} : '{2}'...".format(convert.index(vid) + 1, len(convert), vid[0].split("/")[-1])
            util.inline_prt(prtstr)
            shutil.move(vid[0], os.path.join(launch_path, "i.mp4"))
            try: os.rmdir(os.path.join(launch_path, "TEMP"))
            except OSError as e: pass
            with open(os.devnull, 'wb') as FNULL:
                cmd = [python, "jumpcutter.py", "--input_file","i.mp4","--output_file", "o.mp4", "--silent_speed", "999999", "--sounded_speed", "1", "--frame_margin", "2", "--frame_quality", "1"]
                if fixedFPS > 0:
                    cmd.append("--frame_rate")
                    cmd.append(str(fixedFPS))
                jc = subprocess.Popen(cmd, stdout=FNULL, stderr=FNULL)                    
                jc.wait()
            if jc.returncode == 0:
                if os.path.isfile(vid[1]): os.unlink(vid[1])
                shutil.move(os.path.join(launch_path, "o.mp4"), vid[1])
            else:
                failed = failed + 1
                print("\nJumpcut Job: Jumpcutter failed for: {0}".format(vid[0].split("/")[-1]))
            shutil.move(os.path.join(launch_path, "i.mp4"), vid[0])
        os.chdir(old_dir)
        print("\nJumpcut Job: completed for {0} of {1} files. ({2} failed.)".format(len(convert) - failed, len(convert), failed))
    else:
        print("Jumpcut Job: 'jumpcutter.py' is not compatible with Python 2, please use Python 3!")
    convert = []

def sync_timer():
    x = datetime.today()
    y = x.replace(day = x.day, hour = SYNC_HOUR, minute = SYNC_MINUTE, second = 0, microsecond = 0) + timedelta(days = 1)
    delta_t = y - x
    print("Sync Timer: next Sync is scheduled at {0}".format(time.ctime(time.mktime(y.timetuple()))))
    t = Timer(delta_t.total_seconds(), sync_job)
    t.start()

def sync_job():
    global last_updated
    print ("Sync Job: {0} (last updated: {1})".format(time.ctime(time.time()), time.ctime(last_updated)))
    last_updated_unconfirmed = int(time.time())
    with util.get_driver(True) as driver:
        try:
            driver.get("https://bildungsportal.sachsen.de/opal/home/")
            
            driver.find_element_by_id("id13").click()
            driver.find_element_by_xpath("//select[@name='content:container:login:shibAuthForm:wayfselection']/option[text()='TU Dresden']").click()
            driver.find_element_by_name("content:container:login:shibAuthForm:shibLogin").click()

            selenium_login(driver)

        except (sel.exceptions.NoSuchElementException, sel.exceptions.WebDriverException):
            raise
            print("Sync Job Error: Opal-Login failed. Is the Website down?")

        for i in range(len(sync_urls)):
            sync_runner(i, driver)

    last_updated = last_updated_unconfirmed
    data = ""
    for label, files in file_db.items():
        for file in files:
            data = data + label + ";" + file.replace(";", "_") + "\n"
    if util.file_write(os.path.join(launch_path, "data", "file_db"), data) and util.file_write(os.path.join(launch_path, "data", "last_updated"), str(last_updated)): print("Database successfully updated. ")

    if AUTO_JUMPCUT: jumpcut_job(0)    
    
    if SCHEDULE_SYNC: 
        refresh_sources()
        sync_timer()

def sync_runner(i, driver):
    global file_db, convert
    href = sync_urls[i]
    req = requests.get(href, verify=False)
    if req.status_code == 401 or href.endswith(".pdf"):
        y = 0
        while req.status_code == 401 and y < len(OTHER_LOGINS):
            if req.status_code == 401: y = y + 1
            req = requests.get(sync_urls[i], auth=(OTHER_LOGINS[y][0], OTHER_LOGINS[y][1]), verify=False)
        if req.status_code < 300:
            main_sync(False, i, util.find_links(sync_urls[i], req.text))
    elif req.status_code < 300:
        driver.get(href)
    
        try: driver.find_element_by_class_name("pager-showall").click()
        except Exception: pass
        
        try: files = [item for item in driver.find_element_by_class_name("table-panel").find_elements_by_tag_name("tr")]
        except (sel.exceptions.NoSuchElementException, sel.exceptions.WebDriverException): files = []

        if len(files) > 0: opal_sync(driver, i, files)
        else:
            html = driver.page_source
            try:
                iframe = driver.find_element_by_tag_name("iframe")
                href = iframe.get_attribute("src")
                driver.switch_to.frame(iframe)
                html = html + driver.page_source
                driver.switch_to.default_content()
            except Exception as e: pass
            main_sync(driver, i, util.find_links(href, html))
    else:
        print("Sync Runner for '{0}' ({1} of {2}) failed with status code {3};".format(sync_labels[i], i + 1, len(sync_labels), req.status_code))
        print(req.text)

def main_sync(driver, i, links):
    global file_db, convert
    new = 0
    unchanged = 0
    tw = 40
    n = 0
    label_path = os.path.join(project_path, *sync_labels[i].split("/"))
    for link in links:
        progress = int(round(min(n * tw / len(links), tw)))
        prtstr = "Main Sync Job for '{0}' ({1} of {2}) running: {3} new, {4} unchanged  ".format(sync_labels[i], i + 1, len(sync_labels), new, unchanged)
        s = prtstr + "[{0}{1}] {2:3.0f}%".format("-" * progress," " * (tw - progress), 100 * n/len(links))
        util.inline_prt(s)
        n = n + 1    

        file_name = util.get_filename(link)
        count = re.findall(r'(\.[0-9a-zA-Z\s]{1,6})', file_name)
        if len(count) > 0 and len(link.split("/")) > 0:
            if file_name.endswith(count[-1]):
                if not file_name in file_db[sync_labels[i]]:
                    localpath = util.downloader_beta(driver, link, os.path.join(label_path, file_name), OTHER_LOGINS, True, len(s))
                    if not localpath == "":
                        file_db[sync_labels[i]].append(file_name)
                        if localpath.lower().endswith(".mp4"): convert.append([localpath, re.sub(".mp4", "_edit.mp4", localpath, flags=re.IGNORECASE)])
                        new = new + 1
                else: unchanged = unchanged + 1
    print("Main Sync Job for '{0}' ({1} of {2}) completed: {3} new, {4} unchanged, {5} total.  [{6}] 100%".format(sync_labels[i], i + 1, len(sync_labels), new, unchanged, new + unchanged, tw * "-"))

def opal_sync(driver, i, files):
    global file_db, convert
    downloads = []

    altered = 0
    new = 0
    nofile = 1
    for j in range(1, len(files)):
        try:
            file = files[j].find_element_by_tag_name("a")
            file_name = util.get_filename(file.text)
            file_date = time.mktime(datetime.strptime(re.sub("[A-Za-z]","", files[j].find_elements_by_tag_name("span")[4].text).strip(), "%d.%m.%Y  %H:%M").timetuple())
            file_size = float(re.sub("[A-Za-z]","", files[j].find_elements_by_tag_name("span")[3].text).strip().replace(",","."))
            
            if files[j].find_elements_by_tag_name("span")[3].text.lower().endswith("k"):
                file_size = file_size * 1024
            elif files[j].find_elements_by_tag_name("span")[3].text.lower().endswith("m"):
                file_size = file_size * (1024 ** 2)
            elif files[j].find_elements_by_tag_name("span")[3].text.lower().endswith("g"):
                file_size = file_size * (1024 ** 3)

            if file_name in file_db[sync_labels[i]]:
                if file_date > last_updated:
                    downloads.append([file.get_attribute("href"), file_name, file_size])
                    altered = altered + 1
            else:
                downloads.append([file.get_attribute("href"), file_name, file_size])
                file_db[sync_labels[i]].append(file_name)
                new = new + 1
        except Exception: nofile = nofile + 1 # This row is not a file, probably a subdirectory

    data = util.selenium_downloader(driver, os.path.join(project_path, *sync_labels[i].split("/")), downloads, sync_urls[i])
    
    for item in data[1]: convert.append(item)
    for el in data[0]: 
        while el[1].replace(";", "_") in file_db[sync_labels[i]]: file_db[sync_labels[i]].remove(el[1].replace(";", "_"))    
    
    s = "OPAL Sync Job for '{0}' ({1} of {2}) completed: {3} new, {4} altered, {5} unchanged, {6} total files in the server. \n"
    if len(data[0]) > 0: s = s + "OPAL Sync Job for '{0}' ({1} of {2}): Warning: {7} Files failed to download!\n"
    print(s.format(sync_labels[i], i + 1, len(sync_labels), new, altered, max([len(files) - nofile - new - altered, 0]), max([len(files) - nofile, 0]), len(data[0])))

if __name__== "__main__":
    print("Procrastinator Script v1.1.0")
    main()
