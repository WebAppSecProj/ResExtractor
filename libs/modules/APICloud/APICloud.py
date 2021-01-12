#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import logging
import shutil
import os

from libs.modules.APICloud.uzmap_resource_extractor import tools
from libs.modules.BaseModule import BaseModule
import Config as Config

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: http://www.apicloud.com/video_play/2_5

Reference:
https://github.com/newdive/uzmap-resource-extractor
https://blog.csdn.net/u011687188/article/details/80999016
https://bbs.pediy.com/thread-218656.htm
'''

class APICloud(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.uzmap.pkg.LauncherUI")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False


    def doExtract(self, working_folder):

        extract_folder = self._format_working_folder(working_folder)

        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        #os.makedirs(extract_folder, exist_ok = True)

        # https://github.com/newdive/uzmap-resource-extractor
        extractMap = tools.decryptAndExtractAPICloudApkResources(self.detect_file, extract_folder, printLog=True)

        # parse the xml file, construct the path of app code, and extract
        launch_path = ""
        try:
            t = ET.ElementTree(file=os.path.join(extract_folder, "config.xml"))
            for elem in t.iter(tag='content'):
                launch_path = elem.attrib['src']

            self._dump_info(extract_folder, launch_path)
        except:
            self._log_error(os.path.basename(__file__), self.detect_file, "foo")

        return extract_folder, launch_path


def main():

    f = "./test_case/com.uzmap.pkg.LauncherUI/0c8b013e173768eabf68fead38f4a1c17b949d1a.apk"
    apiCloud = APICloud(f, "android")
    if apiCloud.doSigCheck():
        logging.info("APICloud signature Match")

        extract_folder, launch_path = apiCloud.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
