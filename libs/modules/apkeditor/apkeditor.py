#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/1/21 17:29
# @Author  : fy
# @FileName: apkeditor.py
import re
import sys
import logging
import shutil
import os

from libs.modules.BaseModule import BaseModule

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: http://apkeditor.cn/
'''


class apkeditor(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.moban")
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

        # copy resource dir ("assets/") to working_folder
        resource_path = os.path.join(tmp_folder, "assets/")
        shutil.copytree(resource_path, extract_folder, dirs_exist_ok=True)
        launch_path = "unknown"

        pattern_file = re.compile("(.*?)/smali/com/moban/(.*?)/Constants.smali")
        pattern_line = re.compile(".field public static mHomeUrl:Ljava/lang/String; = \"(.*?)\"")
        for root, dirs, files in os.walk(tmp_folder):
            for filename in files:
                filename = os.path.join(root, filename)
                if pattern_file.match(filename):
                    with open(filename) as f:
                        launch_path = re.findall(pattern_line, f.read())[0]
        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/apkeditor/1c362759ca84885bf38b60b7c752457c4abc28e39291e94785ba098558365ff1.apk"
    f = "./test_case/apkeditor/58279bffd7c692168380f9e6409e9db28189ada2d6bacf982cc2034114524344.apk"
    ae = apkeditor(f, "android")
    if ae.doSigCheck():
        logging.info("apkeditor signature Match")
        extract_folder, launch_path = ae.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
