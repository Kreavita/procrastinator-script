import os

import config
if config.py2:
    reload(sys)
    sys.setdefaultencoding('UTF-8')
        
def newest_file(path):
    paths = [os.path.join(path, basename) for basename in os.listdir(path) if os.path.isfile(os.path.join(path, basename))]
    return max(paths, key=os.path.getctime)

def file_read(path):
    with open(path, "r") as f: lines = [line.strip() for line in f if not line.startswith("#") and line.strip()]
    return lines

def file_write(path, data):
    with open(path, "r") as f:
        lines = [line for line in f if line.startswith("#") and line.strip()]
    with open(path, "w") as f:
        f.writelines(lines)
        f.write(data)
    return True
