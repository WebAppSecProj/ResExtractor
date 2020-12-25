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
from monitor.Url_base import HTML
from Wappalyzer import Wappalyzer,WebPage

def check_domain(ip):
    """
    检查输入的域名格式
    http://wuyu.fxtmets3.cc/wap/main.html改为wuyu.fxtmets3.cc
    """
    if('http' in ip):
        ip = re.findall('https?:\/\/(.*?)\/', ip)[0]
    return ip

def getPage(ip, web):
    qheaders = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"}
    ip = check_domain(ip)
    url = web+ip
    r = requests.get(url, headers=qheaders)
    r.encoding = r.apparent_encoding
    return r.text

def Domain_get_IP(ip):
    """
    域名的IP，地理位置
    """
    dicts = {}
    dicts['IP'] = "unknow"
    dicts['domain'] = "unknow"
    dicts['math_location'] = "unknow"
    dicts['location'] = "unknow"
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
        print("Check domain Error",e)
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

def WebMonitor(url,storage_path,appname):
    pwd = os.path.join(storage_path,appname)
    #初次创建
    if not os.path.exists(pwd):
        os.mkdir(pwd)
        record_json = os.path.join(pwd,"record.json")
        begin = time.time()
        info = Domain_get_IP(url)
        print("domain check"+ str(time.time()-begin))
        init_data = {
            "URL":url,
            "IP":info["IP"],
            "State":"unknow",
            "Alive_days":0,
            "HTML_change_date":[],
            "CSS_change_date":[],
            "Js_change_date":[],
            "Img_change_date":[],
            "Math_place":info["math_location"],
            "Phsical_place":info["location"],
            "Server_type":WappalyzerCheck(url),
            "Monitor_begin":time.asctime(),
            "Monitor_end":"unknow",
            "Super_change":[]
            }
        with open(record_json,'w+') as f:
            json.dump(init_data,f)
            f.close()
    
    #非初次创建的数据更新
    #网页存活检测
    record_json = os.path.join(pwd,"record.json")
    f=open(record_json,'r')
    data = json.load(f)
    f.close()
    h=HTML(url)
    if h.alive == False:
        data["State"]="dead"
        data["Monitor_end"]=time.asctime()
        with open(record_json,'w+') as f:
            json.dump(data,f)
            f.close()
        return
    else:
        #发现网页仍然存活
        #但并未拉下资源时
        if data["State"]=="unknow":
            if h.scarpy_web(appname,storage_path):
                data["State"]="alive"
                data["Alive_days"]=1
                data["HTML_change_date"].append(time.asctime())
                data["CSS_change_date"].append(time.asctime())
                data["Js_change_date"].append(time.asctime())
                data["Img_change_date"].append(time.asctime())
                with open(record_json,'w+') as f:
                    json.dump(data,f)
                    f.close()
        else:   
            #发现网页仍然存活
            #已经拉取过以前的资源了
            data["Alive_days"]+=1
            #先判断有没有变化js
            a = time.time()
            oldjs = open(pwd+"\\js.txt").read().splitlines()   
            newjs = h.js_list
            oldjs.sort()
            newjs.sort()
            if oldjs!=newjs:
                addjs = [ i for i in newjs if i not in oldjs ]
                h.list_download(addjs,pwd)
                with open(pwd+'\\js.txt','a+') as f:
                    for line in addjs:
                        f.write(line+'\n')
                    f.close()
                data["Js_change_date"].append(time.asctime())
            oldcss = open(pwd+"\\css.txt").read().splitlines()
            newcss = h.css_list
            oldcss.sort()
            newcss.sort()
            if oldcss!=newcss:
                addcss = [ i for i in newcss if i not in oldcss ]
                h.list_download(addcss,pwd)
                with open(pwd+'\\css.txt','a+') as f:
                    for line in addcss:
                        f.write(line+'\n')
                    f.close()
                data["CSS_change_date"].append(time.asctime())
            oldimg = open(pwd+"\\img.txt").read().splitlines()
            newimg = h.img_list
            oldimg.sort()
            newimg.sort() 
            if oldimg!=newimg:
                addimg = [ i for i in newimg if i not in oldimg ]
                h.list_download(addimg,pwd)
                with open(pwd+'\\img.txt','a+') as f:
                    for line in addimg:
                        f.write(line+'\n')
                    f.close()
                data["Img_change_date"].append(time.asctime())
            #若是html结构变化巨大，记录
            for file in os.listdir(pwd):
                if file.endswith('.html'):
                    content = open(pwd+"\\"+file,'r',encoding='utf-8').read()
                    print(time.time()-a)
                    if content==None:
                        break
                    if h.file_similarity(content)>0.2:
                        data["Super_change"].append(time.asctime())
            
            with open(record_json,'w+') as f:
                json.dump(data,f)
                f.close()
                
                
if __name__ == "__main__":
    begin = time.time()
    WebMonitor(r"https://blog.csdn.net/qq_40965177/article/details/88086592",
               r'/home/demo/Desktop/WebAppSec/ResExtractor/',
               r"baidu")
    end = time.time()
    print(end-begin)
                
                
                
                
                