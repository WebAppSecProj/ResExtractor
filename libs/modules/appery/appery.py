#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/1/12 16:28
# @Author  : fy
# @FileName: appery.py

import logging
import re
import shutil
import sys

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


class appery(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return True
            return self._find_main_activity("io.appery")
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
    f = "./test_case/io.appery/appery_test-debug.apk"
    f = "./test_case/io.appery/2d341dd7360939bee1f84c1e3a67606c6ea37629a141e22bdc8043692d305d83.apk"
    f = "./test_case/io.appery/4c37503d906bdd80c2275d28e95844697f6657d04ccdc2b1dade73fe728e1144.apk"
    f = "./test_case/io.appery/Diebold Nixdorf SPIRIT_v120_apkpure.com.apk"
    _appery = appery(f, "android")
    if _appery.doSigCheck():
        logging.info("appery signature Match")
        extract_folder, launch_path = _appery.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == '__main__':
    sys.exit(main())
