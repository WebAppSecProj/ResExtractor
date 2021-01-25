#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/1/18 17:35
# @Author  : fy
# @FileName: yunedit.py

import logging
import re
import shutil
import sys
import zipfile

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: https://appery.io/
'''


class yunedit(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            apk_file = zipfile.ZipFile(self.detect_file)
            js_pattern = re.compile(r'^(assets/phone/js/).*')
            css_pattern = re.compile(r'^(assets/phone/css/).*')
            js_dir = ""
            css_dir = ""
            for f in apk_file.namelist():
                m = js_pattern.match(f)
                n = css_pattern.match(f)
                if m is not None:
                    js_dir = m.group()
                if n is not None:
                    css_dir = n.group()
            features = ['assets/phone/start.html', 'assets/phone/index.html']
            if (set(features) < set(apk_file.namelist())) and (len(js_dir)) and (len(css_dir)):
                return True
            return self._find_main_activity("com.yunedit.yeui")
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

        resource_path = os.path.join(tmp_folder, "assets/phone/")
        shutil.copytree(resource_path, extract_folder, dirs_exist_ok=True)

        launch_path = "assets/phone/index.html"
        start_page = os.path.join(resource_path, "start.html")
        if os.path.exists(start_page):
            launch_path = "assets/phone/start.html"
        index_page = os.path.join(resource_path, "index.html")
        if os.path.exists(start_page):
            for str_line in open(index_page).read().split("\""):
                pattern = re.compile(r'^[a-z-]+://')
                if pattern.match(str_line):
                    launch_path = str_line

        self._dump_info(extract_folder, launch_path)

        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/yunedit/3a14541c2af517e025bd2482587f3df22d6fb4c9bfcf8642404cd8a3706f2a74.apk"
    f = "./test_case/yunedit/b9dab98585edc39074e237294d92fbd6dbccdcfb3d177416c536c1d8115ef15f.apk"
    f = "./test_case/yunedit/d2f89f90b8777587531f30949d5a89f992caa228e54c86099e5b3936ab88dc3f.apk"
    yd = yunedit(f, "android")
    if yd.doSigCheck():
        logging.info("yunedit signature Match")
        extract_folder, launch_path = yd.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == '__main__':
    sys.exit(main())
