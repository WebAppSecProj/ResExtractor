# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 11:30:59 2020

@author: hypo
"""

import os,csv,time,sys,logging

from Applications.Monitor.Url_base import HTML
from Applications.Monitor.Web_source import Web_source
from Applications.Monitor.Monitor import WebMonitor

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)


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
        self.iter = self._get_iter()

    def _get_iter(self):
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
        self._monitor = [filePath]  # logging file
        self._pwd = []              # resource folder
        self._label = []            # task name, app name, or sth else
        self._filter =[]            # url filter
        
    def _add_monitorfile(self, filePath):
        self._monitor.append(filePath)
    
    def add_filter(self, filters):
        self._filter.append(filters)

    def add_websource(self, inp: InputBase, label):
        self._pwd.append(inp)
        self._label.append(label)
        
    def parser(self, dst_file):
        if dst_file == None:
            dst_file = self._monitor[0]
        for i in range(0, len(self._pwd)):
            inp = self._pwd[i]
            label = self._label[i]
            for folder in inp:
                log.info("processing folder: {}".format(folder))
                a = Web_source(folder, label)
                for i in self._filter:
                    a.del_top(i)

                a.dump(dst_file)
                log.info("{}".format(a.allurl))

    def run(self, monitor = "all"):
        if monitor == "all":
            for monitor in self._monitor.copy():
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
                    self._monitor.remove(monitor)
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
    # working directory should be set to current folder.
    r = Runner(os.path.join(os.path.dirname(os.path.realpath(__file__)), "url.cvs"))
    r.add_websource(DirInput(sys.argv[1]), "test")
    # eh.., I find aliyun.com etc. in this list.
    r.add_filter(os.path.join(os.path.dirname(os.path.realpath(__file__)), r'CN.csv'))
    r.add_filter(os.path.join(os.path.dirname(os.path.realpath(__file__)), r'my_filter.txt'))
    r.parser(os.path.join(os.path.dirname(os.path.realpath(__file__)), r'url2.csv'))
    r.run()
    #a.add_monitorfile(r'C:\Users\hypo\Desktop\黑灰产paper\monitor\url2.csv')
    #a.run()
    print(time.time()-begin)