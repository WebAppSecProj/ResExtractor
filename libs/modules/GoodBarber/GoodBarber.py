#!/usr/bin/env python3
"""
Created on Tues JAN 05 2021

@author: beizishaozi
"""

import logging
import sys
import shutil
import re
import json
import zipfile

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class GoodBarber(BaseModule):
    def extract_startpage(self, filepath):
        with open(filepath, 'r') as load_f:
            load_dict = json.load(load_f)
        launch_url = []
        flag = 0
        sections = load_dict['gbsettings']['sections']
        for value in sections.values():
            for (k, v) in value.items():
                if v == 'GBModuleTypeCustom':   #指的是自定义模块HTML，支持本地页面或者url链接，如果是url链接会存在key为url的项，本地页面则是存在key为sectionurl的项
                    flag = flag + 1
                elif v == 'GBModuleTypeClickto':    #指的是自定义链接linkto
                    launch_url.append(value['link']['url'])
                elif v == 'GBModuleTypeArticle':
                    launch_url.append(value['baseUrl'])  #指的是自定义RSS链接
                elif k == 'url':
                    flag = flag + 1
            if flag == 2:
                launch_url.append(value['url'])
        return " ".join(launch_url)

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.goodbarber.v2.core.common.activities.SplashscreenActivity")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)
        tmp_folder = os.path.join(os.getcwd(), extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok = True)
        #self._apktool_no_decode_source(tmp_folder)  #用apktool反编译出错，即使是用最新版apktool反编译仍然报错，为解压提取
        z = zipfile.ZipFile(self.detect_file, 'r')
        z.extractall(tmp_folder)
        z.close()

        for dirpath, dirnames, ifilenames in os.walk(tmp_folder):
            if dirpath.find("assets/cache/settings/plugins") != -1:   #自定义页面保存在assets/cache/settings/plugins中
                for fs in ifilenames:
                    f = os.path.join(dirpath, fs)
                    matchObj = re.match(r'(.*)assets/cache/settings/plugins/(.*)', f, re.S)
                    newRP = matchObj.group(2)

                    tf = os.path.join(extract_folder, newRP)
                    if not os.access(os.path.dirname(tf), os.R_OK):
                        os.makedirs(os.path.dirname(tf))
                    with open(tf, "wb") as fwh:  #output the
                        # ugly coding
                        fp = open(os.path.join(dirpath, fs), "rb")
                        c = fp.read()
                        fp.close()
                        fwh.write(c)
                    fwh.close()
        #7b070bc294d48bb947a2b4e0885cd58是固定的，因为这是“settings_json”的md5值
        launch_path = self.extract_startpage(os.path.join(tmp_folder, "assets/cache/settings/7b070bc294dc48bb947a2b4e0885cd58"))

        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/GoodBarber/mivoice.apk"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径, //出错在解压缩失败//
    goodbarber = GoodBarber(f, "android")
    if goodbarber.doSigCheck():
        logging.info("GoodBarber signature Match")

        extract_folder, launch_path = goodbarber.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
