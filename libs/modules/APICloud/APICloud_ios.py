#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import logging
import shutil
import os
import lief
import capstone
import re
import json

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

    def iOSKeyExtract(self):
        #print(self.main_macho_path)
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

        start_address = target_function 
        target_code = bytes(arm64_binary.get_content_from_virtual_address(start_address,0x240))
        #print(hex(start_address))
        cap_md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        cap_md.detail = True
        ins_list = list(cap_md.disasm(target_code,start_address))

        #目标_data段地址
        sign_address = 0

        #for ins in ins_list:
        for tmp_i in range(len(ins_list)):
            ins = ins_list[tmp_i]
            #code i
            '''
            if (ins.mnemonic == "adr") :
                print(hex(ins.address))
                print(ins.op_str)
                target_mem_add = ins.operands[1].value.imm
                is_target_in_data_section = False
                for tmp_section in arm64_binary.sections:
                    if (target_mem_add > tmp_section.virtual_address) & (target_mem_add < (tmp_section.virtual_address + tmp_section.size)):
                        if "_data" in tmp_section.name:
                            is_target_in_data_section = True
                        break
                if is_target_in_data_section == False:
                    continue
                
                cfstring_address =self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(target_mem_add,0x8))
                print(hex(target_mem_add))
                print(hex(cfstring_address))
                
                
                # cfstring struct 
                string_address = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(cfstring_address + 0x10,0x8))
                
                string_size = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(cfstring_address + 0x18,0x8))
                key_str = str(bytes(arm64_binary.get_content_from_virtual_address(string_address,string_size))) 
                if (re.match(key_str,"[a-zA-Z0-9]+")==None) | (len(key_str) != 8):
                    continue
                sign_address = target_mem_add
                break
            '''
            # adrp, get page address first then get offset in page to calculate the _data memory address
            if (ins.mnemonic == "adrp"):
                if ((ins_list[tmp_i + 1].mnemonic != "nop")|(ins_list[tmp_i + 2].mnemonic != "ldr")):
                    continue
                target_page_add = ins.operands[1].value.imm
                target_page_reg = ins.operands[0].value.reg
                ldr_ins = ins_list[tmp_i + 2]
                ldr_source_reg = ldr_ins.operands[1].mem.base
                if ldr_source_reg != target_page_reg:
                    log.error("ldr source reg {} not equal to adrp reg {}".format(ldr_ins.op_str,ins.op_str))
                    sys.exit()
                ldr_off_value = ldr_ins.operands[1].mem.disp
                #print(hex(ldr_off_value))
                
                target_mem_add = target_page_add + ldr_off_value
                
                #check whether target_mem_add in _data section
                is_target_in_data_section = False
                for tmp_section in arm64_binary.sections:
                    if (target_mem_add > tmp_section.virtual_address) & (target_mem_add < (tmp_section.virtual_address + tmp_section.size)):
                        if "_data" in tmp_section.name:
                            is_target_in_data_section = True
                        break
                if is_target_in_data_section == False:
                    continue
                
                # read target cfstring to check if the string is correct 
                cfstring_address =self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(target_mem_add,0x8))
                #print(hex(target_mem_add))
                #print(hex(cfstring_address))

                string_address = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(cfstring_address + 0x10,0x8))
                
                string_size = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(cfstring_address + 0x18,0x8))
                key_str = str(bytes(arm64_binary.get_content_from_virtual_address(string_address,string_size)),"utf-8") 
                #print(key_str)
                if ((re.match("[a-zA-Z0-9]+",key_str)==None) | (len(key_str) != 8)):
                    #print(len(key_str))
                    continue
                sign_address = target_mem_add
                break
                

                
        
        key_seed = ""
        #print(sign_address)
        # 4 cfstring address in _data
        # after 4 cfstring is the change_array
        for tmp_i in range(4):
            target_cfstring_address = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(sign_address + tmp_i*0x8,0x8))

            tmp_string_address = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(target_cfstring_address + 0x10, 0x8))

            
            tmp_string_size = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(target_cfstring_address + 0x18, 0x8))


            tmp_str = str(bytes(arm64_binary.get_content_from_virtual_address(tmp_string_address, tmp_string_size)),"utf-8")
            key_seed += tmp_str
        #print(key_seed)
        key_Array =  []
        for tmp_i in range(0x14):
            #print(hex(sign_address + 0x20 + tmp_i*0x4))
            tmp_int = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(sign_address + 0x20 + tmp_i*0x4, 0x4))
            key_Array.append(tmp_int)

        self.app_key = ""

        for tmp_i in range(0x14):
            tmp_char = key_seed[key_Array[tmp_i]]
            self.app_key += tmp_char
        
        #print(self.app_key)

        self.long_key_list = self.generateiOSLongKey()
    
    

    def decryptiOSFile(self, target_file_path):
        target_file_content = list(open(target_file_path,"rb").read())
        encrypt_byte = bytes(target_file_content)
        file_length = len(target_file_content)
        result_list = []
        key_list = self.long_key_list.copy()
        #print(key_list)

        tmp_v17 = 0 
        tmp_v18 = 0 
        cur_add = 0 
        for tmp_i in range(file_length):
            tmp_v17 = (tmp_v17 + 1) % 0x100
            tmp_v18 = (key_list[tmp_v17] + tmp_v18) % 0x100
            tmp_v = key_list[tmp_v17]
            key_list[tmp_v17] = key_list[tmp_v18]
            key_list[tmp_v18] = tmp_v 
            tmp_v25 = encrypt_byte[cur_add]
            #print(encrypt_byte[cur_add])
            cur_add += 1
            result_list.append((key_list[(key_list[tmp_v17] + tmp_v)%0x100]) ^ tmp_v25)
        
        return result_list

    def isSpecialFile(self,file_path):
        if ".filelist.txt" in file_path:
            return True
        if ".project" in file_path:
            return True
        if file_path.endswith(".png"):
            return True
        if file_path.endswith(".gif"):
            return True
        if file_path.endswith(".json"):
            is_encrypted = False
            try:
                json.loads(open(file_path).read())
                is_encrypted = False
            except:
                is_encrypted = True
            if is_encrypted == False:
                return True
        if file_path.endswith(".xml"):
            is_encrypted = False
            try:
                ET.parse(file_path)
                is_encrypted = False
            except:
                is_encrypted = True
            if is_encrypted == False:
                return True
        return False        

    def doExtractiOSEncrypted(self, extract_folder, tmp_folder):
        self.main_macho_path = os.path.join(tmp_folder, self.app_dir, "UZAPP")

        launch_path = None
        
        self.iOSKeyExtract()

        config_result = self.decryptiOSFile(self.widget_config_path)
        
        try:
            config_root = ET.fromstring(str(bytes(config_result),"utf-8"))
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
        

        for tmp_root, tmp_dirs, files in os.walk(self.widget_path):
            for tmp_dir in tmp_dirs:
                tmp_dir_path = os.path.join(tmp_root,tmp_dir)
                sub_tmp_dir_path = tmp_dir_path.split(self.widget_path)[1]
                #print(sub_tmp_dir_path)
                if sub_tmp_dir_path.startswith("/"):
                    sub_tmp_dir_path = sub_tmp_dir_path[1:]
                target_dir_path = os.path.join(extract_folder,sub_tmp_dir_path)
                #print(target_dir_path)
                if not os.path.exists(target_dir_path):
                    os.makedirs(target_dir_path)
            for tmp_file in files:
                target_file_path = os.path.join(tmp_root,tmp_file)
                
                sub_path = target_file_path.replace(self.widget_path,"")
                if sub_path.startswith("\\"):
                    sub_path = sub_path[1:]
                if sub_path.startswith("/"):
                    sub_path = sub_path[1:]
                
                target_extract_path = os.path.join(extract_folder,sub_path)
                if self.isSpecialFile(target_file_path) == True:
                    shutil.copy(target_file_path,target_extract_path)
                    continue
                file_content = self.decryptiOSFile(target_file_path)
                #print(target_file_path)
                target_extract_file = open(target_extract_path,"wb")
                #print(str(bytes(file_content),"utf-8"))
                target_extract_file.write(bytes(file_content))
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
