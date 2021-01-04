#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import json
import sys
import logging
import shutil
import os

from libs.modules.BaseModule import BaseModule

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info:  https://nativescript.org/#
Related Blog1: https://juejin.cn/post/6844903840324517895 （工作原理）
Related Blog2: https://zhuanlan.zhihu.com/p/21458458 （基础开发）
'''


class NativeScript(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.tns.NativeScriptActivity")
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

        # copy resource dir ("assets/app") to working_folder
        resource_path = os.path.join(tmp_folder, "assets/app")
        shutil.copytree(resource_path, extract_folder, dirs_exist_ok=True)

        # get assets/app/package.json
        # package.json是应用的配置信息，描述应用程序的特征和依赖项，json中的"main"标签对应的应用启动文件
        json_path = os.path.join(tmp_folder, "assets/app/package.json")
        fo = open(json_path, "r+")
        fo_file = json.load(fo)
        launch_path = "assets/app/" + fo_file['main']
        self._dump_info(extract_folder, launch_path)

        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    # f = "./test_case/NativeScript/base.apk"  # not package.json
    f = "./test_case/NativeScript/f8ed6f7e898b2a6311456c38eff1afa3c2ac0d8efe42213a337dbb992a56a32b.apk"
    # f = "./test_case/NativeScript/fea2b53a94fbb87b8d648bfa1682ab8a4a8986392ec0b802df68006297ae9f09.apk"
    ns = NativeScript(f, "android")
    if ns.doSigCheck():
        logging.info("NativeScript signature Match")
        extract_folder, launch_path = ns.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
