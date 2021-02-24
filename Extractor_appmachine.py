#!/usr/bin/env python3

import sys
import Config
import importlib
import logging
import Checker
import argparse
import os
import libs.modules.AppMachine.AppMachine
logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)


def main():
    f = "./test_case/AppMachine/del2.ipa"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径
    AppMachine = libs.modules.AppMachine.AppMachine.AppMachine(f, "ios")
    if AppMachine.doSigCheck():
        logging.info("AppMachine signature Match")
        extract_folder, launch_path = AppMachine.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return


if __name__ == "__main__":

    sys.exit(main())
