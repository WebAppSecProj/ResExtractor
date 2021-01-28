#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/1/27 14:52
# @Author  : fy
# @FileName: yimen.py

import base64
import json
from hashlib import md5
from Crypto.Cipher import AES
import requests
import logging
import shutil
import sys
import os
from libs.modules.BaseModule import BaseModule

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: https://www.yimenapp.net/
'''


class yimen(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.lt.app")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False

    def doExtract(self, working_folder):
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        tmp_folder = os.path.join(extract_folder, "tmp")
        self._apktool(tmp_folder)

        resource_path = os.path.join(tmp_folder, "assets/")
        shutil.copytree(resource_path, extract_folder, dirs_exist_ok=True)
        manifest = os.path.join(tmp_folder, "AndroidManifest.xml")
        root = ET.parse(manifest).getroot()
        pkgName = root.get("package")

        launch_path = "default: assets/www/index.html"  # default local url
        # 通过请求可以获得对应包名的配置信息，再进行解密，获得加载的url
        # __v : 含义未知，编辑在代码中，不影响结果
        # __k : PackageName，应用包名
        #   v : versionCode，不影响结果
        # key : 解密密钥。从代码中提取，当前固定值为"VHf9krzin6mfknctnhJ3zQ``"
        __v = 44
        __k = pkgName
        v = 100
        key = "VHf9krzin6mfknctnhJ3zQ``"

        ym = yimenDecode(__k, key)
        param = "__v=%d&__k=%s&v=%d" % (__v, __k, v)
        url = "https://g.yimenseo.cn/ga/?" + param
        data = {"q": ym.get_q(param), "d": ym.get_d()}
        r = requests.post(url, data)
        res_str = str(ym.decode_response(r.content), "utf8")
        res_json = json.loads(res_str[0:res_str.rindex("}") + 1])
        print(res_json)
        if "url" in res_json:
            appurl = res_json["url"]
            launch_path = appurl
        else:
            msg = res_json["msg"]
            log.info("get apk url error. msg from yimen server: {}".format(msg))
        if launch_path.startswith("local:"):
            local_url = os.path.join(resource_path, launch_path[6:])
            if os.path.exists(local_url) is not True:
                yx_file = open(os.path.join(tmp_folder, "assets/y.x"), "rb")
                yx_str = str(ym.decode_response(yx_file.read()), "utf8")
                yx_json = json.loads(yx_str[0:yx_str.rindex("}") + 1])
                if "url" in yx_json:
                    appurl = yx_json["url"]
                    launch_path = appurl
                else:
                    msg = yx_json["msg"]
                    log.info("get apk url error. yimen local-config msg: {}".format(msg))

        self._dump_info(extract_folder, launch_path)

        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


class yimenDecode:
    def __init__(self, pkgName, key):
        self.pkgName = pkgName
        self.key = key
        self.android_id = "1e085ba17f5d55ee60437a390f523376"

    def get_q(self, str1):
        # 传入的参数需要从代码中读取各个值
        bytes1 = bytes(str1, encoding="utf-8")
        v0 = ""
        for bb in bytes1:
            v4 = '%02x' % ((bb ^ -1) & 0xFF)
            v0 = v0 + v4
        return str(v0)

    def get_d(self):
        # get android_id
        # 当前返回测试机的android_id,应该是可随意更换
        return self.android_id

    def bytes_digest(self, str_in):
        str_in = md5(bytes(str_in, "utf-8")).hexdigest()
        return str_in

    def decode_response(self, res_bytes):
        key = self.bytes_digest(self.bytes_digest(self.pkgName)).encode('utf-8')
        iv = base64.b64decode(self.key.replace('`', '='))
        ci = AES.new(key, AES.MODE_CBC, iv)
        return ci.decrypt(res_bytes)


def main():
    f = "./test_case/yimen/x249050-adr-v100-wv0.apk"  # 未更新应用。服务器端更新了url，更新url为本地url
    # f = "./test_case/yimen/localsrc_x249050-adr-v103-vi2.apk" # 更新后的应用。服务器端更新了url，更新url为本地url
    f = "./test_case/yimen/ceec9d08e7593a8b7050a2c7958528f6e4bfa52e769cd432bfdc03c893f39269.apk"
    f = "./test_case/yimen/壳8fdbd4d7c81ec098e8729cea5853185436bdad009c750b7d3f5240bba7880d87.apk"  # 带壳应用
    ym = yimen(f, "android")
    if ym.doSigCheck():
        logging.info("yimen signature Match")
        extract_folder, launch_path = ym.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))
    return


if __name__ == '__main__':
    main()
