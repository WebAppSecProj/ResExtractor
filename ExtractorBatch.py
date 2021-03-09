#!/usr/bin/env python3

import sys
import Config
import importlib
import logging
import os
import argparse
import libs.Stats as Stats

import Checker

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

stats = Stats.Stats()

def doCheck(file_in_check, task_name):

    distill_modules = []
    # load each module
    for k in Config.Config["modules"].keys():
        m = getattr(
            importlib.import_module(k),
            Config.Config["modules"][k]
        )
        # TODO:: verify each module
        if getattr(m, "doSigCheck") and getattr(m, "doExtract"):
            mod_inst = m(file_in_check, "android")
            if mod_inst.doSigCheck():
                stats.add_entity(mod_inst.__class__)
                logging.info("{} signature Match".format(mod_inst.__class__))
                extract_folder, launch_path = mod_inst.doExtract(os.path.join(Config.Config["working_folder"], task_name, Config.Config["modules"][k]))
                log.info("{} is extracted to {}, the start page is {}".format(file_in_check, extract_folder, launch_path))

    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apk-folder', required=True, help="Folder contains apk files.")
    parser.add_argument('--task-name', required=True, help="Provide name of this task, such that we can classify the analysis result.")

    args = parser.parse_args()

    if Checker.doEnvCheck() == False:
        sys.exit(1)

    for dirpath, dirnames, ifilenames in os.walk(args.apk_folder):
        for fs in ifilenames:
            file_in_check = os.path.join(dirpath, fs)
            if not os.path.isfile(file_in_check):
                continue
            log.info(file_in_check)
            new_apk_file = Checker.doAPKCheck(file_in_check)
            if new_apk_file != False:
                stats.add_entity()
                doCheck(new_apk_file, args.task_name)

    stats.doState()

if __name__ == "__main__":
    sys.exit(main())
