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

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

'''
adb -s emulator-5554 install '/home/demo/Downloads/14557436b6d3512fc199435e728701bf.apk' 
adb devices
'''


'''
import subprocess
import os
import re
import time

cmd1 = r'adb install '
cmd2 = r'adb shell am start -n'
cmd3 = r'adb shell screencap  -p /sdcard/1.png'
cmd4 = r'adb pull /sdcard/1.png d:/1'
cmd5 = r'adb uninstall '
if __name__ == "__main__":
    # proc = subprocess.Popen(cmd1 + "C:\Users\45277\Desktop\telegram\app\bat.apk",
    #            shell=True,stdin=subprocess.PIPE,
    #            stdout=subprocess.PIPE,
    #            stderr=subprocess.PIPE)
    # sq_path = r'D:\PycharmProject\sq'
    # for line in os.listdir(sq_path):
    #     apkPath = os.path.join(sq_path,line)
    #     print(apkPath)
        # sha = line[:-4]
        apkPath = r'C:\Users\24621\Desktop\0e94480edea95eaff5cdbd93a89bd3ca80fa4cbe.apk'  # 填入需要安装的apk路径
        sha = apkPath[23 :-4]


        print("==install==")
        i = subprocess.Popen(['adb', 'install', '-r', apkPath], stdout=subprocess.PIPE)
        print(i.communicate())

        print("==start==")
        # aaa = 'launchable-activity: name=\''
        aaa = 'launchable-activity: name=\''
        bbb = '\'  label=\''
        ccc = 'package: name=\''
        ddd = '\' versionCode=\''
        p1 = subprocess.Popen(['aapt', 'd', 'badging', apkPath], stdout=subprocess.PIPE)
        result = p1.communicate()[0]
        # .format()
        # print(result)
        result = result.decode()
        print(result.find(aaa))
        print("LaunchActivity: " + result[result.find(aaa) + 27:result.find(bbb)])
        print("packagename: " + result[result.find(ccc) + 15:result.find(ddd)])
        activityname = result[result.find(aaa) + 27:result.find(bbb)]
        packagename = result[result.find(ccc) + 15:result.find(ddd)]
        s = subprocess.Popen(['adb', 'shell', 'am', 'start', '-n', packagename + '/' + activityname],
                             stdout=subprocess.PIPE)
        print(s.communicate())
        time.sleep(20)

        print("==screenshot==")
        time.sleep(15)
        s2 = subprocess.Popen(['adb', 'shell', 'screencap', '-p', '/sdcard/' + sha + '.png'],
                              stdout=subprocess.PIPE)
        print(s2.communicate())
        time.sleep(15)

        print("==pull==")
        p = subprocess.Popen(['adb', 'pull', '/sdcard/' + sha + '.png', r'D:\PycharmProject\malicious\sq_pict'], stdout=subprocess.PIPE)
        print(p.communicate())

        print("==uninstall==")
        u = subprocess.Popen(['adb', 'uninstall', packagename], stdout=subprocess.PIPE)
        print(u.communicate())

'''
class SnapShotExtractor:
    def __init__(self, device_serial):
        self._device_serial = device_serial

    def get_screen_shot(self, filename):


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apk-folder', required=True, help="Folder contains apk files.")
    parser.add_argument('--task-name', required=True, help="Provide existing name of this task, such that we can feed the snapshot to.")
    parser.add_argument('--device-serial', help="set the device serial, use `adb devices` to find the device.")

    args = parser.parse_args()

    if Checker.doEnvCheck() == False:
        sys.exit(1)

    # ensure task-name exist
    if not os.path.exists(os.path.join(Config["working_folder"]), args.task_name):
        log.error("can not find such task: {}.".format(args.task_name))
        sys.exit(1)

    proc = subprocess.Popen("adb --version", shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    r = (proc.communicate()[1]).decode()
    if r.find("not found") != -1:
        log.error("adb command not found.")
        sys.exit(1)

    for dirpath, dirnames, ifilenames in os.walk(args.apk_folder):
        for fs in ifilenames:
            file_in_check = os.path.join(dirpath, fs)
            if not os.path.isfile(file_in_check):
                continue
            if Checker.doAPKCheck(file_in_check):
                log.info(file_in_check)


if __name__ == "__main__":
    sys.exit(main())
