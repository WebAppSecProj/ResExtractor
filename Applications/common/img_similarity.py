#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 21:08:56 2020

@author: hypo
"""

import cv2
import numpy as np
import sys

'''
https://www.pianshen.com/article/1315173562/
https://blog.csdn.net/zhangziju/article/details/79754652
'''
def SIFT_FlannBasedMatcher(imgname1, imgname2):

    sift = cv2.xfeatures2d.SIFT_create()

    # FLANN 参数设计
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    img1 = cv2.imread(imgname1)
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)  # 灰度处理图像
    kp1, des1 = sift.detectAndCompute(img1, None)  # des是描述子

    img2 = cv2.imread(imgname2)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    kp2, des2 = sift.detectAndCompute(img2, None)

    # hmerge = np.hstack((gray1, gray2))  # 水平拼接
    # cv2.imshow("gray", hmerge)  # 拼接显示为gray
    # cv2.waitKey(0)

    # img3 = cv2.drawKeypoints(img1, kp1, img1, color=(255, 0, 255))
    # img4 = cv2.drawKeypoints(img2, kp2, img2, color=(255, 0, 255))

    # hmerge = np.hstack((img3, img4))  # 水平拼接
    # cv2.imshow("point", hmerge)  # 拼接显示为gray
    # cv2.waitKey(0)
    matches = flann.knnMatch(des1, des2, k=2)
    matchesMask = [[0, 0] for i in range(len(matches))]

    good = []
    for m, n in matches:
        if m.distance < 0.6 * n.distance:
            good.append([m])

    R = float(len(good)) / (len(kp1) + len(kp2))
    print(R)

    img5 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=2)
    cv2.imshow("FLANN", img5)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    SIFT_FlannBasedMatcher("./img_sim_1-1.png", "./img_sim_1-2.jpg")
    # drawMatchLine("./img_sim_2-1.jpg", "./img_sim_2-2.jpg")
    # SIFT_FlannBasedMatcher("./img_sim_2-1.jpg", "./img_sim_1-1.png")
    # drawMatchLine("./img_sim_2-2.jpg", "./img_sim_2-3.png")
    # drawMatchLine("./img_sim_2-3.png", "./img_sim_2-4.png")

if __name__== "__main__":
    sys.exit(main())
