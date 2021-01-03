#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import subprocess
import zipfile
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

    # fix fake encrypt app?
    # http://bluebox.com/labs/android-security-challenge/
    # one solution: https://github.com/adamely/DalvikBytecodeTampering. I would like to modify the flag of this file rather than extract them all.
    # test case: 上彩公益-e40de64ba4737af78f21b6349c189508.apk
    # invest: it's said that this vul is fixed in the latest os, however, this sample can work on android 11.
    '''
    @author : zoudeneng
    TODO: should limit to the header to avoid conflict.
    '''
    with open(f, 'rb+') as fh:
        # scan the file to find sig
        while fh.tell() < os.path.getsize(f) - 10:
            if fh.read(4) == b'\x50\x4b\x01\x02':
                fh.seek(4, 1)
                if fh.read(1) != b'\x00':
                    log.error("oops, {} is protected by using fake encrypt".format(f))
                    # walk back and reset the tag
                    fh.seek(-1, 1)
                    fh.write(b'\x00')
                fh.seek(-5, 1)
            fh.seek(-3, 1)

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

    doEnvCheck()

if __name__ == "__main__":
    sys.exit(main())
