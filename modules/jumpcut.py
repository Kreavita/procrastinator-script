import subprocess, shutil, os, time, sys

from .util import util
from . import stream
import config

convert = []
failed = -1
active_jc = False

launch_path = os.path.dirname(os.path.abspath(__file__))

def jumpcut_job(fixedFPS):
    global convert, active_jc
    
    if not config.py2:
        if (stream.next_stream - time.time() > 7200 * len(convert) or time.time() - stream.next_stream > config.STREAM_DURATION * 60) and not active_jc:
            print("Jumpcut Job: {0} videos in the queue.".format(len(convert)))
            active_jc = True
            
            failed = 0
            
            old_dir = os.getcwd()
            os.chdir(os.path.join(launch_path, "util"))
            
            for vid in convert:
                prtstr = "Jumpcut Job: jumpcutting {0} of {1} : '{2}'...".format(convert.index(vid) + 1, len(convert), vid[0].split("/")[-1])
                util.inline_prt(prtstr)
                
                shutil.move(vid[0], os.path.join(launch_path, "util", "i.mp4"))
                
                try: os.rmdir(os.path.join(launch_path, "util", "TEMP"))
                except OSError as e: pass
                
                t1 = time.time()
                with open(os.devnull, 'wb') as FNULL:
                    cmd = [sys.executable, "jumpcutter.py", "--input_file","i.mp4","--output_file", "o.mp4", "--silent_speed", "999999", "--sounded_speed", "1", "--frame_margin", "2", "--frame_quality", "1"]
                    if fixedFPS > 0:
                        cmd.append("--frame_rate")
                        cmd.append(str(fixedFPS))
                    jc = subprocess.Popen(cmd, stdout=FNULL, stderr=FNULL)                    
                    jc.wait()
                t2 = time.time()
                
                hh, remainder = divmod(t2-t1, 3600)
                mm, ss = divmod(remainder, 60)
                
                timestr = '{:02} Hours, {:02} Minutes, {:02} Seconds'.format(int(hh), int(mm), int(ss))
                
                if jc.returncode == 0:
                    if os.path.isfile(vid[1]): os.unlink(vid[1])
                    shutil.move(os.path.join(launch_path, "util", "o.mp4"), vid[1])
                    s = "\nJumpcut Job: Jumpcutter completed: {0} in {1})".format(vid[0].split("/")[-1], timestr)
                else:
                    failed = failed + 1
                    s = "\nJumpcut Job: Jumpcutter failed for: {0} (took {1})".format(vid[0].split("/")[-1], timestr)
                print(s + " " * max(len(prtstr) - len(s), 0))
                
                shutil.move(os.path.join(launch_path, "util", "i.mp4"), vid[0])
                
            os.chdir(old_dir)
            active_jc = False
            print("\nJumpcut Job: completed for {0} of {1} files. ({2} failed.)".format(len(convert) - failed, len(convert), failed))
            
        else: print("Jumpcut Job: waiting for next stream to finish, because OBS and the jumpcutter each need 100% of the PC Ressources.")
    else:
        print("Jumpcut Job: 'jumpcutter.py' is not compatible with Python 2, please use Python 3!")

    convert = []
    return failed
