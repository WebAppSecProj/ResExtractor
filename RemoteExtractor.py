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
        # https://gist.github.com/gruber/8891611
        # self._HTTP_REGEX = r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"
        self._HTTP_REGEX = 'https?://[a-zA-Z0-9\.\/_&=@$%?~#-]+'
        self._IP_REGEX = '(((1[0-9][0-9]\.)|(2[0-4][0-9]\.)|(25[0-5]\.)|([1-9][0-9]\.)|([0-9]\.)){3}((1[0-9][0-9])|(2[0-4][0-9])|(25[0-5])|([1-9][0-9])|([0-9])))'
        # 非文本后缀
        self._notfile = ["jpg", "png", "gif", "bmp", "webp", "jepg", "tgz"]
        self._formats = ["jpg", "png", "gif", "bmp", "webp", "jepg", "tgz", "txt", "js", "css"]

        self._topHostPostfix = [
            '.com', '.la', '.io', '.co', '.info', '.net', '.org', '.me', '.mobi',
            '.us', '.biz', '.xxx', '.ca', '.co.jp', '.com.cn', '.net.cn',
            '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag',
            '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br',
            '.bz', '.com.bz', '.net.bz', '.cc', '.com.co', '.net.co',
            '.nom.co', '.de', '.es', '.com.es', '.nom.es', '.org.es',
            '.eu', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in',
            '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms',
            '.com.mx', '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz',
            '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw',
            '.hk', '.co.uk', '.me.uk', '.org.uk', '.vg', ".com.hk",
            '.edu.cn', '.ly', '.live', '.xyz', 'site', 'cn']

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
                                l = re.findall(self._HTTP_REGEX, fs.read())
                                '''
                                for ll in l.copy():
                                    # if ll.find("quilljs.com") != -1:
                                    #     log.info("e")
                                    if not any(urlparse(ll).netloc.endswith(t) for t in self._topHostPostfix):
                                        log.info("invalid postfix: {}".format(ll))
                                        l.remove(ll)
                                '''
                                self._url_list.extend(l)
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
        if not os.path.isdir(os.path.join(target_folder, m)):
            continue
        for inst in os.listdir(os.path.join(target_folder, m)): # in the 2nd round iteration, I reach the app folder.
            working_inst = os.path.join(target_folder, m, inst)
            if not os.path.isdir(working_inst):
                continue
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