#!/usr/bin/env python3
"""
Created on Wed Dec 28 2020

@author: beizishaozi
"""

import logging
import sys
import shutil
import re

import jpype

from Crypto.Hash import MD5
from Crypto.Cipher import DES

import Config as Config

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class AppYet(BaseModule):
    # 通过python实现使用PBEWithMD5AndDES解密，但是appyet加解密前后还有一些字节操作。decry函数不包含字节操作，因此通过jar包调用java方法。
    def decry(self, filepath):
        with open(filepath, "rb") as fh:
            plaintext_to_encrypt = fh.read()
        _password = 'X5nFe16r7FbKpb16lJGH386S4WFaqy1khWWzo7Wyv3Pr1wJlF5C28g39kNcPYt4p2s3FayL3u28KfLxUQx8c922XH9inECtciY0hgsegn443gfeg543'  # MD5
        _salt = b'\xa9\x9b\xc8\x32\x56\x35\xe3\x03'  # IvParameterSpec
        hasher = MD5.new()
        hasher.update(_password.encode('utf-8'))
        hasher.update(_salt)
        result = hasher.digest()

        for i in range(1, 19):
            hasher = MD5.new()
            hasher.update(result)
            result = hasher.digest()
        encoder = DES.new(result[:8], DES.MODE_CBC, result[8:16])
        length = len(plaintext_to_encrypt)
        print(len(plaintext_to_encrypt))
        encrypted = encoder.decrypt(plaintext_to_encrypt[:length - 2])
        print(encrypted.decode('utf-8', errors='ignore'))

    def extract_startpage(self, filepath):
        """
        基本的开发流程如下：
        ①、使用jpype开启jvm
        ②、加载java类
        ③、调用java方法
        ④、关闭jvm（不是真正意义上的关闭，卸载之前加载的类）
        """
        # ①、使用jpype开启虚拟机（在开启jvm之前要加载类路径）
        # 加载刚才打包的jar文件
        decode_jar_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "decodeappyet.jar")

        # 获取jvm.dll 的文件路径
        jvmPath = jpype.getDefaultJVMPath()

        # 开启jvm
        if not jpype.isJVMStarted():
            jpype.startJVM(jvmPath, '-ea',
                           '-Djava.class.path={0}'.format(Config.Config["decrypt_jar"]),
                           convertStrings=False)
        # ②、加载java类（参数是java的长类名）
        javaClass = jpype.JClass("com.ResDecode.Main")()

        # 实例化java对象
        # javaInstance = javaClass()

        # ③、调用java方法，由于我写的是静态方法，直接使用类名就可以调用方法
        _password = 'X5nFe16r7FbKpb16lJGH386S4WFaqy1khWWzo7Wyv3Pr1wJlF5C28g39kNcPYt4p2s3FayL3u28KfLxUQx8c922XH9inECtciY0hgsegn443gfeg543'  # MD5
        plain = javaClass.DeAppYet(filepath, _password)
        feed_url = []
        m = re.findall('FeedUrl":"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(plain))
        if m:
            for tmp in m:
                if tmp not in feed_url:
                    feed_url.append(tmp)
        feedurl = ("".join(feed_url)).replace('FeedUrl":"', ' ')
        web_url = []
        n = re.findall('"Type":"Link","Data":"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(plain))
        if n:
            for tmp in n:
                if tmp not in web_url:
                    web_url.append(tmp)
        weburl = ("".join(web_url)).replace('"Type":"Link","Data":"', ' ')
        # ④、关闭jvm
        # 执行关闭jvm后，后续其他模块执行jpype.startJVM()时，会提示 OSError: JVM cannot be restarted
        # jpype.shutdownJVM()
        return "{} {}".format(feedurl, weburl)

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.appyet.activity.MainActivity")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok=True)
        tmp_folder = os.path.join(os.getcwd(), extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok=True)
        self._apktool_no_decode_source(tmp_folder)  # 不反编译代码

        for dirpath, dirnames, ifilenames in os.walk(tmp_folder):
            if dirpath.find("assets/web") != -1 or dirpath.find(
                    "assets/media") != -1:  # 自定义页面保存在assets/web中，上传的多媒体文件保存在assets/media中
                for fs in ifilenames:
                    f = os.path.join(dirpath, fs)
                    matchObj = re.match(r'(.*)assets/(.*)', f, re.S)
                    newRP = matchObj.group(2)

                    tf = os.path.join(extract_folder, newRP)
                    if not os.access(os.path.dirname(tf), os.R_OK):
                        os.makedirs(os.path.dirname(tf))
                    with open(tf, "wb") as fwh:  # output the
                        # ugly coding
                        fp = open(os.path.join(dirpath, fs), "rb")
                        c = fp.read()
                        fp.close()
                        fwh.write(c)
                    fwh.close()
        launch_path = self.extract_startpage(os.path.join(tmp_folder, "res/raw/metadata.txt"))
        # launch_path = self.decry(os.path.join(tmp_folder, "res/raw/metadata.txt"))
        self._dump_info(extract_folder, launch_path)
        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/AppYet/example.apk"  # 后续会将当前脚本路径与之相拼接，得到最终detect_file路径
    appyet = AppYet(f, "android")
    if appyet.doSigCheck():
        logging.info("AppYet signature Match")
        extract_folder, launch_path = appyet.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == "__main__":
    sys.exit(main())
