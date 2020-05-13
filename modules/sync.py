import requests,os,time,re
from threading import Timer
from datetime import datetime, timedelta
from selenium import common as sel

requests.packages.urllib3.disable_warnings()

from .util import util, login_flows, file_manager as fm
from . import stream, jumpcut as jc
import config

sync_urls = []
sync_labels = []

last_updated = 0
file_db = {}
        
def sync_timer():
    global sync_labels, sync_urls, stream_labels, stream_urls, stream_timestamps, last_updated, file_db

    sync_labels = []
    sync_urls = []

    first = False
    
    for line in fm.file_read(os.path.join(config.launch_path, 'data', 'sources_sync')):
        if len(line) > 4:
            sync_labels.append(line.split(";")[0].strip())
            sync_urls.append(line.split(";")[1].strip())

            if not os.path.exists(os.path.join(config.project_path, line.split(";")[0].strip())):
                os.makedirs(os.path.join(config.project_path, line.split(";")[0].strip()))

            if not line.split(";")[0].strip() in file_db: file_db[line.split(";")[0].strip()] = []
            
    if last_updated == 0:
        first = True
        for line in fm.file_read(os.path.join(config.launch_path, 'data', 'last_updated')):
            try: last_updated = int(line)
            except: pass
            
        for line in fm.file_read(os.path.join(config.launch_path, 'data', 'file_db')):
            if len(line) > 4:
                try:
                    file_db[line.split(";")[0].strip()].append(line.split(";")[1].strip())
                except:
                    file_db[line.split(";")[0].strip()] = [line.split(";")[1].strip()]
    
    if config.SYNC_ON_START and first: sync_job()
    elif config.SCHEDULE_SYNC:
        x = datetime.today()
        y = x.replace(day = x.day, hour = config.SYNC_HOUR, minute = config.SYNC_MINUTE, second = 0, microsecond = 0) + timedelta(days = 1)
        delta_t = y - x
        
        print("Sync Timer: next Sync is scheduled at {0}".format(time.ctime(time.mktime(y.timetuple()))))

        t = Timer(delta_t.total_seconds(), sync_job)
        t.start()

def sync_job():
    time.sleep(1)
    if stream.next_stream - time.time() < 100 * len(sync_labels) and stream.next_stream - time.time() > 0:
        stream_delay = stream.next_stream + config.STREAM_DURATION * 60
        if config.AUTO_JUMPCUT: stream_delay = stream_delay + 2.2 * config.STREAM_DURATION * 60
        
        print("Sync Timer: Sync is delayed to {0}, because stream starts soon.".format(time.ctime(stream_delay)))
        
        t = Timer(stream_delay - time.time(), sync_job)
        t.start()
    else:
        while jc.active_jc:
            time.sleep(60)
        
        global last_updated, file_db
        print ("Sync Job: {0} (last updated: {1})".format(time.ctime(time.time()), time.ctime(last_updated)))

        last_updated_unconfirmed = int(time.time())

        with util.get_driver(True) as driver:
            login_flows.lf_opal(driver)
            for i in range(len(sync_urls)): sync_runner(i, driver)

        last_updated = last_updated_unconfirmed

        data = ""
        for label, files in file_db.items():
            for file in files:
                data = data + label + ";" + file.replace(";", "_") + "\n"
        fm.file_write(os.path.join(config.launch_path, "data", "file_db"), data)
        
        fm.file_write(os.path.join(config.launch_path, "data", "last_updated"), str(last_updated))
        print("Database successfully updated. ")
        
        if config.AUTO_JUMPCUT: jc.jumpcut_job(0)    
        
        sync_timer()

def sync_runner(i, driver):
    href = sync_urls[i]
    req = requests.get(href, verify=False)
    if req.status_code == 401 or href.endswith(".pdf"):
        y = 0
        while req.status_code == 401 and y < len(config.OTHER_LOGINS):
            if req.status_code == 401: y = y + 1
            req = requests.get(sync_urls[i], auth=(config.OTHER_LOGINS[y][0], config.OTHER_LOGINS[y][1]), verify=False)
        if req.status_code < 300:
            main_sync(False, i, util.find_links(sync_urls[i], req.text))
    elif req.status_code < 300:
        driver.get(href)
        time.sleep(0.25)
        
        try:
            driver.find_element_by_class_name("pager-showall").click()
            time.sleep(0.25)
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
    global file_db
    new = 0
    unchanged = 0
    tw = util.tw
    n = 0
    label_path = os.path.join(config.project_path, *sync_labels[i].split("/"))
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
                    localpath = util.downloader_beta(driver, link, os.path.join(label_path, file_name), config.OTHER_LOGINS, True, len(s))
                    if not localpath == "":
                        file_db[sync_labels[i]].append(file_name)
                        if localpath.lower().endswith(".mp4"): jc.convert.append([localpath, re.sub(".mp4", "_edit.mp4", localpath, flags=re.IGNORECASE)])
                        new = new + 1
                else: unchanged = unchanged + 1
    print("Main Sync Job for '{0}' ({1} of {2}) completed: {3} new, {4} unchanged, {5} total.  [{6}] 100%".format(sync_labels[i], i + 1, len(sync_labels), new, unchanged, new + unchanged, tw * "-"))

def opal_sync(driver, i, files):
    global file_db
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

    data = util.selenium_downloader(driver, os.path.join(config.project_path, *sync_labels[i].split("/")), downloads, sync_urls[i])
    
    for item in data[1]: jc.convert.append(item)
    for el in data[0]: 
        while el[1].replace(";", "_") in file_db[sync_labels[i]]: file_db[sync_labels[i]].remove(el[1].replace(";", "_"))    
    
    s = "OPAL Sync Job for '{0}' ({1} of {2}) completed: {3} new, {4} altered, {5} unchanged, {6} total files in the server. \n"
    if len(data[0]) > 0: s = s + "OPAL Sync Job for '{0}' ({1} of {2}): Warning: {7} Files failed to download!\n"
    print(s.format(sync_labels[i], i + 1, len(sync_labels), new, altered, max([len(files) - nofile - new - altered, 0]), max([len(files) - nofile, 0]), len(data[0])))
