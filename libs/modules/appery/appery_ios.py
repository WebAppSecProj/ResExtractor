#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/1/12 17:00
# @Author  : fy
# @FileName: appery_ios.py
import logging
import re
import sys
import shutil
import os
import zipfile
import plistlib

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class appery_ios(BaseModule):
    def _find_bundle_identifier(self, sig):
        detect_zipfile = zipfile.ZipFile(self.detect_file)
        name_list = detect_zipfile.namelist()
        pattern = re.compile(r'Payload/[^/]*.app/Info.plist')
        for path in name_list:
            m = pattern.match(path)
            if m is not None:
                plist_data = detect_zipfile.read(m.group())
                plist_root = plistlib.loads(plist_data)
                return str(plist_root['CFBundleIdentifier']).startswith(sig)
        return False

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("io.appery")
        elif self.host_os == "ios":
            # 需要对ios应用的特征进行判断
            '''
            根据cordova打包出来的文件特征进行匹配
            
            ipa_file = zipfile.ZipFile(self.detect_file)
            app_dir = ""
            pattern = re.compile(r'Payload/[^/]*(\.app/)$')
            for f in ipa_file.namelist():
                m = pattern.match(f)
                if m is not None:
                    app_dir = m.group()
            match_file = [app_dir + "www/cordova.js", app_dir + "www/cordova_plugins.js"]
            match_dic = "www/cordova-js-src"
            return set(match_file) < set(ipa_file.namelist())
            '''
            # appery打包的ios应用，Bundle Identifier的默认值以"io.appery.app"开头
            # 当前匹配规则以默认值为准
            return self._find_bundle_identifier("io.appery.app")
        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        tmp_folder = os.path.join(extract_folder, "tmp")
        ipa_file = zipfile.ZipFile(self.detect_file)
        ipa_file.extractall(tmp_folder)

        app_dir = ""
        pattern = re.compile(r'Payload/[^/]*(\.app/)$')
        for file in ipa_file.namelist():
            m = pattern.match(file)
            if m is not None:
                app_dir = m.group()

        resource_path = os.path.join(tmp_folder, app_dir, "www")
        shutil.copytree(resource_path, extract_folder, dirs_exist_ok=True)

        content = "index.html"
        # Same as Android, if config.xml missing, the default start page is www/index.html
        if os.path.exists(os.path.join(tmp_folder, app_dir, "config.xml")):
            t = ET.ElementTree(file=os.path.join(tmp_folder, app_dir, "config.xml"))
            root = t.getroot()
            for child in root:
                if child.tag == "content":
                    content = child.attrib['src']
        launch_path = "www/" + content
        pattern = re.compile(r'^[a-z-]+://')
        if pattern.match(content):
            launch_path = content
        self._dump_info(extract_folder, launch_path)
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/io.appery/ViewFence.ipa"
    # HABot.ipa can not match Bundle_Identifier start with "io.appery.app"(default sig)
    # resource files same as Cordova
    f = "./test_case/io.appery/HABot.ipa"
    f = "./test_case/io.appery/CamWatch.ipa"
    _appery_ios = appery_ios(f, "ios")
    if _appery_ios.doSigCheck():
        logging.info("appery_ios signature Match")
        extract_folder, launch_path = _appery_ios.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == '__main__':
    sys.exit(main())
