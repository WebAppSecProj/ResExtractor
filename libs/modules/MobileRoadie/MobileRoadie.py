#!/usr/bin/env python3
"""
Created on Mon FEB 5 2021

@author: beizishaozi
"""

import logging
import sys
import shutil
import jpype
import re

import Config as Config
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class MobileRoadie(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.mobileroadie.devpackage.startup.Main")
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
        self._apktool_no_decode_source(tmp_folder)


        appid = ""
        moroappId = ""
        launch_path = []
        urls = []
        if os.path.exists(os.path.join(tmp_folder, "res/values/strings.xml")):
            t = ET.ElementTree(file=os.path.join(tmp_folder, "res/values/strings.xml"))
            for elem in t.iter(tag='string'):
                value = elem.attrib['name']
                if value == "app_id":
                    appid = elem.text
                elif value == "moro_connect_appId":
                    moroappId = elem.text
                elif value.endswith("_url"):
                    urls.append(elem.text)
        if appid == "":
            launch_path = []
        elif appid == "1219" or appid == "10404":
            appid = moroappId
        for url in urls:
            launch_path.append("http://mobileroadie.com"+url+"/"+appid)
        self._dump_info(extract_folder, " ".join(launch_path))
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, " ".join(launch_path)


def main():
    f = "./test_case/Mobileroadie/pepe.apk"    #EKULS6.apk  EKQ361.apk
    mobileroadie = MobileRoadie(f, "android")
    if mobileroadie.doSigCheck():
        logging.info("Mobincube signature Match")

        extract_folder, launch_path = mobileroadie.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
