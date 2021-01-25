#!/usr/bin/env python3
"""
Created on Mon JAN 25 2021

@author: beizishaozi
"""

import logging
import sys
import shutil
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


class AppPark(BaseModule):
    def doSigCheck(self):
        if self.host_os == "android":
            apk = APK(self.detect_file)  #reference "https://github.com/TheKingOfDuck/ApkAnalyser"
            appliname = (str)(apk.get_manifest()['@package'])
            if appliname.startswith("cn.apppark."):
                return True
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

        for dirpath, dirnames, ifilenames in os.walk(tmp_folder):
            if dirpath.find("assets/initFiles") != -1:
                for fs in ifilenames:
                    f = os.path.join(dirpath, fs)
                    matchObj = re.match(r'(.*)assets/initFiles/(.*)', f, re.S)
                    newRP = matchObj.group(2)

                    tf = os.path.join(extract_folder, newRP)
                    if not os.access(os.path.dirname(tf), os.R_OK):
                        os.makedirs(os.path.dirname(tf))
                    with open(tf, "wb") as fwh:  # output the
                        # ugly coding
                        fp = open(os.path.join(dirpath, fs), "rb")
                        c = fp.read()
                        fp.close()
                        fwh.write(c)
                    fwh.close()
        launch_path=""
        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/AppPark/app_rider_1.0.apk"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径, //出错在解压缩失败//
    apppark = AppPark(f, "android")
    if apppark.doSigCheck():
        logging.info("AppPark signature Match")

        extract_folder, launch_path = apppark.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
