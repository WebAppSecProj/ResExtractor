#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Tue Dec 22 21:08:56 2020
@author: yujun
'''

import sys
import Config
import importlib
import logging
import Checker
import argparse
import os
import subprocess
import platform
import re
import hashlib
import time

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

class SnapShotExtractor:
    def __init__(self, device_serial):
        self._device_serial = device_serial

    def _gethash(self, file):
        with open(file, "rb") as frh:
            sha1obj = hashlib.sha1()
            sha1obj.update(frh.read())
            return sha1obj.hexdigest()

    @property
    def _aapt(self):
        if platform.system() == 'Darwin':
            return Config.Config["aapt_osx"]
        elif platform.system() == 'Linux':
            return Config.Config["aapt_linux"]
        elif platform.system() == 'Windows':
            return Config.Config["aapt_windows"]

    def get_screen_shot(self, apk_file, local_folder):

        log.info("install")
        proc = subprocess.Popen("adb install -r '{}'".format(apk_file), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[1]).decode()
        log.info("install: {}".format(r))
        if r.find("failed") != -1:
            log.error("install failed.")
            return False

        # lunch
        proc = subprocess.Popen("{} d badging '{}'".format(self._aapt, apk_file), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        lunch_activity = re.findall("launchable-activity: name='(.*?)'", r)[0]
        package = re.findall("package: name='(.*?)'", r)[0]
        if lunch_activity == "" or package == "":
            log.error("no lunch information.")
            return False

        log.info("start")
        proc = subprocess.Popen("adb shell am start -n {}/{}".format(package, lunch_activity), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[1]).decode()
        log.info("start: {}".format((proc.communicate()[0]).decode()))
        log.info("start: {}".format((proc.communicate()[1]).decode()))

        if "Error" in r:
            log.error("lunch failed.")
            return False

        snap_shot_file_name = self._gethash(apk_file)
        # # take screen shot
        # snap_shot_file = "/sdcard/Splash-{}.png".format(snap_shot_file_name)
        # proc = subprocess.Popen("adb shell screencap -p {}".format(snap_shot_file), shell=True, stdin=subprocess.PIPE,
        #                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # r = (proc.communicate()[1]).decode()
        # if r != "":
        #     log.error("screencap failed.")
        #     return False
        #
        # time.sleep(2)
        #

        # wait for a while
        time.sleep(15)

        # take screen shot
        log.info("screencap")
        snap_shot_file = "/sdcard/{}.png".format(snap_shot_file_name)
        proc = subprocess.Popen("adb shell screencap -p {}".format(snap_shot_file), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[1]).decode()
        log.info("screencap: {}".format(r))
        if r != "":
            log.error("screencap failed.")
            return False

        # retrieve screenshot
        proc = subprocess.Popen("adb pull '{}' '{}'".format(snap_shot_file, local_folder), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        if "error" in r:
            log.error("adb pull failed.")
            return False

        # uninstall
        log.info("uninstall")
        proc = subprocess.Popen("adb uninstall '{}'".format(package), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        log.info("uninstall: {}".format(r))
        if "Failure" in r:
            log.error("adb uninstall failed.")
            return False

        # clean
        log.info("rm")
        proc = subprocess.Popen("adb shell rm '{}'".format(snap_shot_file), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        log.info("rm: {}".format(r))

        log.info("snap shot of {} is stored to {}".format(apk_file, os.path.join(local_folder, snap_shot_file_name)))
        return True

def main():

    # s = SnapShotExtractor("")
    # snapshot_folder = os.path.join(Config.Config["working_folder"], Config.Config["snapshot_folder"])
    # s.get_screen_shot("/hd/sample/803APK/202007APK_pkg/197684CDC55C94AE9BCD035D39D46C226/2020年7月16日李天宇被骗案_202007152035566272339737_QQ_8.4.1.apk", snapshot_folder)

    parser = argparse.ArgumentParser()
    parser.add_argument('--apk-folder', required=True, help="Folder contains apk files.")
    # parser.add_argument('--device-serial', help="set the device serial, use `adb devices` to find the device.")

    args = parser.parse_args()

    if Checker.doEnvCheck() == False:
        sys.exit(1)

    snapshot_folder = os.path.join(Config.Config["working_folder"], Config.Config["snapshot_folder"])
    if not os.path.exists(snapshot_folder):
        os.makedirs(snapshot_folder, exist_ok=True)

    # ensure adb exist
    proc = subprocess.Popen("adb --version", shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = (proc.communicate()[1]).decode()
    if r.find("not found") != -1:
        log.error("adb command not found.")
        sys.exit(1)

    # if args.device_serial:
    #     s = SnapShotExtractor(args.device_serial)
    # else:
    s = SnapShotExtractor("")

    for dirpath, dirnames, ifilenames in os.walk(args.apk_folder):
        for fs in ifilenames:
            file_in_check = os.path.join(dirpath, fs)
            if not os.path.isfile(file_in_check):
                continue
            if Checker.doAPKCheck(file_in_check):
                log.info("processing file: {}.".format(file_in_check))
                r = s.get_screen_shot(file_in_check, snapshot_folder)
                if r == True:
                    log.info("processing file: {} success.".format(file_in_check))
                else:
                    log.info("processing file: {} failed.".format(file_in_check))

    log.info("finished")


if __name__ == "__main__":
    sys.exit(main())
