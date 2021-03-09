#!/usr/bin/env python3

import sys
import Config
import importlib
import logging
import Checker
import argparse
import os

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apk-file', required=True, help="The apk file.")
    parser.add_argument('--task-name', required=True, help="Provide name of this task, such that we can classify the analysis result.")

    args = parser.parse_args()

    if Checker.doEnvCheck() == False:
        sys.exit(1)

    new_apk_file = Checker.doAPKCheck(args.apk_file)
    if new_apk_file == False:
        sys.exit(1)

    for k in Config.Config["modules"].keys():
        m = getattr(
            importlib.import_module(k),
            Config.Config["modules"][k]
        )
        # TODO:: verify each module
        if getattr(m, "doSigCheck") and getattr(m, "doExtract"):
            mod_inst = m(new_apk_file, "android")
            if mod_inst.doSigCheck():
                logging.info("{} signature Match".format(mod_inst.__class__))
                extract_folder, launch_path = mod_inst.doExtract(os.path.join(Config.Config["working_folder"], args.task_name, Config.Config["modules"][k]))
                log.info("{} is extracted to {}, the start page is {}".format(new_apk_file, extract_folder, launch_path))

    return


if __name__ == "__main__":

    sys.exit(main())
