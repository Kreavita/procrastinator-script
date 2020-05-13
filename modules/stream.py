import subprocess, os, time, re
from threading import Timer
from datetime import datetime

from .util import util, login_flows, file_manager as fm
from . import jumpcut as jc
import config
    
stream_labels = []
stream_services = []
stream_urls = []
stream_timestamps = []

next_stream = 0

def stream_timer():
    global stream_labels, stream_services, stream_urls, stream_timestamps, next_stream
    stream_labels = []
    stream_services = []
    stream_urls = []
    stream_timestamps = []
    
    for line in fm.file_read(os.path.join(config.launch_path, 'data', 'sources_stream')):
        if len(line) > 4:
            stream_labels.append(line.split(";")[0].strip())
            stream_services.append(line.split(";")[1].strip())
            stream_urls.append(line.split(";")[2].strip())
            stream_timestamps.append(time.mktime(datetime.strptime(line.split(";")[3].strip(), "%d.%m.%Y %H:%M:%S").timetuple()))
            
            if not os.path.exists(os.path.join(config.project_path, line.split(";")[0].strip())):
                os.makedirs(os.path.join(config.project_path, line.split(";")[0].strip()))

    i = 0
    cycle = True
    next_stream = 0
    while  (i < len(stream_timestamps)) and cycle:
        if time.time() > stream_timestamps[i]:
            i = i + 1
        else:
            cycle = False
            next_stream = stream_timestamps[i]
            print("Stream Timer: next Stream is scheduled at {0}".format(time.ctime(stream_timestamps[i])))
            delta_t = stream_timestamps[i] - time.time()
            
            t = Timer(delta_t, stream_runner, args=[i])
            t.start()
    if i == len(stream_timestamps): print("Stream Timer: no new upcoming stream found.")

def stream_runner(i):
    print("Stream Runner: starting stream record at: {0}".format(time.ctime(time.time())))

    with util.get_driver(False) as driver:
        
        loaded = False
        tries = 0

        while not loaded and tries < 5:

            loaded = False

            if stream_services[i] == "bbb":
                driver.get(stream_urls[i])
                loaded = login_flows.lf_bbb(driver)
                
            if stream_services[i] == "zoom":
                #login_flows.lf_zoom(driver)
                driver.get("https://zoom.us/wc/{0}/join".format(stream_urls[i]))
                loaded = login_flows.lf_zoom_mtg(driver)
                
            if stream_services[i] == "test":
                driver.get(stream_urls[i])
                loaded = True
                
            if not loaded:
                print("Stream Runner: join button not found ({0} of 5 tries)".format(tries + 1))
                tries = tries + 1
                time.sleep(150)

        obs_record(config.STREAM_DURATION * 60)
    
    if os.path.exists(config.OBS_OUTPUT):
        
        vid = fm.newest_file(config.OBS_OUTPUT)
        
        if vid.lower().endswith(".mkv") and os.path.getctime(vid) > stream_timestamps[i]:

            video_name = re.sub(".mkv", "_edit.mp4", os.path.basename(vid), flags=re.IGNORECASE)
            jc.convert.append([vid, os.path.join(config.project_path, stream_labels[i], video_name)])

            if config.AUTO_JUMPCUT: jc.jumpcut_job(config.OBS_FPS)
    else:
        print("Stream Runner: WARNING: The OBS_OUTPUT directory could not be found, you have to manage the OBS Recording manually.")
        
    stream_timer()

def obs_record(duration):
    path_old = os.getcwd()
    os.chdir(config.PATH_OBS)

    obs = subprocess.Popen(["obs64" + config.exe, "--startrecording", "--scene \"Fullscreen\"", "--minimize-to-tray"])
    time.sleep(duration)
    obs.terminate()
    
    os.chdir(path_old)
