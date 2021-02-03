#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import json
import sys
import logging
import shutil
import os
import zipfile

from libs.modules.BaseModule import BaseModule

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: https://trigger.io/
'''


class Trigger(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("io.trigger.forge.android.core.ForgeActivity")
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

        # copy resource dir ("assets/") to working_folder
        resource_path = os.path.join(tmp_folder, "assets/")
        shutil.copytree(resource_path, extract_folder, dirs_exist_ok=True)

        zf = zipfile.ZipFile(self.detect_file, 'r')
        config_file = zf.extract("assets/app_config.json", tmp_folder)
        config_json = json.load(open(config_file, "r+"))

        # local address(fixed-port)
        # https://localhost:44300/assets/src/index.html
        launch_path = "assets/src/index.html"
        if 'core' in config_json:
            if 'general' in config_json['core']:
                if 'url' in config_json['core']['general']:
                    launch_path = config_json["core"]["general"]["url"]
                elif 'live' in config_json['core']['general']:
                    if 'enabled' in config_json['core']['general']['live']:
                        launch_path = config_json["core"]["general"]["live"]['url']
        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    # f = "./test_case/Trigger/helloworld-nosethomepage.apk"
    # f = "./test_case/Trigger/helloworld-sethomepage.apk"
    # f = "./test_case/Trigger/helloworld-addnewjs.apk"
    f = "./test_case/Trigger/7Cups_Trigger.apk"
    trigger = Trigger(f, "android")
    if trigger.doSigCheck():
        logging.info("Trigger signature Match")
        extract_folder, launch_path = trigger.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
