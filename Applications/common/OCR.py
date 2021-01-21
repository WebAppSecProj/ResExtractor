#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 21:08:56 2020

@author: hypo
"""

import sys
import logging
import pytesseract
import time
import subprocess

from PIL import Image
from aip import AipOcr

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

'''
yes, this is quite simple
'''
class OCR_baiduAI:
    def __init__(self):
        self._client = AipOcr("23568294", "xk7FKq0AyfanW6kzOhY9jcNq", "V7AS38Pku8s3GZcdQ6bT2EXnMltNfjiM")

    def get_literal(self, file):
        '''
        http://ai.baidu.com/productlist#tech
        https://ai.baidu.com/ai-doc/OCR/wkibizyjk
        '''

        with open(file, 'rb') as fp:
            image = fp.read()

            """ 调用通用文字识别, 图片参数为本地图片 """
            self._client.basicGeneral(image);

            """ 如果有可选参数 """
            options = {}
            options["language_type"] = "CHN_ENG"
            options["detect_direction"] = "true"
            options["detect_language"] = "true"
            options["probability"] = "true"

            """ 带参数调用通用文字识别, 图片参数为本地图片 """
            return self._client.basicGeneral(image, options)


class OCR_tesseract:
    def __init__(self):
        pass

    def get_literal(self, file):
        '''
        https://blog.csdn.net/dcrmg/article/details/78128026
        https://blog.csdn.net/qq_37372196/article/details/89863593
        https://github.com/tesseract-ocr/tessdata
        '''
        # tesseract env required
        proc = subprocess.Popen("tesseract --version ", shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[1]).decode()
        if r.find("not found") != -1:
            log.error("tesseract required.")
            return False

        image = Image.open(file)
        try:
            chi_sim = pytesseract.image_to_string(image, lang='chi_sim')
        except:
            log.error("setup lang supported.")
            return False
        return chi_sim

def main():
    '''
    1. build the db firstly.
    2. then feed an img file and get the result.
    '''
    begin = time.time()
    # o = OCR_tesseract("/home/demo/Desktop/WebAppSec/ResExtractor/working_folder/snapshot/9715c1fffc9b6beb1860b3e93dee2b8071b9ac15.png")
    file = '/home/demo/Desktop/WebAppSec/ResExtractor/working_folder/snapshot/ce27081e970cfa016d338a21005fe940ee3de2be.png'
    o = OCR_tesseract()
    R = o.get_literal(file)
    log.info(R)

    o = OCR_baiduAI()
    R = o.get_literal(file)
    # process error
    if R.__contains__("error_code"):
        log.error("visit https://ai.baidu.com/ai-doc/OCR/zkibizyhz for reason.")
    for r in R["words_result"]:
        log.info(r["words"])

    end = time.time()
    print(end - begin)

if __name__== "__main__":
    sys.exit(main())
