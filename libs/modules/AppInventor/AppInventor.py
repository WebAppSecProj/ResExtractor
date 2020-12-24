#!/usr/bin/env python3

import logging
import sys
import zipfile
import shutil
import binascii
import base64
import datetime
from apkutils import APK
import re

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

#在主Activity的smali文件中做扫描，获取起始页地址，因为所有创建的组件都在主Activity中
#起始页地址分别可能以http://,https://和file:///android_asset开始
def extract_startpage(mainactivityfile):
    launch_path = []
    fp = open(mainactivityfile)
    data = fp.read()
    m = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', data)
    if m:
        for tmp in m:
            if tmp not in launch_path:
                launch_path.append(tmp)
    k = re.findall('file:///android_asset/(?:[-\w.]|(?:%[\da-fA-F]{2}))+', data)
    if k:
        for tmp in k:
            if tmp not in launch_path:
                launch_path.append(tmp)
    fp.close()
    return " ".join(launch_path)

class AppInventor(BaseModule):
    def doSigCheck(self):
        if self.host_os == "android":
            #com.google.appinventor.components.runtime.multidex.MultiDexApplication is application name
            apk = APK(self.detect_file)  #ference "https://github.com/TheKingOfDuck/ApkAnalyser"
            if apk.get_manifest()['application']['@android:name'] == "com.google.appinventor.components.runtime.multidex.MultiDexApplication":
                return True
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):
        extract_folder = os.path.join(os.getcwd(), working_folder, self.hash)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)
        tmp_folder = os.path.join(os.getcwd(), extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok = True)
        self._apktool(tmp_folder)

        launch_path = ""
        apk = APK(self.detect_file)
        package = str(apk.get_manifest()['@package'])
        mainactivity = str(apk.get_manifest()['application']['activity']['@android:name'])  #app only contain one activity, name is ".xxx"
        for dirpath, dirnames, ifilenames in os.walk(tmp_folder):
            if dirpath.find("assets") != -1:   # store web resource
                for fs in ifilenames:
                    f = os.path.join(dirpath, fs)
                    matchObj = re.match(r'(.*)assets/(.*)', f, re.S)
                    newRP = matchObj.group(2)

                    tf = os.path.join(extract_folder, newRP)
                    if not os.access(os.path.dirname(tf), os.R_OK):
                        os.makedirs(os.path.dirname(tf))
                    with open(tf, "wb") as fwh:  #output the plain
                        # ugly coding
                        fp = open(os.path.join(dirpath, fs), "rb")
                        c = fp.read()
                        fp.close()
                        fwh.write(c)
                    fwh.close()
            #extract the launch path
            elif dirpath.find(package.replace(".", "/")) != -1:
                for fs in ifilenames:
                    if fs.split(".")[0] != mainactivity[1:]:   #必须是文件名相同，不可以用包含这种关系来判断
                        continue
                    launch_path = extract_startpage(os.path.join(dirpath, fs))

        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/AppInventor/test.apk"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径
    appinventor = AppInventor(f, "android")
    if appinventor.doSigCheck():
        logging.info("App Inventor signature Match")

        extract_folder, launch_path = appinventor.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())