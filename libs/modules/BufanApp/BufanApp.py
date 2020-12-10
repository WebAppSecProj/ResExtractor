#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import shutil
import sys

import os
import zipfile

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
            return self._find_main_activity("com.bufan.app.SplashActivity")
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
        config_file = zf.extract("assets/source/config.json", tmp_folder)
        decode_jar_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "decode_bufan.jar")
        MyJSON_jar_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "MyJSON.jar")
        jvmPath = jpype.getDefaultJVMPath()
        if not jpype.isJVMStarted():
            jpype.startJVM(jvmPath, '-ea', '-Djava.class.path={0}:{1}'.format(decode_jar_path, MyJSON_jar_path),
                           convertStrings=False)
        jclass = jpype.JClass("com.decode.Main")()
        appUrl = jclass.get_appUrl(config_file)

        """
        decode JSONString
            method: com.decode.JwtUtils.mainDecode
            input: (String) encoded JSONString
            output: (String) JSONString
        """
        jwtclass = jpype.JClass("com.decode.JwtUtils")
        log.info(jwtclass.mainDecode(jclass.readJSON(config_file)))

        self._dump_info(extract_folder, appUrl)
        # jpype.shutdownJVM()
        return extract_folder, appUrl


def main():
    f = "./test_case/BufanApp/bufan1.apk"
    bufan = BufanApp(f, "android")
    if bufan.doSigCheck():
        logging.info("BufanApp signature Match")
        extract_folder, launch_path = bufan.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
