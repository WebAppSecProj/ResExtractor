#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import base64
import logging
import shutil
import sys

import os
import zipfile

from Crypto.Cipher import AES

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: https://www.appbsl.cn/index
'''


class BSLApp(BaseModule):
    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.bslyun.app.activity.MainActivity")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):

        extract_folder = self._format_working_folder(working_folder)

        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok=True)
        tmp_folder = os.path.join(extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok=True)

        zf = zipfile.ZipFile(self.detect_file, 'r')
        config_file = zf.extract("assets/app_config.xml", tmp_folder)
        fo = open(config_file, "r+")
        config_str = self._decode(fo.read(os.path.getsize(config_file)))

        dd = config_str.find('</config>') + 9 - len(config_str)
        if dd != 0:
            root = ET.fromstring(config_str[:dd])
        elif dd == 0:
            root = ET.fromstring(config_str)
        launch_path = root.find('mainUrl').text

        self._dump_info(extract_folder, launch_path)

        # clean env
        shutil.rmtree(tmp_folder)

        return extract_folder, launch_path


    def _decode(self, config_str):
        key = 'IUP4fLZ7wuNeOQtE'.encode('utf-8')
        iv = 'handsomehandsome'.encode('utf-8')
        mode = AES.MODE_CBC
        cipher = AES.new(key, mode, iv)
        config_str = cipher.decrypt(base64.b64decode(config_str.encode('utf-8')))

        barr = bytearray(config_str)
        for i in range(len(barr)):
            if barr[i] == 13 or barr[i] == 10:  # 13 =‘\r 12='\n' 32=" "
                barr[i] = 32
        config_str = barr.decode()
        return config_str


def main():
    f = "./test_case/com.bslyun.app.activity.MainActivity/suishou.apk"
    bsl = BSLApp(f, "android")
    if bsl.doSigCheck():
        logging.info("BSLApp signature Match")

        extract_folder, launch_path = bsl.doExtract("./working_folder")
        # print(extract_folder)
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return


if __name__ == "__main__":
    sys.exit(main())
