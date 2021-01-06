#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import logging
import shutil
import os
import base64

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from libs.modules.BaseModule import BaseModule

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info:  https://www.ofcms.com/
在线打包系统
'''


class Ofcms(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.ofcms_client.MainActivity")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok=True)
        launch_path = getUrl(self.detect_file)
        if len(launch_path) == 0:
            tmp_folder = os.path.join(extract_folder, "tmp")
            self._apktool(tmp_folder)
            launch_path = getSourceUrl(tmp_folder)
            # clean env
            shutil.rmtree(tmp_folder)

        self._dump_info(extract_folder, launch_path)
        return extract_folder, launch_path


def getSourceUrl(tmp_folder):
    SourceUrl = ""
    strXml = os.path.join(tmp_folder, "res/values/strings.xml")
    tree = ET.ElementTree(file=strXml)
    root = tree.getroot()
    for child in root:
        if child.attrib.get("name") == 'of_0_core_url':
            SourceUrl = child.text
    return SourceUrl


def getUrl(detect_file):
    i = 0
    i2 = 0
    url = ""
    length = os.path.getsize(detect_file)
    bArr = open(detect_file, 'rb').read(length)
    bArr2 = bytes([65, 80, 75, 32, 83, 105, 103, 32, 66, 108, 111, 99, 107])
    bArr3 = bytearray(200)
    while True:
        if i2 >= length:
            i = -1
            break
        i3 = 0
        while i3 < 13 and bArr[((length - 13) - i2) + i3] == bArr2[i3]:
            i3 += 1
        if i3 == 13:
            i = (length - 13) - i2
            break
        i2 += 1
    if i > 0:
        mm = 0
        while mm < 200:
            bArr3[mm] = bArr[i - 200 - 8 + mm]
            mm += 1
        url = base64.b64decode(bArr3).decode()
    return url


def main():
    f = "./test_case/Ofcms/7935d733e7decfa8ea074f68f4099902576998db4cd609150c4b8b07dcafe982.apk"
    # f = "./test_case/Ofcms/京东白条_ofcms.apk"
    # f = "./test_case/Ofcms/ofcms_demo.apk"
    # f = "./test_case/Ofcms/ofcms_demo2.apk"

    ofcms = Ofcms(f, "android")
    if ofcms.doSigCheck():
        logging.info("Ofcms signature Match")
        extract_folder, launch_path = ofcms.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
