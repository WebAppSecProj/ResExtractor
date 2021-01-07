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
from hashlib import md5
from Wappalyzer import Wappalyzer, WebPage
from Applications.Monitor.Url_base import HTML
from Applications.Monitor.MonitorConfig import MonitorConfig
import shutil


def run(self, monitor="all"):
    if monitor == "all":
        for monitor in self._monitor.copy():
            if not os.path.exists(monitor):
                continue
            try:
                with open(monitor, 'r') as csvfile:
                    new_dict = []
                    for row in csv.DictReader(csvfile):
                        if WebMonitor(row['URL'],
                                      row['folder'],
                                      row['appname']):
                            new_dict.append(row)
                with open(monitor, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['appname', 'URL', 'folder'])
                    writer.writerows([i["appname"], i["URL"], i["folder"]] for i in new_dict)
                # 检查完删除monitor列表
                self._monitor.remove(monitor)
            except Exception as e:
                print("Monitor {} Error".format(e))
    else:
        if not os.path.exists(monitor):
            return
        try:
            with open(monitor, 'r') as csvfile:
                new_dict = []
                for row in csv.DictReader(csvfile):
                    if WebMonitor(row['URL'],
                                  row['folder'],
                                  row['appname']):
                        new_dict.append(row)
            with open(monitor, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['appname', 'URL', 'folder'])
                writer.writerows([i["appname"], i["URL"], i["folder"]] for i in new_dict)
            # 检查完删除monitor列表
            self.monitor.remove(monitor)
        except Exception as e:
            print("Monitor {} Error".format(e))

