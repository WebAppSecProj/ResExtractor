#!/usr/bin/env python3
"""
Created on Wed Dec 25 2020

@author: beizishaozi
"""
import logging
import sys
import shutil
import hashlib
import re

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Reference:
1) http://www.appcan.cn/
'''

# extracting the starting page from "res/xml/config.xml" in "<content src="index.html" />"

def isEncrypted(enfile):
    flag = False
    with open(enfile, "rb") as f:
        read_data = f.read()
        length = len(read_data)
        a = read_data[(length-17):]   #此时读取的是bytes，要将bytes转换为str，才能进行字符串比较
        if a == "3G2WIN Safe Guard".encode("UTF-8"):
            flag = True
    f.close()
    return flag

def rc4_init_sbox(key):
    # s_box = list(range(256))  # 我这里没管秘钥小于256的情况，小于256不断重复填充即可
    s_box = [0xD7,0xDF,0x02,0xD4,0xFE,0x6F,0x53,0x3C,0x25,0x6C,0x99,
                                0x97,0x06,0x56,0x8F,0xDE,0x40,0x11,0x64,0x07,0x36,0x15,0x70,0xCA,0x18,0x17,0x7D,
                                0x6A,0xDB,0x13,0x30,0x37,0x29,0x60,0xE1,0x23,0x28,0x8A,0x50,0x8C,0xAC,0x2F,0x88,
                                0x20,0x27,0x0F,0x7C,0x52,0xA2,0xAB,0xFC,0xA1,0xCC,0x21,0x14,0x1F,0xC2,0xB2,0x8B,
                                0x2C,0xB0,0x3A,0x66,0x46,0x3D,0xBB,0x42,0xA5,0x0C,0x75,0x22,0xD8,0xC3,0x76,0x1E,
                                0x83,0x74,0xF0,0xF6,0x1C,0x26,0xD1,0x4F,0x0B,0xFF,0x4C,0x4D,0xC1,0x87,0x03,0x5A,
                                0xEE,0xA4,0x5D,0x9E,0xF4,0xC8,0x0D,0x62,0x63,0x3E,0x44,0x7B,0xA3,0x68,0x32,0x1B,
                                0xAA,0x2D,0x05,0xF3,0xF7,0x16,0x61,0x94,0xE0,0xD0,0xD3,0x98,0x69,0x78,0xE9,0x0A,
                                0x65,0x91,0x8E,0x35,0x85,0x7A,0x51,0x86,0x10,0x3F,0x7F,0x82,0xDD,0xB5,0x1A,0x95,
                                0xE7,0x43,0xFD,0x9B,0x24,0x45,0xEF,0x92,0x5C,0xE4,0x96,0xA9,0x9C,0x55,0x89,0x9A,
                                0xEA,0xF9,0x90,0x5F,0xB8,0x04,0x84,0xCF,0x67,0x93,0x00,0xA6,0x39,0xA8,0x4E,0x59,
                                0x31,0x6B,0xAD,0x5E,0x5B,0x77,0xB1,0x54,0xDC,0x38,0x41,0xB6,0x47,0x9F,0x73,0xBA,
                                0xF8,0xAE,0xC4,0xBE,0x34,0x01,0x4B,0x2A,0x8D,0xBD,0xC5,0xC6,0xE8,0xAF,0xC9,0xF5,
                                0xCB,0xFB,0xCD,0x79,0xCE,0x12,0x71,0xD2,0xFA,0x09,0xD5,0xBC,0x58,0x19,0x80,0xDA,
                                0x49,0x1D,0xE6,0x2E,0xE3,0x7E,0xB7,0x3B,0xB3,0xA0,0xB9,0xE5,0x57,0x6E,0xD9,0x08,
                                0xEB,0xC7,0xED,0x81,0xF1,0xF2,0xBF,0xC0,0xA7,0x4A,0xD6,0x2B,0xB4,0x72,0x9D,0x0E,
                                0x6D,0xEC,0x48,0xE2,0x33]
    # print("原来的 s 盒：%s" % s_box)
    j = 0
    for i in range(256):
        j = (j + s_box[i] + ord(key[i % len(key)])) % 256
        #j = (j + s_box[i] + ord(key[i])) % 256
        s_box[i], s_box[j] = s_box[j], s_box[i]
    # print("混乱后的 s 盒：%s"% s_box)
    return s_box

def rc4_excrypt(plain, box):
    #print("调用解密程序成功。")
    #plain = base64.b64decode(plain.encode('utf-8'))
    #plain = bytes.decode(plain)
    res = []
    i = j = 0
    for s in plain:
        i = (i + 1) % 256
        j = (j + box[i]) % 256
        box[i], box[j] = box[j], box[i]
        t = (box[i] + box[j]) % 256
        k = box[t]
        res.append(chr(s ^ k))
    # print("res用于解密字符串，解密后是：%res" %res)
    cipher = "".join(res)
    # print("解密后的字符串是：%s" %cipher)
    # print("解密后的输出(没经过任何编码):")
    return cipher


class AppCan(BaseModule):

    def transmit(self, value):
        key = value.replace("-", "")
        l = list(key)
        l.reverse()         #反转字符串，如"abc"变为"cba"
        result = "".join(l)
        #print(result)

        v6 = ['d', 'b', 'e', 'a', 'f', 'c']
        v7 = ['2', '4', '0', '9', '7', '1', '5', '8', '3', '6']
        v0 = []
        ll = list(result)
        i = 0
        for c in ll:
            cc = ord(c)
            if cc >= 97 and cc <= 102:
                v0.append(v6[cc-97])
            elif cc >= 48 and cc <= 57:
                v0.append(v7[cc-48])
            else:
                v0.append(ll[i])
            i = i + 1
            if i == 8 or i == 12 or i == 16 or i ==20:
                v0.append('-')
        #print("".join(v0))
        return "".join(v0)


    def extractKey(self, key, configfile):
        if key != "":
            return key

        value = ""      #store appkey from file "/res/values/strings.xml"
        t = ET.ElementTree(file=configfile)
        for elem in t.iter(tag='string'):
            appid = elem.attrib['name']
            if appid == "appkey" :
                value = elem.text
        #print(value)
        key = self.transmit(value)   #读取appkey之后将其进行转换
        return key


    def decryptFile(self, enfile, key):
        filename = os.path.splitext(os.path.split(enfile)[1])[0]  #refer https://www.cnblogs.com/panfb/p/9546035.html
        #print(filename)
        with open(enfile, "rb") as f:
            data = f.read()
        cipherlen = len(data)-0x111
        #print(str(cipherlen))
        input1 = hashlib.md5()  #要加密的字符串
        input1.update(str(cipherlen).encode("utf-8"))
        input1.update(filename.encode("utf-8"))
        dest1 = input1.digest()  #形如b'\xf5\xb3\xb9\xb3\x03\xf5\xa0YBr\xf9\x9d\x19\x1b\xbfE', hexdigest的结果f5b3b9b303f5a0594272f99d191bbf45, 0x45=69=E
        start = dest1[1]
        #print(start)
        cipher = data[start:start+cipherlen]  #这才是真正的密文段

        input2 = hashlib.md5()
        input2.update(dest1)
        input2.update("982398e^)f8y99e4^$%^&%^&%^&%&^$#$#sdfsda90239%7we98^bjk789234y6cxzv98324df96621378*28973yr^%UBFG%^&*IOyhfdsuyf892yr98ghwequifyh879esa6yf83g2ui1rfgtvbiygf92183klsdahfjsadhjkfsadfbhdj74e8923yhr32hjfkdsahfuy^&2364327848e^$%^$*(&(&wrtf32$6987987fuihewr87ft872".encode("utf-8"))
        input2.update(key.encode("utf-8"))
        input2.update(filename.encode("utf-8"))
        dest2 = input2.hexdigest()  #generate 32 md5 sig successfully
        #print(dest2)
        #hexdigest的十六进制结果是32位，其中可能包含有0x0d，转换之后其去掉0，为0xd
        i = 0
        dest3 = []
        for c in dest2:
            if i%2 == 0:
                if c != "0":
                    dest3.append(c)
            else:
                dest3.append(c)
            i = i + 1
        #print("".join(dest3))
        #将处理过的签名值重复多次，直至满足256位,构建256位初始密钥
        #i = 0
        #dest4 = []
        #length = len(dest3)
        #for i in range(256):
        #    dest4.append(dest3[i%length])
        #key = "".join(dest4)    #len(key) = 256
        #print(key)
        #RC4解密
        s_box = rc4_init_sbox(dest3)   #构建256位初始密钥是为了后续处理初始状态向量值S
        crypt = rc4_excrypt(cipher, s_box)
        return crypt


    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("org.zywx.wbpalmstar.engine.LoadingActivity")
        elif self.host_os == "ios":
            log.error("not support yet.")
            return False
        return False


    def doExtract(self, working_folder):

        extract_folder = self._format_working_folder(working_folder)

        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)
        tmp_folder = os.path.join(extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok=True)
        self._apktool(tmp_folder)

        configfile=os.path.join(tmp_folder, "res/values/strings.xml")
        launch_path = ""
        encryptflag = 0  #0:unknown  1:encrypt
        key = ""

        for dirpath, dirnames, ifilenames in os.walk(tmp_folder):
            if dirpath.find("assets/widget") != -1:   # store web resource  and f != "assets/widget/config.xml"
                for fs in ifilenames:
                    f = os.path.join(dirpath, fs)
                    encryptflag = isEncrypted(f)

                    # if f.endswith("ui-color.css"):
                    #     print("ha")

                    matchObj = re.match(r'(.*)assets/widget/(.*)', f, re.S)
                    newRP = matchObj.group(2)

                    tf = os.path.join(extract_folder, newRP)
                    if not os.access(os.path.dirname(tf), os.R_OK):
                        os.makedirs(os.path.dirname(tf))

                    with open(tf, "wb") as fwh:  #output the plain
                        if encryptflag:             #encrypt
                            key = self.extractKey(key, configfile)
                            fwh.write(self.decryptFile(f, key).encode("UTF-8"))      #the plain after decrypted
                        else:
                            # ugly coding
                            fp = open(f, "rb")
                            c = fp.read()
                            fp.close()
                            fwh.write(c)                                     #no encrypt

                    if f.endswith("assets/widget/config.xml"):
                        encryptflag = isEncrypted(f)
                        if encryptflag:             # encrypted
                            key = self.extractKey(key, configfile)
                            plain = self.decryptFile(f, key)
                        else:                       # no encrypt
                            # ugly coding
                            fp = open(f, "r")
                            plain = fp.read()
                            fp.close()
                        results = re.findall('(?<=<)content.*(?=>)', plain)
                        for r_con in results:
                            src = re.findall('(?<=src=").*(?=")', r_con)
                            if len(src) == 1:
                                launch_path = src[0]
                                break
                #print(launch_path)
        self._dump_info(extract_folder, launch_path)     #store the home page

        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "./test_case/AppCan/apphe.apk"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径
    appcan = AppCan(f, "android")
    if appcan.doSigCheck():
        logging.info("AppCan signature Match")
        extract_folder, launch_path = appcan.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
