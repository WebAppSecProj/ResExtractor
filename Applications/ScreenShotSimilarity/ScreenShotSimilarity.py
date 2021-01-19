#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 21:08:56 2020

@author: hypo
"""

import sys
import logging
import time
import argparse
import Applications.common.img_similarity as img_similarity
import pickle

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)


def main():
    '''
    1. build the db firstly.
    2. then feed an img file and get the result.
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('--img-folder', help="Folder contains img files.")
    parser.add_argument('--img-file', help="img file for searching.")
    parser.add_argument('--db-file', required=True, help="db file for preserving keypoint of images.")
    parser.add_argument('--DEBUG', help="show designate number of similar img.")

    args = parser.parse_args()
    if not args.img_folder and not args.img_file:
        log.error("Should provide either img-folder or img-file argument")
        exit(1)

    begin = time.time()

    m = img_similarity.SIFTFlannBasedMatcher()

    if args.img_folder and args.db_file:
        m.build_signature_db(args.img_folder, args.db_file, incremental=True)

    if args.db_file and args.img_file:
        res = m.search_img(args.img_file, args.db_file)
        showTime = 0
        for i in sorted(res.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
            log.info(i)
            if args.DEBUG:
                with open(args.db_file, 'rb') as f:
                    db = pickle.load(f)

                if showTime < int(args.DEBUG):
                    showTime += 1
                    m.debug_(args.img_file, db[i[0]]["file"])

    # 0.03 is likely a good threshold

    end = time.time()
    log.info(end - begin)

if __name__== "__main__":
    sys.exit(main())