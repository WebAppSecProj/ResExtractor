#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2021/1/27 14:52
# @Author  : fy
# @FileName: yimen.py

import base64
import hashlib
import json
import biplist
from hashlib import md5
from Crypto.Cipher import AES
import plistlib
from Crypto.Cipher import DES
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
            Yimen_Engine_path = os.path.join("Frameworks","YMPlugin.framework")
            #print(Yimen_Engine_path)
            return self._check_file_exists(Yimen_Engine_path,True)
            #return False
        return False

    def doExtract(self,working_folder):
        if self.host_os == "android":
            return self.doExtractAndroid(working_folder)
        elif self.host_os == "ios":
            return self.doExtractiOS(working_folder)
    
    def decrypt_ios_config(self, content, enc_key):
        iv = [0x54,0x77,0xfd,0x92,0xbc,0xe2,0x9f,0xa9]
        ci = DES.new(enc_key.encode('utf-8'),DES.MODE_CBC,bytes(iv))
        return ci.decrypt(content)


    def request_ios_config_from_host(self, bundle_id, enc_key):
        __v = 43
        __k = bundle_id
        param = "__k=%s&__v=%d" % ( __k, __v)
        url = "https://g.yimenseo.net/gi/?" + param
        r = requests.post(url)
        #print(url)
        res_str = str(self.decrypt_ios_config(r.content,enc_key), "utf-8")
        res_json = json.loads(res_str[0:res_str.rindex("}") + 1])
        return res_json


    def scan_local_res_from_json(self, tar_json):
        path_list = set()
        for tmp_key in tar_json:
            tmp_value = tar_json[tmp_key]
            if isinstance(tmp_value,str):
                if "local:" in tmp_value:
                    tmp_path = tmp_value.replace("local:","")
                    sub_dir = os.path.dirname(tmp_path)
                    path_list.add(sub_dir)
            if isinstance(tmp_value,dict):
                path_list.update(self.scan_local_res_from_json(tmp_value))
        return path_list



    def doExtractiOS(self,working_folder):
        launch_path = None
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        tmp_folder = os.path.join(extract_folder, "tmp")

        self._ipa_extract(tmp_folder)

        ipa_root_path = os.path.join(tmp_folder,self._ipa_app_path())
        config_z_path = os.path.join(ipa_root_path,"config.z")
        #root_config_path = os.path.join(ipa_root_path,"config")
        plist_lib_path = os.path.join(ipa_root_path,"Info.plist")

        # get bundle identifier and its key
        
        bundle_id = biplist.readPlist(plist_lib_path)["CFBundleIdentifier"]
        tmp_md5 = hashlib.md5()
        tmp_md5.update(bundle_id.encode("utf-8"))
        tmp_md5_1 = tmp_md5.hexdigest()

        tmp_md5 = hashlib.md5()
        tmp_md5.update(tmp_md5_1.encode("utf-8"))
        enc_key = tmp_md5.hexdigest()[12:20]
        
        init_url = json.load(open(config_z_path))["url"]
        #print(init_url)
        
        res_json = self.request_ios_config_from_host(bundle_id,enc_key)
        #print(res_json)
        if init_url == "":
            #print(res_json["url"])
            if res_json["url"] != None:
                init_url = res_json["url"]
        
        
        local_res_path_list = self.scan_local_res_from_json(res_json)
        for tmp_path in local_res_path_list:
            if tmp_path.startswith("/"):
                tmp_path = tmp_path[1:]
            if tmp_path == "" : 
                continue
            src_path = os.path.join(ipa_root_path,tmp_path)
            tar_path = os.path.join(extract_folder,tmp_path)
            shutil.copytree(src_path,tar_path,dirs_exist_ok=True)
        
        if init_url != None:
            launch_path = init_url
        else:
            launch_path = "None"
        #print(launch_path)
        self._dump_info(extract_folder, launch_path)

        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path
            

    def doExtractAndroid(self, working_folder):
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
        #print(res_json)
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
