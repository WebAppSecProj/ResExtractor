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
import os
import pickle
import networkx as nx
import matplotlib.pyplot as plt

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

def recursive_search():

    return

def main():
    '''
    1. build the db firstly.
    2. then feed an img file and get the result.
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('--img-folder', help="Folder contains img files.")
    parser.add_argument('--db-file', required=True, help="db file for preserving keypoint of images.")
    parser.add_argument('--sim-threshold', help="similarity threshold.")
    parser.add_argument('--cluster-only', action='store_true', help="cluster only.")
    #parser.add_argument('--ana-result', help="analysis result.")

    args = parser.parse_args()

    begin = time.time()

    if not args.cluster_only and args.img_folder and args.db_file:
        m = img_similarity.SIFTFlannBasedMatcher()
        m.build_signature_db(args.img_folder, args.db_file, incremental=True)

    if not args.cluster_only and args.db_file:
        img_extension = [".bmp", ".dib", ".jpeg", ".jpg", ".jpe", ".jp2", ".png", ".webp", ".pbm", ".pgm", ".ppm",
                         ".pxm", ".pnm", ".pfm", ".sr", ".tiff", ".tif", ".exr", ".hdr", ".pic"]  # check cv2.imread
        R = {}
        for dirpath, dirnames, filenames in os.walk(args.img_folder):
            for f in filenames:
                file_in_check = os.path.join(os.path.abspath(dirpath), f)
                if not os.path.isfile(file_in_check):
                    continue
                if os.path.splitext(file_in_check)[-1].lower() not in img_extension:
                    continue

                log.info("processing: {}".format(file_in_check))
                res = m.search_img(file_in_check, args.db_file)
                R[os.path.splitext(os.path.basename(file_in_check))[-2]] = res
                for i in sorted(res.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
                    log.info(i)
            with open("./Applications/ScreenShotSimilarity/screenshot_similar_db.pkl", 'wb') as f:
                pickle.dump(R, f)

    sim_threshold = 0.3
    if args.sim_threshold:
        sim_threshold = float(args.sim_threshold)

    with open("./Applications/ScreenShotSimilarity/screenshot_similar_db.pkl", 'rb') as f:
        db = pickle.load(f)
    # log.info(db)
    # {file, {file, ratio}}

    # similar_db layout: {hash-of-apk1, {hash-of-apk2: sim-ratio1-2}}
    # new layout:[set, set]
    G = []
    for k, v in db.items():
        g = set([k])        # init g
        for k1, v1 in v.items():
            if v1 > sim_threshold:
                g.add(k1)
        G.append(g)

    GN = []
    for g in G:
        skip = False
        for gt in GN:
            if g.issubset(gt):      # has been merged
                skip = True
                break
        if skip == True:
            continue

        # work list algo
        gn = g                         # init gn
        while True:
            stable = True
            for gt in G:
                if gn.isdisjoint(gt) or gt.issubset(gn):
                    continue
                gn = gn.union(gt)
                stable = False

            if stable == True:
                break
        GN.append(gn)

    for i in GN:
        log.info(i)
    # ugly view.
    G = nx.DiGraph()
    for k, v in db.items():
        log.info("next group pic")
        for k1, v1 in v.items():
            if v1 > sim_threshold:
                log.info("{} -> {}, {}".format(k, k1, v1))
                G.add_weighted_edges_from([(k, k1, v1)])
    nx.draw_networkx(G)
    plt.show()

    # 0.03 is likely a good threshold

    end = time.time()
    log.info(end - begin)

if __name__== "__main__":
    sys.exit(main())
