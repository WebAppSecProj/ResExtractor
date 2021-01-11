#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import json
import logging
import re
import shutil
import sys

import os
import zipfile
import Config as Config

import jpype

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class BufanApp(BaseModule):
    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.bufan.app")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):

        extract_folder = self._format_working_folder(working_folder)

        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok=True)
        tmp_folder = os.path.join(os.getcwd(), extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok=True)

        zf = zipfile.ZipFile(self.detect_file, 'r')
        appUrl = ""
        if "assets/source/dconfig.json" in zf.namelist():
            config_file = zf.extract("assets/source/dconfig.json", tmp_folder)
            fo = open(config_file, "r+")
            config_json = json.load(fo)
            appUrl = config_json["url"]
            shutil.copy(config_file, extract_folder)
        else:
            """
            get keys from smali code
            filename:  com.bufan.util.JwtUtils.smali
            """
            self._apktool(tmp_folder)
            JwtUtilsPath = os.path.join(tmp_folder, "smali/com/bufan/utils/JwtUtils.smali")
            JwtUtilsFile = open(JwtUtilsPath, "r+")
            JwtUtilsStr = JwtUtilsFile.read()
            keys = []
            patterns = [".field public static final TAG:Ljava/lang/String; = \"(.*?)\"",
                        ".field public static final key1:Ljava/lang/String; = \"(.*?)\"",
                        ".field public static final key2:Ljava/lang/String; = \"(.*?)\"",
                        ".field public static final key3:Ljava/lang/String; = \"(.*?)\"",
                        ".field public static final key4:Ljava/lang/String; = \"(.*?)\"",
                        ".field public static final key5:Ljava/lang/String; = \"(.*?)\"",
                        ".field public static final key6:Ljava/lang/String; = \"(.*?)\"",
                        ".field public static final key7:Ljava/lang/String; = \"(.*?)\"",
                        ".field public static final key8:Ljava/lang/String; = \"(.*?)\""]
            for pattern in patterns:
                pt = re.findall(pattern, JwtUtilsStr)
                keys.extend(pt)
            JwtUtilsFile.close()

            config_file = zf.extract("assets/source/config.json", tmp_folder)
            shutil.copy(config_file, extract_folder)
            jvmPath = jpype.getDefaultJVMPath()
            if not jpype.isJVMStarted():
                jpype.startJVM(jvmPath, '-ea',
                               '-Djava.class.path={0}'.format(Config.Config["decrypt_jar"]),
                               convertStrings=False)

            jclass = jpype.JClass("com.ResDecode.Main")()
            """
            get appUrl
                method: com.ResDecode.Main.get_appUrl
                input: (String) encoded JSONString, (String[]) keys
                output: (String) url
            """
            try:
                appUrl = str(jclass.get_appUrl(config_file, keys))  # cast to str
            except:
                self._log_error(os.path.basename(__file__), self.detect_file, "foo")

        self._dump_info(extract_folder, appUrl)
        # jpype.shutdownJVM()

        # clean env
        shutil.rmtree(tmp_folder)

        return extract_folder, appUrl


def main():
    # f = "./test_case/bugs/14b03ed97138c6f99f71f5bd633548c4.apk"  # need decode
    f = "./test_case/BufanApp/世耀国际_bufan.apk"
    f = "./test_case/BufanApp/惠普分期_bufan.apk"  # need decode
    # f = "./test_case/BufanApp/淘客_bufan.apk"
    bufan = BufanApp(f, "android")
    if bufan.doSigCheck():
        logging.info("BufanApp signature Match")
        extract_folder, launch_path = bufan.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
