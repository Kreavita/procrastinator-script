import time
import config
from modules import stream, sync

if config.py2:
    import thread
    reload(sys)
    sys.setdefaultencoding('UTF-8')
else:
    import _thread as thread  #Py3

def main():
    if config.STREAM_RECORDING: thread.start_new_thread (stream.stream_timer, ())
    
    if config.SCHEDULE_SYNC or config.SYNC_ON_START: sync.sync_timer()

    print("script init completed.")
    while config.STREAM_RECORDING or config.SCHEDULE_SYNC:
        if config.STREAM_RECORDING or config.SCHEDULE_SYNC: time.sleep(3600)
        
if __name__== "__main__":
    print("Procrastinator Script v2.0")
    main()
