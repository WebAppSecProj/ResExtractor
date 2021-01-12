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
from hashlib import md5
from Wappalyzer import Wappalyzer, WebPage
from libs.WebUtil import HTML
import Config

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

def check_domain(ip):
    """
    检查输入的域名格式
    http://wuyu.fxtmets3.cc/wap/main.html改为wuyu.fxtmets3.cc
    """
    if ('http' in ip):
        try:
            if ip.count('/') >= 3:
                ip = re.findall('https?:\/\/(.*?)\/', ip)[0]
            else:
                ip = re.findall('https?:\/\/(.*?)', ip)[0]
        except:
            return ip
        return ip
    else:
        try:
            if ip.count('/') >= 1:
                ip = re.findall('https?:\/\/(.*?)\/', ip)[0]
            else:
                ip = re.findall('https?:\/\/(.*?)', ip)[0]
        except:
            return ip
        return ip


def getPage(ip, web):
    qheaders = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}
    ip = check_domain(ip)
    url = web + ip
    r = requests.get(url, headers=qheaders)
    r.encoding = r.apparent_encoding
    return r.text

def Domain_get_IP(ip):
    """
    域名的IP，地理位置
    """
    dicts = {}
    dicts['IP'] = "unknown"
    dicts['domain'] = "unknown"
    dicts['math_location'] = "unknown"
    dicts['location'] = "unknown"
    text = getPage(ip, "https://ip.tool.chinaz.com/")
    domain = re.findall('<span class=\"Whwtdhalf w15-0\">(.*?)<\/span>', text)
    ips = re.findall('onclick=\"AiWenIpData\(\'(.*?)\'\)\">', text)
    result = re.findall('<span class=\"Whwtdhalf w50-0\">(.*?)<\/span>', text)
    try:
        dicts['IP'] = ips[0]
        dicts['domain'] = domain[3]
        dicts['math_location'] = domain[4]
        dicts['location'] = result[1]
    except Exception as e:
        print("Check domain Error", e)
    return dicts


def WappalyzerCheck(url):
    if not url.startswith('http'):
        url = "http://" + url
    try:
        wappalyzer = Wappalyzer.latest()
        webpage = WebPage.new_from_url(url)
        return list(wappalyzer.analyze(webpage))
    except:
        return []


def WebMonitor(url, storage_path, appname="foo"):

    h = HTML(url)
    pwd = os.path.join(storage_path, appname, md5(url.encode('utf-8')).hexdigest())
    # if force == True and os.path.exists(pwd):
    #     shutil.rmtree(pwd)

    # 初次创建
    if not os.path.exists(pwd):
        os.makedirs(pwd, exist_ok=True)
        record_json = os.path.join(pwd, "record.json")
        info = Domain_get_IP(url)
        # print("domain check"+ str(time.time()-begin))
        init_data = {
            "URL": url,
            "IP": info["IP"],
            "State": "unknown",
            "Alive_days": 0,
            "HTML_change_date": [],
            "CSS_change_date": [],
            "Js_change_date": [],
            "Img_change_date": [],
            "Math_place": info["math_location"],
            "Physical_place": info["location"],
            "Server_type": WappalyzerCheck(url),
            "Monitor_begin": time.asctime(),
            "Monitor_end": "unknown",
            "Super_change": []
        }
        with open(record_json, 'w+') as f:
            json.dump(init_data, f)

    # 网页存活检测
    record_json = os.path.join(pwd, "record.json")
    with open(record_json, 'r') as f:
        data = json.load(f)

    if h.alive == False:
        data["State"] = "dead"
        data["Monitor_end"] = time.asctime()
        with open(record_json, 'w+') as f:
            json.dump(data, f)
        print("------{} is already closed".format(url))
        return False
    else:
        # 发现网页仍然存活
        # 但并未拉下资源时
        if data["State"] == "unknown":
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


# I would like to config the task names rather than get them from the command line
MonitorConfig ={
    "tasks": [
        "xingyuan.2020.01.05",
    ],
}

if __name__ == "__main__":

    # working directory should be set to the root directory
    '''
    for task in MonitorConfig["task_folder"]:       # for each task
        for m in os.listdir(task):                  # for each module
            for inst in os.listdir(m):              # for each app
                remote_res_folder = os.path.join(Config.Config["working_folder"], task, m, inst, Config.Config["remote_res_folder"])
                if not os.path.exists(remote_res_folder, Config.Config["remote_res_info"]):
                    log.warning("incomplete instance: {}".format(inst))
                    continue
    '''

    begin = time.time()
    WebMonitor(r"https://blog.csdn.net/qq_40965177/article/details/88086592",
               MonitorConfig["monitor_folder"],
               r"baidu")     # hash of the app, such that I can find the related apps.
    end = time.time()
    print(end - begin)
