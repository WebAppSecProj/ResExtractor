#!/usr/bin/env python3
"""
Created on Mon FEB 2 2021

@author: beizishaozi
"""

import logging
import sys
import shutil
import jpype
import re

import Config as Config
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class Mobincube(BaseModule):
    def extracturl(self, tmp_folder):
        fp = open(os.path.join(tmp_folder, "assets/app.dat"), "rb")
        data = fp.read()
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(data))
        target =[]
        if urls:
            for url in urls:
                #第一次正则匹配之后，无法得到纯正的URL链接；通过将\\替换为空格，可以保证第二次政策匹配之后得到纯正的URL链接。即使一开始有多个链接在一起，也可以通过第二次分开
                url2 = str(url).replace("\\", " ")
                target2 = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(url2))
                target.append(" ".join(target2))
        #print(urls)
        #print(target)
        return " ".join(target)

    def deletesuffix(self, f, suff):
        idx = f.find(suff)
        if idx == -1:
            idx = len(f)
        return f[:idx]

    #通过java解码并不彻底，只解码了本地资源部分，url链接部分是通过正则匹配实现的，因为如果还是java解码比较复杂，app.dat是通过byte拼接成的文件，格式复杂，也没有统一标准。因此这里有取巧成分，也是考虑到框架改变的情况
    def getresourcefiles(self,tmp_folder):
        # 获取jvm.dll 的文件路径
        jvmPath = jpype.getDefaultJVMPath()

        # 开启jvm
        if not jpype.isJVMStarted():
            jpype.startJVM(jvmPath, '-ea',
                           '-Djava.class.path={0}'.format(Config.Config["decrypt_jar"]),
                           convertStrings=False)
        # ②、加载java类（参数是java的长类名）
        javaClass = jpype.JClass("com.ResDecode.Main")()

        # ③、调用java方法，由于我写的是静态方法，直接使用类名就可以调用方法
        resourcefiles = javaClass.DeMobincube(os.path.join(tmp_folder, "assets/app.dat"))
        fnlist=[]
        #print(str(resourcefiles).split(","))
        for f in (str(resourcefiles).split(",")):         #记录了app.dat中资源文件名字列表,去除文件后缀
            fnlist.append(self.deletesuffix(f, "."))
        #print(fnlist)
        return fnlist

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.mobimento.caponate.MainActivity")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)
        tmp_folder = os.path.join(os.getcwd(), extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok = True)
        self._apktool_no_decode_source(tmp_folder)

        fnlist = self.getresourcefiles(tmp_folder)

        for dirpath, dirnames, ifilenames in os.walk(tmp_folder):
            if dirpath.find("assets") != -1 and (dirpath.find("assets/android") == -1) and (dirpath.find("assets/config") == -1):
                for fs in ifilenames:
                    f = os.path.join(dirpath, fs)
                    matchObj = re.match(r'(.*)assets/(.*)', f, re.S)
                    newRP = matchObj.group(2)

                    newRP1 = self.deletesuffix(newRP, ".")
                    if newRP1 not in fnlist and dirpath.endswith("assets") : #如果assets目录下文件不在资源文件名字列表中，则不需要输出
                        continue

                    tf = os.path.join(extract_folder, newRP)
                    if not os.access(os.path.dirname(tf), os.R_OK):
                        os.makedirs(os.path.dirname(tf))
                    with open(tf, "wb") as fwh:  # output th
                        # ugly coding
                        fp = open(os.path.join(dirpath, fs), "rb")
                        c = fp.read()
                        fp.close()
                        fwh.write(c)
                    fwh.close()
        launch_path=self.extracturl(tmp_folder)
        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/mobincube/EKQ361.apk"    #EKULS6.apk  EKQ361.apk
    mobincube = Mobincube(f, "android")
    if mobincube.doSigCheck():
        logging.info("Mobincube signature Match")

        extract_folder, launch_path = mobincube.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
