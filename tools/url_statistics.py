#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 11:30:59 2020

@author: hypo
"""

import os, sys, logging, argparse, csv, re

import Config as Config
import datetime
import shutil

from urllib.parse import urlparse, urljoin
from libs.WebUtil import WebUtil

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)


if __name__ == "__main__":

    res_url = {}
    res_domain = {}
    for dirpath, dirnames, ifilenames in os.walk(Config.Config["working_folder"]):
        for fs in ifilenames:
            file_in_check = os.path.join(dirpath, fs)
            if not os.path.isfile(file_in_check):
                continue
            if fs == Config.Config["remote_res_info"]:
                log.info(file_in_check)

                with open(file_in_check, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    row = [col['URL'] for col in reader]
                    for u in row:
                        res_url[u] = res_url.get(u, 0) + 1
                        d = urlparse(u).netloc
                        res_domain[d] = res_domain.get(d, 0) + 1

    log.info("url info list:")
    for i in sorted(res_url.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
        log.info(i)

    log.info("domain info list:")
    for i in sorted(res_domain.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
        log.info(i)

    log.info("copy to my_filter.txt file:")
    for i in sorted(res_domain.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
        if i[1] > 8:
            print(i[0])

