#!/usr/bin/env python3
"""
Created on Wed Dec 25 2020

@author: beizishaozi
"""
import logging
import sys
import zipfile
import shutil
import subprocess
import Config as Config

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Reference:
1) http://cordova.axuer.com/docs/zh-cn/latest/guide/support/index.html
'''

# extracting the starting page from "res/xml/config.xml" in "<content src="index.html" />"

class Cordova(BaseModule):
    def doSigCheck(self):
        if self.host_os == "android":
            # Cordova app's signature is the apk which contain the file "/assets/www/cordova.js /assets/www/cordova_plugin.js /assets/www/cordova-js-src"
            zf = zipfile.ZipFile(self.detect_file, 'r')
            flag1 = 0
            flag2 = 0
            for f in zf.namelist():
                if f.startswith("assets/www/cordova-js-src"):
                    flag1 = 1
                elif f == "assets/www/cordova.js":
                    flag2 = flag2 + 1
                elif f == "assets/www/cordova_plugins.js":
                    flag2 = flag2 + 1
            if flag1+flag2 == 3:
                return True
            return False

            #return self._find_main_activity("cordova.MainActivity")
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

        zf = zipfile.ZipFile(self.detect_file, 'r')

        launch_path = ""

        for f in zf.namelist():
            if f.startswith("assets/www/"):

                td = os.path.dirname(os.path.join(extract_folder, f[len("assets/www/"): ]))
                if not os.access(td, os.R_OK):
                    os.makedirs(td)
                with open(os.path.join(extract_folder, f[len("assets/www/"): ]), "wb") as fwh:
                    fwh.write(zf.read(f))
            elif f == "res/xml/config.xml":

                # extracting the starting page in "<content src="index.html" />" from "res/xml/config.xml"
                # Ugly coding, I would like to use ElementTree instead.
                proc = subprocess.Popen("{} dump xmltree '{}' '{}'".format(Config.Config["aapt_ubuntu"], self.detect_file, "res/xml/config.xml"),
                                        shell=True, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                r = (proc.communicate()[0]).decode()
                #只匹配标签src可能存在多个答案，因此还需要配合标签content来确定，应该是标签content之后的第一个src的值才是起始页真正地址
                launch_path = "no found"
                contid = r.find("E: :content")
                if contid >= 0:
                    cont = r[contid+11:]
                    srcid = cont.find("A: src")
                    if srcid >= 0:
                        launch_path = (cont[srcid:].split("\""))[1]

                #只匹配标签src可能存在多个答案
                #matchObj = re.match(r'(.*)A: src=\"(.*?)\" \((.*)', r, re.S)
                #if matchObj:
                #    launch_path = matchObj.group(2)
                #else:
                #    log.error("internal error")

        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/Cordova/bjgas.apk"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径
    cordova = Cordova(f, "android")
    if cordova.doSigCheck():
        logging.info("cordova signature Match")

        extract_folder, launch_path = cordova.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
