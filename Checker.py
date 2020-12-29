#!/usr/bin/env python3

import sys
import logging
import subprocess
import zipfile

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

'''
common checker, app specific checking should reside in related module.
'''

def doAPKCheck(f):
    try:
        zf = zipfile.ZipFile(f, "r")
    except:
        log.error("invalid zip format.")
        return False

    # to find corrupted zip file.
    if zf.testzip() != None:
        log.error("corrupted zip file.")
        return False

    if "AndroidManifest.xml" not in zf.namelist():
        log.error("not an APK file.")
        return False

    return True

def doEnvCheck():

    # check python3 environment
    if sys.version_info.major < 3:
        log.error("python3 required.")
        return False

    # java env required
    proc = subprocess.Popen("java -version", shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = (proc.communicate()[1]).decode()
    if r.find("not found") != -1:
        log.error("java runtime required.")
        return False

    # ensure aapt can work well?

    return True

def main():

    doCheck()
if __name__ == "__main__":
    sys.exit(main())
