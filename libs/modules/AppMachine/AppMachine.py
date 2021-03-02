#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2.22 2021
auther @ddecadall
"""
import logging
import sys
import shutil
import hashlib
import re
import zipfile

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class AppMachine(BaseModule):
    const_key_seed_str = "http://mobile.appmachine.com/mobilewebservice.asmx"
    key_list = []

    def generateKey(self, key_seed_str):
        key_list = [0x0,0x0,0x0,0x0]
        num = 0
        for tmp_i in range(len(key_seed_str)):
            tmp_char = key_seed_str[tmp_i]
            if (((tmp_char.isalnum())|(tmp_char == "_")|(tmp_char == " "))&((tmp_char != " ")|((tmp_i<=0)|(key_seed_str[tmp_i-1]!=" ")))):
                num3 = self._limit_to_int32((num & 3)<<3)
                num4 = self._limit_to_int32(0xff << (num3 & 0x1f))
                num2 = ((key_list[(num & 0xf) >> 2] & num4)>>(num3 & 0x3f)) & 0xff
                num2 = (((num2 << 1)^(num2 >> 1 )) ^ ord(tmp_char.lower())) & 0xff
                tmp_num = key_list[(num & 0xf)>>2]
                key_list[(num & 0xf)>>2] = tmp_num & self._limit_to_int32((~num4)&0xff+0xffffff00)
			    #print(key_list[(num & 0xf)>>2])

                num5 = self._limit_to_int32((num2 << (num3 & 0x1f))& num4)|(key_list[(num & 0xf) >>2])
			    #print(hex(num5))
                key_list[(num & 0xf)>>2] = num5
                num +=1
			    #print(key_list)
        return key_list

    def convertByteListToIntList(self, target_byte_list):
        byte_length = len(target_byte_list)
        #print(target_byte_list)
        int_list = []
        for tmp_i in range(byte_length // 4):
            tmp_int = self._convert_list_to_int(target_byte_list[tmp_i*0x4:(tmp_i+1)*0x4])
            #print(target_byte_list[tmp_i * 0x4:0x4])
            #print(tmp_int)
            int_list.append(tmp_int)
        return int_list

    def decryptFile(self, enfile):
        enc_file = open(enfile,"rb")
        print(enfile)
        # get encrypted file length 
        enc_file_content = enc_file.read()
        enc_file_length = self._convert_list_to_int(enc_file_content[:4])
        enc_file_content = enc_file_content[4:]
        result_byte_list = []

        remain_file_size = len(enc_file_content)
        # split file by 0x4000 byte , each block convert to int list and decrypt it 
        while remain_file_size > 0 :
            if remain_file_size > 0x4000:
                remain_file_size = remain_file_size - 0x4000
                to_dec_content = enc_file_content[:0x4000]
                enc_file_content = enc_file_content[0x4000:]
                enc_file_int_list = self.convertByteListToIntList(to_dec_content)
                result_byte_list.extend(self.decryptContent(enc_file_int_list))
            
            else:
                #print(len(enc_file_content))
                #print(remain_file_size)
                if remain_file_size%8 != 0:
                    need_fill_length = 8 - (remain_file_size % 8 )
                    remain_file_size = (remain_file_size//8 + 1)*8
                    enc_file_content += bytes(need_fill_length)
                #print(len(enc_file_content))
                enc_file_int_list = self.convertByteListToIntList(enc_file_content)
                result_byte_list.extend(self.decryptContent(enc_file_int_list))
                break
        enc_file.close()
        return bytes(result_byte_list[:enc_file_length])
    
    # modified TEA decrypt algorithm
    def decryptContent(self, enc_int_list):
        key_list = self.key_list
        result_byte_list = []
        num = 13 
        num6 = 0x9e3779b9
        index = 0 
        
        enc_length = len(enc_int_list)
        #print(enc_length)
        #print(enc_int_list)
        while index < enc_length:
            num2 = self._limit_to_int32(enc_int_list[index])
            num3 = self._limit_to_int32(enc_int_list[index+1])

            num4 = 0xc6ef3720
            num5 = 0x20

            while(True):
                if(num5 <= 0):
                    num5 -= 1 
                    enc_int_list[index] = self._limit_to_int32(num2^num)
                    enc_int_list[index+1] = self._limit_to_int32(num3)
                    num = self._limit_to_int32(self._limit_to_int32(num + 0x1b)%0x7ae0)
                    index += 2 
                    break
                num5 -= 1 
                # num3 -= (((num2<<4) ^ (num2>>5))+num2) ^ (num4 + this._key[(num4>>11)&3]) 
                num3 = self._limit_to_int32(num3 - self._limit_to_int32(self._limit_to_int32(self._limit_to_int32(self._limit_to_int32(num2<<4) ^ self._limit_to_int32(num2>>5))+num2) ^ self._limit_to_int32(num4 + key_list[(num4>>11)&3])))
                # num4 = num4 -num6
                num4 = self._limit_to_int32(num4 - num6)
                # num2 -= (((num3<<4) ^ (num3>>5))+num3) ^ (num4 + this._key[(num4 & 3)])
                num2 = self._limit_to_int32(num2 - self._limit_to_int32(self._limit_to_int32(self._limit_to_int32(self._limit_to_int32(num3<<4) ^ self._limit_to_int32(num3>>5))+num3) ^ self._limit_to_int32(num4 + key_list[(num4 & 3)])))
        
        #convert int32 list to byte list 
        #print(enc_int_list)
        for tmp_i in range(len(enc_int_list)):
            result_byte_list.extend(self._convert_int_to_byte_list(enc_int_list[tmp_i],0x4))
        
        return result_byte_list

        
        



    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("\'app.Main\'")
        elif self.host_os == "ios":
            AppMachine_ios_sig = os.path.join("Appmachine.SuperPin.IOS.dll")
            #print(AppMachine_ios_sig)
            if self._check_file_exists(AppMachine_ios_sig):
                return True
        return False

    def doExtract(self, working_folder):
        if self.host_os == "android":
            return self.doExtractAndroid(working_folder)
        elif self.host_os == "ios":
            log.error("no ios ")
    
    

                

    def doExtractiOS(self, working_folder):
        
        launch_path = None

        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)
        tmp_folder = os.path.join(extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok=True)
        
        self._ipa_extract(tmp_folder)

        self.app_dir_path = os.path.join(tmp_folder,self._ipa_app_path())
        self.resource_file_path = os.path.join(self.app_dir_path,"resources.zip")

        if os.path.exists(self.resource_file_path) == False:
            log.error("no resources.zip in path {} something wrong".format(self.resource_file_path))
            #sys.exit()
            return "", ""
        
        tmp_zip_file = zipfile.ZipFile(self.resource_file_path)
        tmp_zip_file.extractall(extract_folder)

        # delete tmp to walk the extract_folder
        shutil.rmtree(tmp_folder)
        self.key_list = self.generateKey(self.const_key_seed_str)


        apps_dat_path = os.path.join(extract_folder,"apps.dat")
        if os.path.exists(apps_dat_path) ==False:
            log.error("no apps.dat in resources.zip {} something wrong".format(apps_dat_path))
            #sys.exit()
            return "", ""
        
        apps_data = ET.parse(apps_dat_path)
        app_drawing_no = None
        for tmp_app_info in apps_data.getroot()[0]:
            if tmp_app_info.tag == "DrawingNo":
                app_drawing_no = tmp_app_info.text
        if app_drawing_no == None:
            log.error("no drawing no in apps.dat {} something wrong".format(apps_dat_path))
            #sys.exit()
            return "", ""
        #print(app_drawing_no)
        # delete all unrelated dir
        for tmp_file in os.listdir(extract_folder):
            if os.path.isdir(os.path.join(extract_folder,tmp_file)):
                if tmp_file != app_drawing_no:
                    shutil.rmtree(os.path.join(extract_folder,tmp_file))
        


        for root_path, dirs, files in os.walk(extract_folder):
            for tmp_file in files:
                if (tmp_file.endswith(".dat")&(tmp_file!="apps.dat")&(tmp_file!="marker.dat")):
                    target_file_path = os.path.join(root_path,tmp_file)
                    dec_result = self.decryptFile(target_file_path)
                    #replace extracted file with decypted content
                    n_target_file = open(target_file_path,"wb")
                    n_target_file.write(dec_result)
                    n_target_file.close()



        

        launch_path = "None"

        self._dump_info(extract_folder, launch_path)     #store the home page

        
        return extract_folder, launch_path

                    

            

    def doExtractAndroid(self, working_folder):

        launch_path = None

        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)
        tmp_folder = os.path.join(extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok=True)
        
        self._apktool(tmp_folder)
        
        #self._ipa_extract(tmp_folder)

        #self.app_dir_path = os.path.join(tmp_folder,self._ipa_app_path())
        self.assets_dir_path = os.path.join(tmp_folder,"assets")
        self.resource_file_path = os.path.join(self.assets_dir_path,"resources.zip")

        if os.path.exists(self.resource_file_path) == False:
            log.error("no resources.zip in path {} something wrong".format(self.resource_file_path))
            #sys.exit()
            return "", ""
        
        tmp_zip_file = zipfile.ZipFile(self.resource_file_path)
        tmp_zip_file.extractall(extract_folder)

        # delete tmp to walk the extract_folder
        shutil.rmtree(tmp_folder)
        self.key_list = self.generateKey(self.const_key_seed_str)
        #print(self.key_list)

        apps_dat_path = os.path.join(extract_folder,"apps.dat")
        if os.path.exists(apps_dat_path) ==False:
            log.error("no apps.dat in resources.zip {} something wrong".format(apps_dat_path))
            #sys.exit()
            return "", ""
        
        apps_data = ET.parse(apps_dat_path)
        app_drawing_no = None
        for tmp_app_info in apps_data.getroot()[0]:
            if tmp_app_info.tag == "DrawingNo":
                app_drawing_no = tmp_app_info.text
        if app_drawing_no == None:
            log.error("no drawing no in apps.dat {} something wrong".format(apps_dat_path))
            #sys.exit()
            return "", ""
        #print(app_drawing_no)
        # delete all unrelated dir
        for tmp_file in os.listdir(extract_folder):
            if os.path.isdir(os.path.join(extract_folder,tmp_file)):
                if tmp_file != app_drawing_no:
                    shutil.rmtree(os.path.join(extract_folder,tmp_file))
        

        for root_path, dirs, files in os.walk(extract_folder):
            for tmp_file in files:
                if (tmp_file.endswith(".dat")&(tmp_file!="apps.dat")&(tmp_file!="marker.dat")):
                    
                    target_file_path = os.path.join(root_path,tmp_file)
                    dec_result = self.decryptFile(target_file_path)
                    #replace extracted file with decypted content
                    n_target_file = open(target_file_path,"wb")
                    n_target_file.write(dec_result)
                    n_target_file.close()



        

        launch_path = "None"

        self._dump_info(extract_folder, launch_path)     #store the home page

        
        return extract_folder, launch_path


def main():
    f = "./test_case/AppMachine/des.apk"    #后续会将当前脚本路径与之相拼接，得到最终detect_file路径
    appcan = AppMachine(f, "android")
    if appcan.doSigCheck():
        logging.info("AppCan signature Match")
        extract_folder, launch_path = appcan.doExtract("working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
