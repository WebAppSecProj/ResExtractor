# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 11:30:59 2020

@author: hypo
"""

import os,sys,csv,time
from Url_base import HTML
from Web_source import Web_source
from Monitor import WebMonitor

class InputBase:
    """
    InputBase class.
    InputBase is an iterator-based class, you first overwrite __iter__ for some context data (like current index of iterator).
    Then, __next__ is called when Runner requests data.
    """
    def __iter__(self):
        """
        Default implementation is to return self.
        """
        return self

    def __next__(self):
        raise NotImplementedError(
            "Subclass of InputBase should implement __next__ method.")
        
class DirInput(InputBase):
    """
    An example of InputBase implementation to list First level subdirectory for input folder.
    Can also serve as a base class for Input that filters a directory. 
    """
    def __init__(self, folder: str):
        self.folder = folder
        self.iter = self.get_iter()

    def get_iter(self):
        """
        The main entry is get_iter that returns an iterator of First level subdirectory.
        """
        return iter(
            os.path.join(self.folder, a) for a in os.listdir(self.folder)
            if os.path.isdir(os.path.join(self.folder, a)))

    def __next__(self):
        file_name = next(self.iter)
        return file_name

class Runner():
    def __init__(self, filePath):
        self.monitor = [filePath]
        self.pwd = []
        self.label = []
        self.filter =[]
        
    def add_monitorfile(self,filePath):
        self.monitor.append(filePath)
    
    def add_filter(self,filters):
        self.filter.append(filters)
        
        
    def add_websource(self,inp:InputBase,label):
        self.pwd.append(inp)
        self.label.append(label)
        
    def parser(self,dst_file=self.monitor[0]):
        for i in range(0,len(self.pwd)):
            inp = self.pwd[i]
            label = self.label[i]
            for folder in inp:
                print(folder)
                a = Web_source(folder,label)
                for i in self.filter:
                    a.del_top(i)
                a.dump(dst_file)

        
    def run(self,monitor = "all"):
        if monitor == "all":
            for monitor in self.monitor.copy():
                if not os.path.exists(monitor):
                    continue
                try:
                    with open(monitor,'r') as csvfile:
                        new_dict=[]
                        for row in csv.DictReader(csvfile):
                            if WebMonitor(row['URL'],
                                              row['folder'],
                                              row['appname']):
                                new_dict.append(row)
                    with open(monitor,'w',newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['appname','URL','folder'])
                        writer.writerows([i["appname"],i["URL"],i["folder"]]for i in new_dict)
                    #检查完删除monitor列表
                    self.monitor.remove(monitor)
                except Exception as e:
                    print("Monitor {} Error".format(e))
        else:
            if not os.path.exists(monitor):
                return
            try:
                with open(monitor,'r') as csvfile:
                    new_dict=[]
                    for row in csv.DictReader(csvfile):
                        if WebMonitor(row['URL'],
                                          row['folder'],
                                          row['appname']):
                            new_dict.append(row)
                with open(monitor,'w',newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['appname','URL','folder'])
                    writer.writerows([i["appname"],i["URL"],i["folder"]]for i in new_dict)
                #检查完删除monitor列表
                self.monitor.remove(monitor)
            except Exception as e:
                print("Monitor {} Error".format(e))
    
if __name__ == "__main__":
    begin=time.time()
    a = Runner(r'C:\Users\hypo\Desktop\黑灰产paper\monitor\url.csv')
    a.add_websource(DirInput(r'G:\涉案APK\盘古\working_folder\working_folder'),"test")
    a.add_filter(r'CN.csv')
    a.add_filter(r'my_filter.txt')
    a.parser(r'C:\Users\hypo\Desktop\黑灰产paper\monitor\url2.csv')
    a.run()
    #a.add_monitorfile(r'C:\Users\hypo\Desktop\黑灰产paper\monitor\url2.csv')
    #a.run()
    print(time.time()-begin)