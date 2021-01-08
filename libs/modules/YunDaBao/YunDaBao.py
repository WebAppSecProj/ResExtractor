#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/1/6 15:50
# @Author  : fy
# @FileName: YunDaBao.py
import sys
import logging
import shutil
import os

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: http://app.yundabao.cn/index.aspx
'''


class YunDaBao(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.wta.NewCloudApp.activity.ZitianNewsActivity")
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

        myxml_path = os.path.join(tmp_folder, "res/xml/myxml.xml")
        shutil.copy(myxml_path, extract_folder)

        myxml_file = open(myxml_path, mode="r+")
        myxml_tree = ET.parse(myxml_file)
        myxml_root = myxml_tree.getroot()
        launch_path = myxml_root.find("row").get("weburl")

        # clean env
        shutil.rmtree(tmp_folder)
        self._dump_info(extract_folder, launch_path)
        return extract_folder, launch_path


def main():
    f = "./test_case/YunDaBao/jiuwei312041_200.apk"
    # f = "./test_case/YunDaBao/a4348b81b88b5304e5da44d8365401144d4529d7c2aebd43692310dcd8f1c8d7.apk"  # guangdayinghang
    # f = "./test_case/YunDaBao/ff68145c63effb9c8a86a22f24303513a9c869a3872b5079c74f1a9b12ed3d52.apk"  # xingyeyinghang
    # f = "./test_case/YunDaBao/60db0a908f9f20adfaa35f1cc6301ef21d553c470bd4e55fe40728620421b73b.apk"  # 赢美
    # f = "./test_case/YunDaBao/0b376ab37b3dd4b55ff11be35c7d542ef8960732257041c12f57e24bac1b2f36.apk"  # 给你花
    ydb = YunDaBao(f, "android")
    if ydb.doSigCheck():
        logging.info("YunDaBao signature Match")
        extract_folder, launch_path = ydb.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == '__main__':
    sys.exit(main())
