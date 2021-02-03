#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import logging
import shutil
import os
import lief
import capstone
import re

#from libs.modules.APICloud.uzmap_resource_extractor import tools
from libs.modules.BaseModule import BaseModule
import Config as Config

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: http://www.apicloud.com/video_play/2_5

Reference:
https://github.com/newdive/uzmap-resource-extractor
https://blog.csdn.net/u011687188/article/details/80999016
https://bbs.pediy.com/thread-218656.htm
'''

class APICloud(BaseModule):

    def doSigCheck(self):
        if self.host_os == "android":
            return self._find_main_activity("com.uzmap.pkg.LauncherUI")
        elif self.host_os == "ios":
            self.app_dir = self._ipa_app_path()
            self.main_infoplist_content = self._dir_info_plist_from_ipa(self.app_dir)
            #print(self.main_infoplist_content)
            if self.main_infoplist_content["CFBundleExecutable"] == "UZApp":
                #self.main_macho = os.path.join(self.app_dir,"UZApp")
                return True
        return False


    def doExtractAndroid(self, working_folder):

        extract_folder = self._format_working_folder(working_folder)

        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        #os.makedirs(extract_folder, exist_ok = True)

        # https://github.com/newdive/uzmap-resource-extractor
        extractMap = tools.decryptAndExtractAPICloudApkResources(self.detect_file, extract_folder, printLog=True)

        # parse the xml file, construct the path of app code, and extract
        launch_path = ""
        try:
            t = ET.ElementTree(file=os.path.join(extract_folder, "config.xml"))
            for elem in t.iter(tag='content'):
                launch_path = elem.attrib['src']

            self._dump_info(extract_folder, launch_path)
        except:
            self._log_error(os.path.basename(__file__), self.detect_file, "foo")

        return extract_folder, launch_path
    
    def iOSKeyExtract(self):
        print(self.main_macho_path)
        fat_binary = lief.MachO.parse(self.main_macho_path,config=lief.MachO.ParserConfig.deep)
        arm64_binary = None 
        for tmp_i in range(fat_binary.size):
            tmp_Binary = fat_binary.at(tmp_i)
            if tmp_Binary.header.cpu_type == lief.MachO.CPU_TYPES.ARM64:
                arm64_binary = tmp_Binary
        if arm64_binary == None:
            log.error("no arm 64 binary in macho {}".format(self.main_macho_path))
            sys.exit()
        target_function = self._get_target_method_add(self.main_macho_path,"UZPrivacy","getAppKeySecret")
        if target_function == None:
            log.error("no +[UZPrivacy getAppKeySecret]")
            self.app_key = None
            return 

        start_address = target_function.value 
        target_code = bytes(arm64_binary.get_content_from_virtual_address(start_address,0x240))

        cap_md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        ins_list = cap_md.disasm(target_code,start_address)[0]

        #目标_data段地址
        sign_address = 0

        for ins in ins_list:
            if ins.mnemonic == "adr" | ins.mnemonic == "adrp":
                target_mem_add = ins.value.mem.base
                is_target_in_data_section = False
                for tmp_section in arm64_binary.sections:
                    if (target_mem_add > tmp_section.virtual_address) & (target_mem_add < (tmp_section.virtual_address + tmp_section.size)):
                        if "_data" in tmp_section.name:
                            is_target_in_data_section = True
                        break
                if is_target_in_data_section == False:
                    continue
                
                cfstring_address = 0
                tmp_add_list = arm64_binary.get_content_from_virtual_address(target_mem_add,0x8)
                for tmp_i in range(0x8):
                    cfstring_address += tmp_i*0x100 + tmp_add_list[tmp_i]
                # cfstring struct 
                string_address = 0
                tmp_add_list = arm64_binary.get_content_from_virtual_address(cfstring_address + 0x10,0x8)
                for tmp_i in range(0x8):
                    string_address += tmp_i*0x100 + tmp_add_list[tmp_i]
                
                string_size = 0 
                tmp_add_list = arm64_binary.get_content_from_virtual_address(cfstring_address + 0x18,0x8)
                for tmp_i in range(0x8):
                    string_size += tmp_i*0x100 + tmp_add_list[tmp_i]
                key_str = str(bytes(arm64_binary.get_content_from_virtual_address(string_address,string_size))) 
                if (re.match(key_str,"[a-zA-Z0-9]+")==None) | (len(key_str) == 8):
                    continue
                sign_address = target_mem_add
                break
        
        key_seed = ""
        for tmp_i in range(4):
            target_cfstring_address = 0
            tmp_add_list = arm64_binary.get_content_from_virtual_address(sign_address + tmp_i,0x8)
            for tmp_j in range(0x8):
                target_cfstring_address += tmp_j*0x100 + tmp_add_list[tmp_j]

            tmp_string_address = 0
            tmp_add_list = arm64_binary.get_content_from_virtual_address(target_cfstring_address + 0x10, 0x8)
            for tmp_j in range(0x8):
                tmp_string_address = tmp_j * 0x100 + tmp_add_list[tmp_j]
            
            tmp_string_size = 0 
            tmp_add_list = arm64_binary.get_content_from_virtual_address(target_cfstring_address + 0x18, 0x8)
            for tmp_j in range(0x8):
                tmp_string_size = tmp_j * 0x100 + tmp_add_list[tmp_j]

            tmp_str = str(bytes(arm64_binary.get_content_from_virtual_address(tmp_string_address, tmp_string_size)))
            key_seed += tmp_str

        key_Array =  []
        for tmp_i in range(0x14):
            tmp_int = 0 
            for tmp_j in range(0x4):
                tmp_int += tmp_j + arm64_binary.get_content_from_virtual_address(sign_address + tmp_i*0x4 + tmp_j, 0x1)
            key_Array.append(tmp_int)
        
        self.app_key = ""

        for tmp_i in range(0x14):
            tmp_char = key_Array[tmp_i]
            self.app_key += tmp_char
    
    def generateiOSLongKey(self):
        filled_list = [0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xA,0xB,0xC,0xD,0xE,0xF]
        result_key = []
        for tmp_i in range(int(0x100/0x10)):
            for tmp_j in range(0x10):
                result_key.append(filled_list[tmp_j]+tmp_i*0x10)

        tmp_fill_list = []
        for tmp_i in range(0x100):
            tmp_fill_list.append(self.app_key[tmp_i%len(self.app_key)])

        tmp_v10 = 0
        for tmp_i in range(0x100):
            tmp_x = result_key[tmp_i]
            tmp_v10  = (ord(tmp_fill_list[tmp_i]) + tmp_x + tmp_v10) % 0x100
            result_key[tmp_i] = result_key[tmp_v10]
            result_key[tmp_v10] = tmp_x 
        return result_key

    def decryptiOSFile(self, target_file_path):
        target_file_content = list(open(target_file_path,"rb").read())
        encrypt_byte = bytes(target_file_content)
        file_length = len(target_file_content)
        result_list = []
        key_list = self.generateiOSLongKey()

        tmp_v17 = 0 
        tmp_v18 = 0 
        cur_add = 0 
        for tmp_i in range(file_length):
            tmp_v17 = (tmp_v17+1) % 0x100
            tmp_v18 = ([tmp_v17] + tmp_v18) % 0x100
            tmp_v = key_list[tmp_v17]
            key_list[tmp_v17] = key_list[tmp_v18]
            key_list[tmp_v18] = tmp_v 
            tmp_v25 = encrypt_byte[cur_add]
            #print(encrypt_byte[cur_add])
            cur_add +=1
            result_list.append((key_list[(key_list[tmp_v17] + tmp_v)%0x100]) ^ tmp_v25)
        
        return result_list

            

    def doExtractiOSEncrypted(self, extract_folder, tmp_folder):
        self.main_macho_path = os.path.join(tmp_folder, self.app_dir, "UZAPP")

        launch_path = None
        
        self.iOSKeyExtract()

        config_result = self.decryptiOSFile(self.widget_config_path)
        try:
            config_root = ET.fromstring(config_result)
        except:
            log.error("key is wrong for iOS version")
            sys.exit()
        
        launch_path = None

        for child in config_root:
            if child.tag == "content":
                launch_path = child.attrib["src"]

        if launch_path == None:
            log.error("cannot get src rule : {}".config_result)
            sys.exit()
        

        for dir_path,dirs, files in os.walk(self.widget_path):
            for tmp_file in files:
                target_file_path = os.path.join(dir_path,tmp_file)
                sub_path = target_file_path.replace(self.widget_path,"")
                if sub_path.startswith("\\"):
                    sub_path = sub_path[1:]
                target_extract_path = os.path.join(extract_folder,sub_path)
                file_content = self.decryptiOSFile(target_file_path)
                target_extract_file = open(target_extract_path,"wb")
                target_extract_file.write(file_content)
                target_extract_file.close()


        return launch_path
    
    def doExtractiOSNoEncrypted(self, extract_folder, tmp_folder):
        config_root = ET.parse(self.widget_config_path)
        launch_path = None

        for child in config_root:
            if child.tag == "content":
                launch_path = child.attrib["src"]

        if launch_path == None:
            log.error("cannot get src rule : {}".config_result)
            sys.exit()
        
        for dir_path,dirs, files in os.walk(self.widget_path):
            for tmp_file in files:
                target_file_path = os.path.join(dir_path,tmp_file)
                sub_path = target_file_path.replace(self.widget_path,"")
                if sub_path.startswith("\\"):
                    sub_path = sub_path[1:]
                target_extract_path = os.path.join(extract_folder,sub_path)
                shutil.copy(target_file_path,target_extract_path)
        return launch_path


    def doExtractiOS(self, working_folder):
        
        extract_folder = self._format_working_folder(working_folder)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)
        tmp_folder = os.path.join(extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok=True)
        
        self._ipa_extract(tmp_folder)
        self.widget_path = os.path.join(tmp_folder,self._ipa_app_path(),"widget")

        self.widget_config_path = os.path.join(self.widget_path,"config.xml")
        if os.path.exists(self.widget_config_path) == False:
            log.error("no config.xml in path {} ".format(self.widget_config_path))
            sys.exit()

        try:
            ET.parse(self.widget_config_path)
            self.is_encrypted = False
        except:
            self.is_encrypted = True

        if self.is_encrypted == True:
            launch_path = self.doExtractiOSEncrypted( extract_folder, tmp_folder)
        else:
            launch_path = self.doExtractiOSNoEncrypted( extract_folder,tmp_folder)

        shutil.rmtree(tmp_folder)


        return extract_folder, launch_path


    def doExtract(self, working_folder):
        if self.host_os == "android":
            return  self.doExtractAndroid(working_folder)
        else:
            return self.doExtractiOS(working_folder)   

def main():

    f = "./test_case/apicloud/chaoyang.ipa"
    apiCloud = APICloud(f, "ios")
    if apiCloud.doSigCheck():
        logging.info("APICloud signature Match")

        extract_folder, launch_path = apiCloud.doExtract("./working_folder")
        log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
