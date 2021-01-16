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
import Applications.common.HTMLSimilarity.HTMLSimilarityWrapper as HTMLSimilarityWrapper

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)


def main():
    '''
    1. build the db firstly.
    2. then feed a html file and get the result.
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('--html-folder', help="Folder containing html files.")
    parser.add_argument('--html-file', help="html file for searching.")
    parser.add_argument('--db-file', required=True, help="db file for preserving eigenvector of html files.")

    args = parser.parse_args()
    if not args.html_folder and not args.html_file:
        log.error("Should provide either html-folder or html-file argument")
        exit(1)

    begin = time.time()

    s = HTMLSimilarityWrapper.HTMLSimilarityWrapper()

    if args.html_folder and args.db_file:
        s.build_db(args.html_folder, args.db_file)

    if args.db_file and args.html_file:
        res = s.search_html(args.html_file, args.db_file)

        for i in sorted(res.items(), key=lambda kv: (kv[1], kv[0]), reverse=False):
            log.info(i)

    end = time.time()
    log.info(end - begin)

if __name__== "__main__":
    sys.exit(main())
