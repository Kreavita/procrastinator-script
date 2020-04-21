import os,sys,time,requests,re
from selenium import webdriver

requests.packages.urllib3.disable_warnings()
try:
    reload(sys)
    sys.setdefaultencoding('UTF-8')
    from urlparse import urljoin
    from urllib2 import unquote
except Exception as e:
    from urllib.parse import urljoin, unquote
    pass

class Util:
    def __init__(self, timeout):
        self.exe = ""
        if os.name == "nt": self.exe = ".exe"
        self.timeout = timeout

        self.launch_path = os.path.dirname(os.path.abspath(__file__))

        self.mime_list = ""
        with open(os.path.join(self.launch_path, 'mime')) as f:
            for line in f: self.mime_list = self.mime_list + line.strip()

    def get_driver(self, headless):
        try:
            options = webdriver.firefox.options.Options()
            options.headless = headless
            self.dl_ext = ".part"
            profile = webdriver.FirefoxProfile()
            profile.set_preference("browser.helperApps.alwaysAsk.force", False)
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.dir", os.path.join(self.launch_path, "download"))
            profile.set_preference("browser.download.manager.showWhenStarting", False)
            profile.set_preference("pdfjs.disabled", True)
            profile.set_preference("media.mp4.enabled", False)
            profile.set_preference("media.ffmpeg.enabled", False)
            profile.set_preference("media.webm.enabled", False)
            profile.set_preference("media.av1.enabled", False)
            profile.set_preference("media.ffvpx.mp3.enabled", False)
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk", self.mime_list)
            driver = webdriver.Firefox(profile, options=options, executable_path=os.path.join(self.launch_path, "driver", "geckodriver" + self.exe))
        except Exception as e:
            print("WebDriver: Error occured with Firefox: {0}, forcing Chrome...".format(e))
            options = webdriver.chrome.options.Options()
            options.headless = headless
            self.dl_ext = ".crdownload"
            options.add_experimental_option("prefs", {
                "directory_upgrade": True,
                "download.prompt_for_download": False, 
                "download.default_directory": os.path.join(self.launch_path, "download"),
                "plugins.always_open_pdf_externally": True,
                'profile.default_content_settings': {'images': 2, 'videos': 2},
                'profile.default_content_setting_values.automatic_downloads': 2,
                "safebrowsing.enabled": True
            })
            driver = webdriver.Chrome(options=options, executable_path=os.path.join(self.launch_path, "driver", "chromedriver" + self.exe))

        driver.maximize_window()
        driver.implicitly_wait(self.timeout)
        return driver

    def selenium_downloader(self, driver, target_dir, data, url):
        if len(data) > 0:
            if not isinstance(data[0][0], list):
                downloads = data
                convert = []
            else:
                downloads = data[0]
                convert = data[1]
            tries = 0
            while tries < 3 and len(downloads) > 0:                    
                dl_size = sum([download[2] for download in downloads])
                retry = []
                
                tw = 40   
                n = 0
                pre_s = "Selenium downloader: downloading {0:.2f} MiB in {1} Files:  ".format(dl_size / float(1024 ** 2), len(downloads))
                s = pre_s + "{0}     ".format(" " * tw)
                for download in downloads:
                    self.inline_prt(s)
                    retry_queue = False
                    if tries < 2:
                        if tries == 1: download[0] = urljoin(url.rstrip("/") + "/", download[1])
                        try: localpath = self.downloader_beta(driver, download[0], os.path.join(target_dir, download[1]), [], False, len(s))
                        except Exception as e: retry_queue = True
                    else:
                        try: localpath = self.ugly_downloader(driver, download, os.path.join(target_dir, download[1]))
                        except Exception as e: raise #retry_queue = True
                    try:
                        if localpath == '': retry_queue = True
                        elif abs(os.path.getsize(localpath) - download[2])>0.05 * download[2]: retry_queue = True
                        elif localpath.lower().endswith(".mp4"): convert.append([localpath, re.sub(".mp4", "_edit.mp4", localpath, flags=re.IGNORECASE)])
                    except Exception as e: retry_queue = True

                    if retry_queue: retry.append(download)

                    n = n + 1
                    progress = int(round(min(n * tw / len(downloads), tw)))
                    s = pre_s + "[{0}{1}] {2:3.0f}%".format("-" * progress," " * (tw - progress), 100 * n/len(downloads))

                print(s)
                downloads = retry
                if not retry:
                    print("Selenium downloader: SUCCESS: {0} Videos added to convert queue.".format(len(convert)))
                else:
                    print("Selenium downloader: retrying failed Downloads: {0}".format([item[1] for item in retry]))
                    tries = tries + 1
            if tries == 3:
                failed = [download[1] for download in downloads]
                print("Selenium downloader: ERROR: {0} files failed to download after 3 tries: {1}".format(len(failed),failed))
            return [downloads, convert]
        else:
            return [[],[]]
    
    def file_read(self,path):
        with open(path, "r") as f: lines = [line.strip() for line in f if not line.startswith("#")]
        return lines
    
    def file_write(self, path, data):
        with open(path, "r") as f:
            lines = [line for line in f if line.startswith("#")]
        with open(path, "w") as f:
            f.writelines(lines)
            f.write(data)
        return True
    
    def downloader_beta(self, driver, url, path, logins, ignore, line_length):
        localpath = ""
        s = ""
        headers = {}
        if not driver == False:
            headers['User-Agent'] = driver.execute_script("return navigator.userAgent")
            cookies = driver.get_cookies()
            cookiestr = ""
            for cookie in cookies:
                cookiestr = cookiestr + cookie["name"] + "=" + cookie["value"] + ";"
            headers['Cookie'] = cookiestr
        try:
            verify=True
            req = requests.get(url, headers = headers, verify=True, stream = True)
        except requests.exceptions.SSLError as e:
            verify=False
            s = s + "\ndelta DL: Error with SSL Certificates, disabled Verify."
            req = requests.get(url, headers = headers, verify=False, stream = True)
        y = 0
        while req.status_code == 401 and y < len(logins):
            req = requests.get(url, headers = headers, auth=(logins[y][0], logins[y][1]), verify=verify, stream = True)
            if req.status_code == 401: y = y + 1
        if req.status_code < 300:
            if not (ignore and req.headers['content-type'].startswith(("text/", "application/javascript", "application/x-javascript", "application/json", "image/"))):
                try:
                    fname = self.get_filename(re.findall("filename=\"(.+)\"", req.headers['content-disposition'])[0])
                    path = os.path.join(os.path.dirname(path), fname)
                except:
                    pass
                with open(path, "wb") as f: 
                    for chunk in req.iter_content(chunk_size=64000):
                        f.write(chunk)
                localpath = path
        else: s = s + "\ndelta DL: Got Error Code: {0} with URL: {1}".format(req.status_code, url)
        
        s = s.strip("\n")
        if len(s) > 0: print(s + " " * max(line_length - len(s), 0))
        return localpath
    
    def newest_file(self, path):
        paths = [os.path.join(path, basename) for basename in os.listdir(path) if os.path.isfile(os.path.join(path, basename))]
        return max(paths, key=os.path.getctime)

    def find_links(self, url, content):
        if url.lower().endswith(".pdf"):
            links = re.findall(r'(?<=URI\().+?(?=\))', content)
        else:
            links = []
            for find in re.findall('"(http[s]?://.*?)"', content):
                if find not in links:
                    links.append(find)
            for find in re.findall('href\="(.*?)"', content):
                if not find.lower().startswith(("http://", "https://")):
                    find = urljoin(url, find)
                if find not in links:
                    links.append(find)
        return links
    
    def get_filename(self, html_string):
        fname = unquote(html_string).replace(";", "_")
        if len(fname.split("/")) > 0: fname = fname.split("/")[-1]
        return fname

    def inline_prt(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()
        sys.stdout.write("\b" * (len(s) + 1))
    
    def ugly_downloader(self, driver, download, path):
        driver.find_element_by_xpath('//a[@data-file-name="'+download[1]+'"]').click()

        downloading = True
        dl = os.path.join(self.launch_path, "download", download[1])
        oldfsize = os.path.getsize(dl)
        if os.path.isfile(dl + self.dl_ext) : oldfsize = oldfsize + os.path.getsize(dl + self.dl_ext)

        while downloading:
            time.sleep(1)
            newfsize = os.path.getsize(dl)
            if os.path.isfile(dl + self.dl_ext) : newfsize = newfsize + os.path.getsize(dl + self.dl_ext)
            if newfsize == oldfsize: downloading = False
            else: oldfsize = newfsize
        if os.path.isfile(path): os.unlink(path)
        os.rename(dl, path)
        return path