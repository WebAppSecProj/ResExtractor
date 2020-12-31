#!/usr/bin/env python3

import sys
import logging
import subprocess
import zipfile
import struct
import os

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

    # TODO: fix fake encrypt app?
    # http://bluebox.com/labs/android-security-challenge/
    # solution: https://github.com/adamely/DalvikBytecodeTampering
    # test case: 上彩公益-e40de64ba4737af78f21b6349c189508.apk
    # invest: it's said that this vul is fixed in the latest os, however, this sample can work on android 11.

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
