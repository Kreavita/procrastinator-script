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
STREAM_DURATION = 100 # Duration of a Streaming session (in minutes)
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

#these are not used for the moment
ZOOM_EMAIL = "sample.email@provider.com" # Your Zoom Email (You need a zoom account or I have to proof that "I'm not a robot")
ZOOM_PASS = "zoom-password" # Your Zoom Password

#-----------------------------------------------------------------------
# end of configuration
#-----------------------------------------------------------------------
import os

exe = ""
python = "python3"

if os.name == "nt":
    exe = ".exe"
    python = "py"

launch_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(launch_path, PROJECT_DIR)

py2 = False
try: import _thread as thread  #Py3
except:
    import thread  #Py2
    py2 = True

