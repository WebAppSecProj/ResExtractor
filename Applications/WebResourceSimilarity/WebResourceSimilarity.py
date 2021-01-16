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

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)


def main():
    '''
    1. similarity of the layout of web resource.
    2. similarity of html.
    3. similarity of img.
    '''

    begin = time.time()



    end = time.time()
    log.info(end - begin)

if __name__== "__main__":
    sys.exit(main())
