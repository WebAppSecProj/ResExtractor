#!/usr/bin/env python3

import sys
import logging
import subprocess

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

'''
common env checker, app specific checking should reside in related module.
'''

def doCheck():

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
