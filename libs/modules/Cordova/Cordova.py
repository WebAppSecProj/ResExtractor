#!/usr/bin/env python3
"""
Created on Wed Dec 25 2020

@author: beizishaozi
"""
import logging
import re
import sys
import zipfile
import shutil

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Reference:
1) http://cordova.axuer.com/docs/zh-cn/latest/guide/support/index.html
'''


# extracting the starting page from "res/xml/config.xml" in "<content src="index.html" />"

class Cordova(BaseModule):
    def doSigCheck(self):
        if self.host_os == "android":
            # Cordova app's signature is the apk which contain the file "/assets/www/cordova.js /assets/www/cordova_plugins.js /assets/www/cordova-js-src"
            apk_file = zipfile.ZipFile(self.detect_file)
            pattern = re.compile(r'^(assets/www/cordova-js-src).*')
            app_dir = ""
            for f in apk_file.namelist():
                m = pattern.match(f)
                if m is not None:
                    app_dir = m.group()
            features = ['assets/www/cordova.js', 'assets/www/cordova_plugins.js']
            if (set(features) < set(apk_file.namelist())) and (len(app_dir)):
                return True
            return self._find_main_activity("cordova.MainActivity")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        tmp_folder = os.path.join(extract_folder, "tmp")
        self._apktool(tmp_folder)

        resource_path = os.path.join(tmp_folder, "assets/www/")
        shutil.copytree(resource_path, extract_folder, dirs_exist_ok=True)
        content = "index.html"
        # if config.xml missing, the default start page is assets/www/index.html
        if os.path.exists(os.path.join(tmp_folder, "res/xml/config.xml")):
            t = ET.ElementTree(file=os.path.join(tmp_folder, "res/xml/config.xml"))
            root = t.getroot()
            for child in root:
                if "content" in child.tag:
                    content = child.attrib['src']
        launch_path = "assets/www/" + content  # in java code, start page is "file:///android_asset/www/" + content
        pattern = re.compile(r'^[a-z-]+://')
        if pattern.match(content):
            launch_path = content

        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/Cordova/U878d.apk"  # 后续会将当前脚本路径与之相拼接，得到最终detect_file路径
   # f = "./test_case/Cordova/a39d09b5d96bbe2715acce62c26788eb7b6a84ce0ba67ee619ff1f1c8d7f0713.apk"  # App Yourself：launcher activity start with "net.ays"
   # f = "./test_case/Cordova/a0812e6bc398784bda36979eae895775da42ca3b6958b134784cd4dc7a99455d.apk"  # hk.com.appbuilder: launcher activity start with "hk.com.appbuilder.cms"
   # f = "./test_case/Cordova/3a60fcc118cbbb09b9b0f14fa47e62a35a.apk"  # start page isn't a local source
    f = "./test_case/Cordova/justep_app.apk"   # example of Justep
    cordova = Cordova(f, "android")
    if cordova.doSigCheck():
        logging.info("cordova signature Match")
        extract_folder, launch_path = cordova.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
