#!/usr/bin/env python3
"""
Created on Tues JAN 11 2021

@author: beizishaozi
"""

import logging
import sys
import shutil
import re
import zipfile

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class SeattleCloud(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return (self._find_main_activity("com.seattleclouds.AppStarterActivity") or self._find_main_activity("com.qbiki.seattleclouds.AppStarterActivity"))
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

        z = zipfile.ZipFile(self.detect_file, 'r')
        z.extractall(tmp_folder)
        z.close()

        #一般情况下，app.xml文件都是存在的，还未遇到不存在的情况，为了预防这种情况。如果不存在app.xml，则将assets目录下后缀为html\js\css的文件输出
        if os.path.exists(os.path.join(tmp_folder, "assets/Main/app.xml")):
            t = ET.ElementTree(file=os.path.join(tmp_folder, "assets/Main/app.xml"))
            for elem in t.iter(tag='xml'):
                for subelem in elem.iter(tag='page'):
                    resfile = subelem.attrib['id']
                    tf = os.path.join(extract_folder, resfile)
                    if not os.access(os.path.dirname(tf), os.R_OK):
                        os.makedirs(os.path.dirname(tf))
                    with open(tf, "wb") as fwh:  #output the
                         # ugly coding
                        fp = open(os.path.join(tmp_folder, "assets/Main", resfile), "rb")
                        c = fp.read()
                        fp.close()
                        fwh.write(c)
                    fwh.close()
        else:
            for dirpath, dirnames, ifilenames in os.walk(tmp_folder):
                if dirpath.find("assets") != -1:
                    for fs in ifilenames:
                        if fs.endswith(".html") == False:
                            continue
                        elif fs.endswith(".js") == False:
                            continue
                        elif fs.endswith(".css") == False:
                            continue
                        f = os.path.join(dirpath, fs)
                        matchObj = re.match(r'(.*)assets/(.*)', f, re.S)
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
        launch_path=""
        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/SeattleCloud/saving-your-relationship_5.0.apk"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径, //出错在解压缩失败//
    seattlecloud = SeattleCloud(f, "android")
    if seattlecloud.doSigCheck():
        logging.info("GoodBarber signature Match")

        extract_folder, launch_path = seattlecloud.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
