#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 21:08:56 2020

@author: hypo
"""

import cv2
import sys
import os
import pickle
import logging

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

'''
https://www.pianshen.com/article/1315173562/
https://blog.csdn.net/zhangziju/article/details/79754652
'''

class SIFTFlannBasedMatcher:
    def __init__(self):
        self._sift = cv2.xfeatures2d.SIFT_create()
        # FLANN 参数设计
        FLANN_INDEX_KDTREE = 0
        self._index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        self._search_params = dict(checks=50)
        self._flann = cv2.FlannBasedMatcher(self._index_params, self._search_params)
        self._threshold = 0.4
        self._key_point_threshold = 100

    def debug_(self, img1, img2):

        kp1, des1, img1_h = self._get_kp_des(img1)
        kp2, des2, img2_h = self._get_kp_des(img2)
        matches = self._flann.knnMatch(des1, des2, k=2)

        good = []
        for m, n in matches:
            if m.distance < self._threshold * n.distance:
                good.append([m])

        R = float(len(good)) * 2 / (len(kp1) + len(kp2))
        log.info(R)

        imgX = cv2.drawMatchesKnn(img1_h, kp1, img2_h, kp2, good, None, flags=2)
        cv2.imshow("FLANN", imgX)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _get_kp_des(self, imgname):
        img_h = cv2.imread(imgname)
        kp, des = self._sift.detectAndCompute(img_h, None)  # des是描述子
        return kp, des, img_h

    def get_similar(self, file, db_file, DEBUG=False):
        retMe = {}
        if not os.access(db_file, os.R_OK):
            log.info("build db first")
            return
        with open(db_file, 'rb') as f:
            db = pickle.load(f)

        kp, des, _ = self._get_kp_des(file)
        for k, v in db.items():
            # if keypoint < 100
            if len(v["des"]) < self._key_point_threshold:
                continue
            try:
                matches = self._flann.knnMatch(des, v["des"], k=2)
            except:
                log.error("error matching".format(k))
                continue

            good = []
            for m, n in matches:
                if m.distance < self._threshold * n.distance:
                    good.append([m])

            R = float(len(good)) * 2 / (len(des) + len(v["des"]))
            retMe[k] = R

        return retMe

    def build_db(self, path, db_file):
        '''
        db formant:
        path: {"des": des}
        '''
        img_extension = [".bmp", ".dib", ".jpeg", ".jpg", ".jpe", ".jp2", ".png", ".webp", ".pbm", ".pgm", ".ppm", ".pxm", ".pnm", ".pfm", ".sr", ".tiff", ".tif", ".exr", ".hdr", ".pic"] # check cv2.imread
        if not os.access(db_file, os.R_OK):
            db = {}
        else:
            with open(db_file, 'rb') as f:
                db = pickle.load(f)

        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                file_in_check = os.path.join(os.path.abspath(dirpath), f)
                if not os.path.isfile(file_in_check):
                    continue
                if db.__contains__(file_in_check):
                    continue
                if os.path.splitext(file_in_check)[-1] not in img_extension:
                    continue

                try:
                    kp, des, _ = self._get_kp_des(file_in_check)
                except:
                    log.error("error when processing: {}".format(file_in_check))
                    continue

                # if len(kp) == 0:
                #     log.error("img with no enough keypoint: {}".format(file_in_check))
                #     continue
                db[file_in_check] = {"des": des}

        log.info("total {} image files are found".format(len(db)))

        with open(db_file, 'wb') as f:
            pickle.dump(db, f)

def main():
    '''
    1. build the db firstly.
    2. then feed an img file and get the result.
    '''
    m = SIFTFlannBasedMatcher()

    "for debugging"
    # m.debug_("/home/demo/Desktop/WebAppSec/ResExtractor/working_folder/xingyuan.2020.01.05/DCloud/7f467367a1d9991436cec337daf30dc945fd33c7/localres/images/src_images_but_shouc_n.png",
    #          "/home/demo/Desktop/WebAppSec/ResExtractor/working_folder/xingyuan.2020.01.05/DCloud/7f467367a1d9991436cec337daf30dc945fd33c7/localres/images/src_images_but_shouc_n.png")

    # "build db firstly"
    # m.build_db("../../working_folder", "../../img.db.pkl")

    "compare one by one"
    img = "/home/demo/Desktop/WebAppSec/ResExtractor/working_folder/xingyuan.2020.01.05/DCloud/7f467367a1d9991436cec337daf30dc945fd33c7/localres/images/src_images_toux01.png"
    res = m.get_similar(img, "../../img.db.pkl")
    showTime = 0
    for i in sorted(res.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
        if showTime < 10:
            showTime += 1
            m.debug_(img, i[0])
        log.info(i)

    # 0.03 is likely a good threshold


if __name__== "__main__":
    sys.exit(main())
