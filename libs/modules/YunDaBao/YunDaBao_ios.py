#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/1/8 10:52
# @Author  : fy
# @FileName: YunDaBao_ios.py
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


class YunDaBao(BaseModule):
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
            return self._find_main_activity("com.wta.NewCloudApp.activity.ZitianNewsActivity")
        elif self.host_os == "ios":
            # 需要对ios应用的特征进行判断
            return self._find_bundle_identifier("com.zitian")  # 云打包的ios应用，Bundle Identifier以"com.zitian"开头
        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        tmp_folder = os.path.join(extract_folder, "tmp")
        ipa_file = zipfile.ZipFile(self.detect_file)
        ipa_file.extractall(tmp_folder)

        app_dir = ""
        pattern = re.compile(r'Payload/[^/]*.app/myxml.xml')
        for file in ipa_file.namelist():
            m = pattern.match(file)
            if m is not None:
                app_dir = m.group()

        xml_file_path = os.path.join(tmp_folder, app_dir)
        shutil.copy(xml_file_path, extract_folder)
        xml_file = open(xml_file_path, "r+")
        myxml_tree = ET.parse(xml_file)
        myxml_root = myxml_tree.getroot()
        launch_path = myxml_root.find("row").get("weburl")

        self._dump_info(extract_folder, launch_path)
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/YunDaBao/花总管.ipa"
    # f = "./test_case/YunDaBao/花木网.ipa"
    ydb = YunDaBao(f, "ios")
    if ydb.doSigCheck():
        logging.info("YunDaBao signature Match")
        extract_folder, launch_path = ydb.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == '__main__':
    sys.exit(main())
