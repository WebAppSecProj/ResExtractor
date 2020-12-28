#!/usr/bin/env python3

import sys
import Config
import importlib
import logging
import EnvChecker

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


def main():
    if EnvChecker.doCheck() == False:
        sys.exit(1)

    distill_modules = []
    # load each module
    for m in Config.Config["modules"].keys():
        module = getattr(
            importlib.import_module(m),
            Config.Config["modules"][m]
        )

        # TODO:: verify each module
        if getattr(module, "doSigCheck") and getattr(module, "doExtract"):
            distill_modules.append(module(sys.argv[1], "android"))

    for m in distill_modules:
        if m.doSigCheck():
            logging.info("{} signature Match".format(m.__class__))
            extract_folder, launch_path = m.doExtract(Config.Config["working_folder"])
            log.info("{} is extracted to {}, the start page is {}".format(sys.argv[1], extract_folder, launch_path))

    # fork the service ?
    # fork the webdriver
    return


if __name__ == "__main__":
    sys.exit(main())
