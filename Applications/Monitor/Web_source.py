#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 19:17:30 2020

@author: Hypo
"""
import os, sys, re, csv, time
#from Url_base import HTML
#from Monitor import WebMonitor

class Web_source():
    def __init__(self, dirpath, appname):
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
        #非文本后缀
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
                    column = [row['web'] for row in reader]
                    for i in column:
                        for j in self.allurl.copy():
                            if i in j:
                                self.allurl.remove(j)
            except:
                pass
        if topfile.endswith(".txt"):
            try:
                with open(topfile, 'r') as txt:
                    column = txt.read().splitlines()
                    for i in column:
                        for j in self.allurl.copy():
                            if i in j:
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
                
def test():
    begin = time.time()
    a=Web_source(r'G:\涉案APK\盘古\working_folder\working_folder\5ae6ee34631adfd2f35fa7e7994e9b91949f3d4f','test3')
    a.del_top(r'G:\涉案APK\CN.csv')
    a.del_top(r'C:\Users\hypo\Desktop\黑灰产paper\monitor\my_filter.txt')
    b, c = a.remote_url
    print(len(c))
    #print(c)
    #print(a.allurl)
    print(len(a.allurl))
    a.dump(r'C:\Users\hypo\Desktop\黑灰产paper\monitor\url.csv')
    print(time.time()-begin)
    
if __name__== "__main__":
    sys.exit(test())