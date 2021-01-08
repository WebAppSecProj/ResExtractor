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
from deprecated.sphinx import deprecated
from hashlib import md5
from urllib.parse import urlparse, urljoin

from libs.WebUtil import WebUtil

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

class Web_resource():
    def __init__(self, dirpath, appname="FOO"):
        if os.path.exists(dirpath):
            self._dir = dirpath
        else:
            self._dir = None
        self._appname = appname
        self._url_list = None
        self._format_list = None
        self._notformat_list = None
        self._HTTP_REGEX = 'https?://[a-zA-Z0-9\.\/_&=@$%?~#-]+'
        self._IP_REGEX = '(((1[0-9][0-9]\.)|(2[0-4][0-9]\.)|(25[0-5]\.)|([1-9][0-9]\.)|([0-9]\.)){3}((1[0-9][0-9])|(2[0-4][0-9])|(25[0-5])|([1-9][0-9])|([0-9])))'
        # 非文本后缀
        self._notfile = ["jpg", "png", "gif", "bmp", "webp", "jepg", "tgz"]
        self._formats = ["jpg", "png", "gif", "bmp", "webp", "jepg", "tgz", "txt", "js", "css"]

    @property
    def allurl(self):
        if self._url_list == None:
            if self._dir:
                self._url_list = []
                for root, dirs, files in os.walk(self._dir):
                    for f in files:
                        if any(f.endswith(i) for i in self._notfile):
                            continue
                        fp = os.path.join(root, f)
                        if not os.path.isfile(fp):
                            continue
                        try:
                            with open(fp, 'r', encoding='utf-8') as fs:
                                self._url_list.extend(re.findall(self._HTTP_REGEX, fs.read()))
                        except:
                            continue
                        self._url_list = list(set(self._url_list))
                return self._url_list
            return None
        else:
            return self._url_list

    def del_top(self, filter_file):
        if self.allurl == None:
            return None
        if filter_file.endswith(".csv"):
            try:
                with open(filter_file, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    row = [col['web'] for col in reader]
                    for i in row:
                        for j in self.allurl.copy():
                            # if i.find("opensource.org") != -1 and j.find("opensource.org") != -1:
                            #     log.info("FOO")
                            if not i.lower().startswith("www."):
                                i = "www." + i
                            k = urlparse(j).netloc
                            if not k.lower().startswith("www."):
                                k = "www." + k
                            if i.lower() == k.lower():
                                log.info("url removed: {} by filter: {}".format(j, filter_file))
                                self.allurl.remove(j)
            except:
                pass
        if filter_file.endswith(".txt"):
            try:
                with open(filter_file, 'r') as txt:
                    row = txt.read().splitlines()
                    for i in row:
                        for j in self.allurl.copy():
                            if not i.lower().startswith("www."):
                                i = "www." + i
                            k = urlparse(j).netloc
                            if not k.lower().startswith("www."):
                                k = "www." + k
                            if i.lower() == k.lower():
                                log.info("url removed: {} by filter: {}".format(j, filter_file))
                                self.allurl.remove(j)
            except:
                pass

    @property
    def purified_url(self):
        return self._notformat_list

    def _purify_url(self):
        if self.allurl == None:
            return None
        self._format_list = []
        self._notformat_list = []
        for i in self.allurl.copy():
            if any(i.endswith(t) for t in self._formats):
                self._format_list.append(i)
            else:
                self._notformat_list.append(i)
        return self._format_list, self._notformat_list


    def dump(self, filepath, method="csv"):
        if self.allurl == None:
            return None
        _, _ = self._purify_url()

        if method == "csv":
            if not os.path.exists(filepath):
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w', newline='') as f:
                    f_csv = csv.writer(f)
                    f_csv.writerow(['appname', 'URL', 'folder'])
                    for i in self._notformat_list:
                        f_csv.writerow([self._appname, i, self._dir])
            else:
                with open(filepath, 'a', newline='') as f:
                    f_csv = csv.writer(f)
                    for i in self._notformat_list:
                        f_csv.writerow([self._appname, i, self._dir])


RemoteExtractorConfig = {
    "benign_url_list": [r"db/benign_url/CN.csv", r"db/benign_url/US.csv", r"db/benign_url/my_filter.txt"],
    # eh.., I find aliyun.com etc. in this list.
    #"benign_url_list": [r"db/benign_url/CN.csv", r"db/benign_url/my_filter.txt"],
}

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--task-name', required=True, help="Provide name of the task, such that we can reach the local resource.")
    args = parser.parse_args()

    target_folder = os.path.join(Config.Config["working_folder"], args.task_name)
    if not os.path.exists(target_folder):
        log.error("no such task `{}` exist".format(args.task_name))
        exit(1)

    # walk the local resource folder to get urls.
    for m in os.listdir(target_folder):                         # in the 1st round iteration, I reach the module folder
        for inst in os.listdir(os.path.join(target_folder, m)): # in the 2nd round iteration, I reach the app folder.
            working_inst = os.path.join(target_folder, m, inst)
            log.info("working on {}".format(working_inst))

            # start to retrieve the remote resource.
            local_res_folder = os.path.join(working_inst, Config.Config["local_res_folder"])
            remote_res_folder = os.path.join(working_inst, Config.Config["remote_res_folder"])
            # clean
            shutil.rmtree(remote_res_folder, ignore_errors=True)

            r = Web_resource(local_res_folder)

            # I would like to preserve all urls firstly, such that we can do statistic to find the dominate urls and supplement the `my_filter.txt` file.
            logging_file = os.path.join(
                remote_res_folder,
                Config.Config["remote_res_info"],
            )
            r.dump(logging_file)

            # then remove top urls
            for f in RemoteExtractorConfig["benign_url_list"]:
                r.del_top(os.path.join(os.path.dirname(os.path.realpath(__file__)), f))
            logging_file = os.path.join(
                remote_res_folder,
                Config.Config["filtered_remote_res_info"],
            )
            r.dump(logging_file)

            # retrieve the first web resource
            web_resource_folder = os.path.join(remote_res_folder, str(datetime.date.today()))
            os.makedirs(web_resource_folder, exist_ok=True)

            for u in r.purified_url:
                log.info("processing: {}".format(u))
                downloader = WebUtil(u)
                downloader.scarpy_web(web_resource_folder)

                # log sth.