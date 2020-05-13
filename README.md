# procrastinator-script
A tool that automatically downloads and updates media files and documents from various cloud services of the TU Dresden in the background, such as OPAL or Magma.

It requires either Firefox _(preferred)_ or Chrome to be installed and runs on Linux and Windows. (macOS is not tested.)

## 1. Features

- automatically download new and updated files from web services specified in `data/sources_sync`
- schedule and record`bigbluebutton` streams specified in `data/sources_stream` automatically at the specified time and for the specified duration
- edit recorded and downloaded videos automatically using [Jumpcutter](https://github.com/carykh/jumpcutter), a python video editor which removes silent parts by [carykh](https://www.youtube.com/user/carykh)

## 2. Installation (simple)

Install [Python 3](https://www.python.org/downloads/), then download [`installer.py`](https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/installer.py) and run it in a new folder as root / Admin

(Note: on Windows, you can download [`start-installer.bat`](https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/start-installer.bat) in the same directory as [`installer.py`](https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/installer.py), then right click it and select "run as Administrator")

After that, all you have to do is to put `C:\Program Files\ffmpeg\bin` to the User PATH. ([Tutorial here](https://www.youtube.com/watch?v=qjtmgCb8NcE)) and restart your PC after that!

(To uninstall, go to `Apps & Features` and remove `OBS Studio` and `Python`, then Remove `C:\Program Files\ffmpeg` and the folder where [`installer.py`](https://raw.githubusercontent.com/Kreavita/procrastinator-script/master/installer.py) is in.)

## 3. Installation (manually)

1. **Download and Unzip this Repo.**

2. **Install Python 3.**

   Windows: download the latest python version [here](https://www.python.org/downloads/), install it normally and install `Py`  as well (should be installed by default)

   Linux: use your package manager and update python3 to the latest version

   (Note: The script would work with python 2, but the jumpcutter wont.)

3. **Install these Python packages** using `pip install` (Linux: `pip3 install`):  `selenium requests pillow audiotsm scipy numpy pytube3`

4. **Download and Install ffmpeg.**

   Windows: download a build from a source of your choice, e.g. from [here](https://ffmpeg.zeranoe.com/builds/), unzip it and put the content into e.g. `C:\Program Files\ffmpeg`, then add the binary folder, `C:\Program Files\ffmpeg\bin`  to the PATH. ([Tutorial here](https://www.youtube.com/watch?v=qjtmgCb8NcE))

   Linux: install ffmpeg with your package manager

~~5. **Download the Jumpcutter.**~~

   ~~Download [jumpcutter.py](https://raw.githubusercontent.com/carykh/jumpcutter/master/jumpcutter.py) and put it in the same directory as this script~~
   no longer needed as i include a customized version in the script

6. **Download a WebDriver**

   for Firefox: [geckodriver](https://github.com/mozilla/geckodriver/releases), for Chrome: [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads), they are OS specific!

   unzip it and move it into the `driver` folder

7. On Windows: **restart the pc**

## 4. Setup

Set up the **sources** in the `data` folder, one line for each source, data separated by `;`

- `data/sources_stream`: Folder Name; URL of the stream; Date as: DD.MM.YYYY hh:mm:ss (It has to be exactly this format!)


- `data/sources_sync`: Folder Name; URL of the source

​	(Note: currently, only `bigbluebutton` streams are supported)

​	(Note: Folders Names can include sub folders such as `folder/subfolder`)

Set up the **script** in the *config* section of `procrastinatorScript100.organized.py` to fulfill your needs:

* **STREAM_RECORDING**: Do you wish to record scheduled streams? (True/False)


* **STREAM_DURATION**: Duration of a Streaming session (in minutes) (default: 100)


* **OBS_OUTPUT**: Path to the OBS recordings
* **OBS_FPS**: The framerate of your recordings. Set it to 0 and the script tries to detect it, but it wont always work (default: 60)


* **PATH_OBS**: Path to the obs64 executable, you shouldnt change this on windows after a normal OBS installation (default: "C://Program Files/obs-studio/bin/64bit")


* **SYNC_ON_START**: Do you wish to synchronize on Script startup? (True/False)


* **AUTO_JUMPCUT**: Do you wish to automatically shorten video material by removing the silence parts using the [Jumpcutter](https://github.com/carykh/jumpcutter)?


* **SCHEDULE_SYNC**: Schedule a daily sync of your local Directory and the specified Sources? (True/False)


* **SYNC_HOUR**, **SYNC_MINUTE**: hour and minute of the scheduled sync (default: 6:00)


* **TUD_NAME**: Your Full name
* **TUD_USER**: Your TU username


* **TUD_PASS**: Your TU password
* **OTHER_LOGINS**: If some of your sources require HTTP Authentication, add the login credentials to this list
* **PROJECT_DIR** The Directory name where all Media Files will be organized

## 5. Launch

Double Click `procrastionarScript100.organized.py` and maximize the window. Now it should be working

(Note: on Windows, just double click the `start-windows.bat`)

If anything does not work properly, let me know!