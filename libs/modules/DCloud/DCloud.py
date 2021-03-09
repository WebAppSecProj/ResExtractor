#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/3/9 15:03
# @Author  : fy
# @FileName: DCloud.py

import logging
import os
import sys
import zipfile
import shutil
import json
from Crypto.Cipher import DES
from libs.modules.BaseModule import BaseModule

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: https://dcloud.io/

Reference:
1) https://uniapp.dcloud.net.cn/
2) https://dcloud.io/wap2app.html?platform=wap2app (not yet)
'''


class DCloud(BaseModule):
    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("io.dcloud.PandoraEntry")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):

        extract_folder = self._format_working_folder(working_folder)
        launch_path = ""

        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok=True)
        tmp_folder = os.path.join(os.getcwd(), extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok=True)

        # extract the assets/data/dcloud_control.xml to get appid
        zf = zipfile.ZipFile(self.detect_file, 'r')

        if "assets/data/dcloud_control.xml" in zf.namelist():
            config_file = zf.extract("assets/data/dcloud_control.xml", tmp_folder)
            # parse the xml file, construct the path of app code, and extract
            appid = ""
            t = ET.ElementTree(file=config_file)
            for elem in t.iter(tag='app'):
                appid = elem.attrib['appid']
            code_dir = "assets/apps/{}/www/".format(appid)
            for f in zf.namelist():
                if f.startswith(code_dir):
                    # print(f)
                    # create dir anyway
                    td = os.path.dirname(os.path.join(extract_folder, f[len(code_dir):]))
                    if not os.access(td, os.R_OK):
                        os.makedirs(td)
                    with open(os.path.join(extract_folder, f[len(code_dir):]), "wb") as fwh:
                        fwh.write(zf.read(f))
            # extracting the starting page
            try:
                j = json.load(open(os.path.join(extract_folder, "manifest.json"), 'r'))
                launch_path = j['launch_path']
                self._dump_info(extract_folder, j['launch_path'])
            except:
                self._log_error(os.path.basename(__file__), self.detect_file, "foo")

        else:
            # Fix possible vulnerabilities caused by handling "nonspacing mark" file
            # nonspacing mark 非间隔标记 (https://www.fileformat.info/info/unicode/category/Mn/list.htm)
            keyfile, enfile = b'', b''
            list_asset_file = []
            for file_in_zip in zf.namelist():
                if file_in_zip.startswith("assets/"):
                    list_asset_file.append(file_in_zip)
            file1, file2 = zf.read(list_asset_file[0]), zf.read(list_asset_file[1])
            if len(list_asset_file) == 2:
                len1, len2 = len(file1), len(file2)
                if len1 < len2:
                    keyfile, enfile = file1, file2
                else:
                    keyfile, enfile = file2, file1
            else:
                print("assets files error")
            keyfile = keyfile.decode()
            key_offset = int(keyfile[(len(keyfile) - 33 - int(keyfile[-1])):(len(keyfile) - 33)])
            key = keyfile[key_offset: key_offset + 8].encode()
            defile = DES.new(key[:8], DES.MODE_ECB).decrypt(enfile)
            filename = os.path.join(tmp_folder, 'tmp_assets.zip')
            with open(filename, 'wb') as file_object:
                file_object.write(defile)
            zz = zipfile.ZipFile(filename)
            zz.extractall(extract_folder)
            config_file = os.path.join(extract_folder, "assets/data/dcloud_control.xml")
            appid = ""
            t = ET.ElementTree(file=config_file)
            for elem in t.iter(tag='app'):
                appid = elem.attrib['appid']
            code_dir = "assets/apps/{}/www/".format(appid)
            try:
                j = json.load(open(os.path.join(extract_folder, code_dir, "manifest.json"), 'r'))
                launch_path = j['launch_path']
                self._dump_info(extract_folder, j['launch_path'])
            except:
                self._log_error(os.path.basename(__file__), self.detect_file, "foo")

        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/io.dcloud.PandoraEntry/103a97f1a8cdbe9a4f80187279f3b78f9e0e7acd.apk"
    # f = "./test_case/io.dcloud.PandoraEntry/优优直播-0db09368a72d287ca0a37785d4efee29.apk"
    dCloud = DCloud(f, "android")
    if dCloud.doSigCheck():
        logging.info("DCloud signature Match")
        extract_folder, launch_path = dCloud.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
