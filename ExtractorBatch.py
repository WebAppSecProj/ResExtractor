#!/usr/bin/env python3

import sys
import Config
import importlib
import logging
import os
import zipfile
import libs.Stats as Stats

import Checker

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

stats = Stats.Stats()

def doCheck(file_in_check):

    distill_modules = []
    # load each module
    for m in Config.Config["modules"].keys():
        module = getattr(
            importlib.import_module(m),
            Config.Config["modules"][m]
        )

        # TODO:: verify each module
        if getattr(module, "doSigCheck") and getattr(module, "doExtract"):
            distill_modules.append(module(file_in_check, "android"))

    for m in distill_modules:
        if m.doSigCheck():
            stats.add_entity(m.__class__)
            logging.info("{} signature Match".format(m.__class__))
            extract_folder, launch_path = m.doExtract(Config.Config["working_folder"])
            log.info("{} is extracted to {}, the start page is {}".format(file_in_check, extract_folder, launch_path))

    # fork the service ?
    # fork the webdriver
    return

def main():
    if Checker.doEnvCheck() == False:
        sys.exit(1)

    for dirpath, dirnames, ifilenames in os.walk(sys.argv[1]):
        for fs in ifilenames:
            file_in_check = os.path.join(dirpath, fs)
            if not os.path.isfile(file_in_check):
                continue
            log.info(file_in_check)
            if Checker.doAPKCheck(file_in_check):
                stats.add_entity()
                doCheck(file_in_check)

    stats.doState()

if __name__ == "__main__":
    sys.exit(main())
