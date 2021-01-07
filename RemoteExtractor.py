#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 11:30:59 2020

@author: hypo
"""

import os, sys, logging, argparse, csv, re

import Config as Config

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

    def del_top(self, topfile):
        if self.allurl == None:
            return None
        if topfile.endswith(".csv"):
            try:
                with open(topfile, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    row = [row['web'] for row in reader]
                    for i in row:
                        for j in self.allurl.copy():
                            if i in j:
                                log.info("url removed: {}".format(j))
                                self.allurl.remove(j)
            except:
                pass
        if topfile.endswith(".txt"):
            try:
                with open(topfile, 'r') as txt:
                    row = txt.read().splitlines()
                    for i in row:
                        for j in self.allurl.copy():
                            if i in j:
                                log.info("url removed: {}".format(j))
                                self.allurl.remove(j)
            except:
                pass

    @property
    def remote_url(self):
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
        if self._notformat_list == None:
            self.remote_url
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

class Runner():
    def __init__(self, local_res_pwd, remote_res_pwd):
        self._local_res_pwd = local_res_pwd                 # local res path
        self._remote_res_pwd = remote_res_pwd               # remote res path
        self._filter =[]                                    # url filter

    def add_filter(self, filters):
        '''
        urls of boilerplate code should be removed
        '''
        self._filter.append(filters)

    def parse(self):
        '''
        Distill urls
        '''
        r = Web_resource(self._local_res_pwd)
        for i in self._filter:
            r.del_top(i)

        logging_file = os.path.join(
            self._remote_res_pwd,
            Config.Config["remote_res_info"],
        )

        log.info("{}".format(r.allurl))
        r.dump(logging_file)

RemoteExtractorConfig = {
    "benign_url_list": [r"db/benign_url/CN.csv", r"db/benign_url/US.csv", r"db/benign_url/my_filter.txt"],
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
    for m in os.listdir(target_folder):                         # in the 1st round iteration, I get module folder
        for inst in os.listdir(os.path.join(target_folder, m)): # in the 2nd round iteration, I get the app folder.
            working_inst = os.path.join(target_folder, m, inst)
            log.info("working on {}".format(working_inst))

            # start to retrieve the remote resource.
            r = Runner(
                os.path.join(working_inst, Config.Config["local_res_folder"]),
                os.path.join(working_inst, Config.Config["remote_res_folder"])
            )
            # eh.., I find aliyun.com etc. in this list.
            for f in RemoteExtractorConfig["benign_url_list"]:
                r.add_filter(os.path.join(os.path.dirname(os.path.realpath(__file__)), f))
            r.parse()
