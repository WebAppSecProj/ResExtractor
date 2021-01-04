#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import json
import re
import sys
import logging
import shutil
import os
import zipfile

from libs.modules.BaseModule import BaseModule

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info:  https://nativescript.org/#
Related Blog: https://juejin.cn/post/6844903840324517895
'''


class NativeScript_ios(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.tns.NativeScriptActivity")
        elif self.host_os == "ios":
            # 需要对ios应用的特征进行判断
            return True
            # log.error("not support yet.")
            # return False
        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        tmp_folder = os.path.join(extract_folder, "tmp")
        ipa_file = zipfile.ZipFile(self.detect_file)
        ipa_file.extractall(tmp_folder)

        app_dir = ""
        pattern = re.compile(r'[^/]*(\.app/)$')
        for file in ipa_file.namelist():
            m = pattern.match(file)
            if m is not None:
                app_dir = m.group()
        resource_path = os.path.join(tmp_folder, app_dir, "app")
        shutil.copytree(resource_path, extract_folder, dirs_exist_ok=True)
        json_path = os.path.join(resource_path, "package.json")
        fo = open(json_path, "r+")
        fo_file = json.load(fo)
        launch_path = app_dir + "app/" + fo_file['main']
        self._dump_info(extract_folder, launch_path)
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    # 通过NativeScript本地编译出的ios应用，只找到以.app结尾的文件夹，由于实际场景中的ios应用为.ipa结尾的文件，
    # 因为.ipa文件可看作是一个压缩包，故将.app文件夹打包压缩成.zip进行处理。
    f = "./test_case/NativeScript/test.zip"
    ns_ios = NativeScript_ios(f, "ios")
    if ns_ios.doSigCheck():
        logging.info("NativeScript signature Match")
        extract_folder, launch_path = ns_ios.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
