#!/usr/bin/env python3
"""
Created on Wed Dec 25 2020

@author: beizishaozi
"""

import logging
import sys
import zipfile
import shutil
import re

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
1) http://www.andromo.com/
Andromo don't support to generate iOS app.
Andromo don't support to encryption.
Andromo support custom package name for paid plan. free app only lived for 7 days.
'''

class Andromo(BaseModule):
    def doSigCheck(self):
        if self.host_os == "android":
            # Andromo app's signature is the apk which contain the file "/assets/consentform.html"
            zf = zipfile.ZipFile(self.detect_file, 'r')
            flag = 0
            for f in zf.namelist():
                if f == "assets/consentform.html":
                    flag = 1
            if flag == 1:
                return True
            return False

        elif self.host_os == "ios":
            log.error("not support yet.")
            return False

        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)
        tmp_folder = os.path.join(os.getcwd(), extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok = True)
        self._apktool(tmp_folder)

        launch_path=[]
        for dirpath, dirnames, ifilenames in os.walk(tmp_folder):
            if dirpath.find("assets") != -1:   # store web resource  and f != "assets/widget/config.xml"
                for fs in ifilenames:
                    if fs == "consentform.html":
                        continue
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
            elif dirpath.endswith("res/values") != -1:
                for fs in ifilenames:
                    if fs != "strings.xml":
                        continue
                        # parse the xml file, construct the path of app code, and extract
                    t = ET.ElementTree(file=os.path.join(dirpath, fs))
                    for elem in t.iter(tag='string'):
                        value = elem.attrib['name']
                        if value.startswith("Website") and value.endswith("_webview_content"):
                            launch_path.append(elem.text)
                        elif value.startswith("Rss_") and value.endswith("rss_feed_url"):
                            launch_path.append(elem.text)

        self._dump_info(extract_folder, "".join(launch_path))
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/Andromo/app_andromo.apk"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径
    andromo = Andromo(f, "android")
    if andromo.doSigCheck():
        logging.info("Andromo signature Match")

        extract_folder, launch_path = andromo.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
