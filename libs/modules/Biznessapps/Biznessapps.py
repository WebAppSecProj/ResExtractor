#!/usr/bin/env python3
"""
Created on Tues JAN 11 2021

@author: beizishaozi
"""

import logging
import sys
import shutil
import re
import requests
import json

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class Biznessapps(BaseModule):
    def doSigCheck(self):
        if self.host_os == "android":
            return (self._find_main_activity("com.biznessapps.main.MainActivity") or self._find_main_activity("com.bzapps.main.MainActivity"))
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
        self._apktool_no_decode_source(tmp_folder)

        t = ET.ElementTree(file=os.path.join(tmp_folder, "res/values/strings.xml"))
        txt=""
        launch_url=[]
        for elem in t.iter(tag='string'):
            name = elem.attrib['name']
            if name == 'code_name':
                txt = elem.text
        if txt != "":
            url = "https://www.cdnstabletransit.com/iphone/1.1.1/init.php?app_code="+txt+"&ba_version=50&firstRun=0&notFirstLaunch=1&device_user_id=eaae73dd691273c3&device=iphone5"
            # 2. 发送请求，获取响应
            print(url)
            res = requests.get(url=url) #res即返回的响应对象
            # 3. 解析响应
            result=res.text
            setting = json.loads(result[1:len(result)-1])  # 去掉首尾中括号
            for item in (setting['tabs']):
                #print(item)
                if 'URL' in item:
                    if item['URL'] == '0':
                        continue
                    #print(item['URL'])
                    launch_url.append(item['URL'])
        #print(launch_url)
        launch_path = " ".join(launch_url)
        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/Biznessapps/com.app_svrta.layout_4104_apps.evozi.com.apk"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径, //出错在解压缩失败//
    biznessapps = Biznessapps(f, "android")
    if biznessapps.doSigCheck():
        logging.info("Biznessapps signature Match")

        extract_folder, launch_path = biznessapps.doExtract("working_fold")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
