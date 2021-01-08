#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 19:14:18 2020

@author: hypo
"""

import os
import json
import time
import re
import requests
import logging
import sys
import urllib
import shutil
import ssl

from hashlib import md5
from Wappalyzer import Wappalyzer, WebPage
from urllib.parse import urlparse

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

# To remove error.
# urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1123)>
ssl._create_default_https_context = ssl._create_unverified_context


class HTMLUtil:
    def __init__(self, url):
        self._url = url

    @property
    def alive(self):
        """
        test if the url is alive
        """
        try:
            response = urllib.request.urlopen(self._url, timeout=3)
        except IOError:
            return False
        except ssl.CertificateError:
            return False
        else:
            code = response.getcode()
            if code != 200:
                return False
            else:
                return True

class WebResourceDownloader:
    '''
    Download do download stuff, other thing should be excluded
    '''
    def __init__(self, url, storage_path, log_file):
        self._url = url
        self._storage_path = os.path.join(storage_path, md5(url.encode('utf-8')).hexdigest())
        self._config_file = os.path.join(self._storage_path, log_file)

    def _wappalyzer_check(self):
        if not self._url.startswith('http'):
            url = "http://" + self._url
        else:
            url = self._url
        try:
            wappalyzer = Wappalyzer.latest()
            webpage = WebPage.new_from_url(url, verify=False)
            return list(wappalyzer.analyze(webpage))
        except:
            return []

    def _get_ip_info(self):
        """
        域名的IP，地理位置
        @ return ip, domain, math_location, location
        """
        gheaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}
        domain = urlparse(self._url).netloc
        url = "https://ip.tool.chinaz.com/" + domain
        r = requests.get(url, headers=gheaders)
        if r.status_code != 200:
            return None, None, None, None
        r.encoding = r.apparent_encoding

        # t1[0]: ip
        # t2[0]: 域名
        # t3[1]: 数字地址
        # t3[0]: 物理地址

        t1 = re.findall('onclick=\"AiWenIpData\(\'(.*?)\'\)\">', r.text)
        t2 = re.findall('<span class=\"Whwtdhalf w15-0 lh45\">(.*?)<\/span>', r.text)
        t3 = re.findall('<span class=\"Whwtdhalf w30-0 lh24 tl ml80\">\s+<p>(.*?)<\/p>', r.text)

        if len(t2[0]) < 2:
            return t1[0], t2[0], None, t3[0]
        else:
            return t1[0], t2[0], t2[1], t3[0]

    def scarpy_web(self, appname, path):
        if not self.alive:
            return False
        newpath = os.path.join(path, appname)
        if not os.path.isdir(newpath):
            os.makedirs(newpath)

        content = self.get_content
        if content == None:
            return False

        "save the main html"
        if self.getname.endswith('.html'):
            self.download_file(self.getname, newpath)
        else:
            try:
                super_urlretrieve(
                    self.getname,
                    os.path.join(newpath, self.getname.split('/')[-1] + ".html")
                )
                # '{}{}.{}'.format(newpath+'\\',self.getname.split('/')[-1],'html'))
            except:
                pass

        "save css file"
        result = self.css_list
        _ = self.list_download(result, newpath)
        with open(os.path.join(newpath, 'css.txt'), 'w+') as f:
            for line in result:
                f.write(line + '\n')

        lists = self.js_list
        _ = self.list_download(lists, newpath)
        with open(os.path.join(newpath, 'js.txt'), 'w+') as f:
            for line in lists:
                f.write(line + '\n')

        pic_list = self.img_list
        _ = self.list_download(pic_list, newpath)
        with open(os.path.join(newpath, 'img.txt'), 'w+') as f:
            for line in pic_list:
                f.write(line + '\n')

        return True


    def doDownload(self):
        shutil.rmtree(self._storage_path, ignore_errors=True)
        os.makedirs(self._storage_path, exist_ok=True)

        ip, domain, math_location, location = self._get_ip_info()
        log_data = {
            "URL": self._url,
            "IP": ip,
            "State": "unknown",
            "Alive_days": 0,
            "HTML_change_date": [],
            "CSS_change_date": [],
            "Js_change_date": [],
            "Img_change_date": [],
            "Math_place": math_location,
            "Physical_place": location,
            "Server_type": self._wappalyzer_check(),
            "Monitor_begin": time.asctime(),
            "Monitor_end": "unknown",
            "Super_change": []
        }

        h = HTMLUtil(self._url)
        if h.alive == False:
            log_data["State"] = "dead"
            log_data["Monitor_end"] = time.asctime()
            with open(self._config_file, 'w+') as f:
                json.dump(log_data, f)
            log.info("can not access {}".format(self._url))
            return

        if h.scarpy_web(md5(url.encode('utf-8')).hexdigest(), os.path.join(storage_path, appname)):
            data["State"] = "alive"
            data["Alive_days"] = 1
            data["HTML_change_date"].append(time.asctime())
            data["CSS_change_date"].append(time.asctime())
            data["Js_change_date"].append(time.asctime())
            data["Img_change_date"].append(time.asctime())
            with open(record_json, 'w+') as f:
                json.dump(data, f)
            print("------{} download done".format(url))

        '''

def WebMonitor(url, storage_path, appname="foo"):


    # 初次创建
    if not os.path.exists(pwd):
        os.makedirs(pwd,)
        record_json = os.path.join(pwd, "record.json")
        info = Domain_get_IP(url)
        # print("domain check"+ str(time.time()-begin))
        init_data = {
        }
        with open(record_json, 'w+') as f:
            json.dump(init_data, f)

    # 网页存活检测
    record_json = os.path.join(pwd, "record.json")
    with open(record_json, 'r') as f:
        data = json.load(f)


    else:
        # 发现网页仍然存活
        # 但并未拉下资源时
        if data["State"] == "unknown":
        else:
            # 发现网页仍然存活
            # 已经拉取过以前的资源了
            change_flag = False
            data["Alive_days"] += 1
            # 先判断有没有变化js
            with open(os.path.join(pwd, "js.txt")) as f:
                oldjs = f.read().splitlines()
            newjs = h.js_list
            oldjs.sort()
            newjs.sort()
            if oldjs != newjs:
                change_flag = True
                addjs = [i for i in newjs if i not in oldjs]
                h.list_download(addjs, pwd)
                with open(os.path.join(pwd, "js.txt"), 'a+') as f:
                    for line in addjs:
                        f.write(line + '\n')
                data["Js_change_date"].append(time.asctime())

            with open(os.path.join(pwd, "css.txt")) as f:
                oldcss = f.read().splitlines()
            newcss = h.css_list
            oldcss.sort()
            newcss.sort()
            if oldcss != newcss:
                change_flag = True
                addcss = [i for i in newcss if i not in oldcss]
                h.list_download(addcss, pwd)
                with open(os.path.join(pwd, 'css.txt'), 'a+') as f:
                    for line in addcss:
                        f.write(line + '\n')
                data["CSS_change_date"].append(time.asctime())

            with open(os.path.join(pwd, "img.txt")) as f:
                oldimg = f.read().splitlines()
            newimg = h.img_list
            oldimg.sort()
            newimg.sort()
            if oldimg != newimg:
                change_flag = True
                addimg = [i for i in newimg if i not in oldimg]
                h.list_download(addimg, pwd)
                with open(os.path.join(pwd, 'img.txt'), 'a+') as f:
                    for line in addimg:
                        f.write(line + '\n')
                data["Img_change_date"].append(time.asctime())
            # 若是html结构变化巨大，记录
            if change_flag:
            # if True:
                for file in os.listdir(pwd):
                    if file.endswith('.html'):
                        content = open(os.path.join(pwd, file), 'r', encoding='utf-8').read()
                        if content == None:
                            break
                        if h.file_similarity(content) > 0.2:
                            data["Super_change"].append(time.asctime())

            with open(record_json, 'w+') as f:
                json.dump(data, f)
            print("-------check {} done".format(url))
        return True

'''

if __name__ == "__main__":
    downloader = WebResourceDownloader("https://wzpa2.lanchengzxl.com", "test", "log.json")
    downloader.doDownload()
