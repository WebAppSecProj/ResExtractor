#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import abc
import logging
import sys
import hashlib
import subprocess
import json
import os
import csv
import lief
import zipfile
import biplist
import plistlib

import Config as Config
import platform

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

class BaseModule(metaclass=abc.ABCMeta):
    def __init__(self, detect_file, host_os):
        if os.path.isabs(detect_file):
            self.detect_file = detect_file
        else:
            self.detect_file = os.path.join(os.getcwd(), detect_file)

        self.host_os = host_os
        self.hash = self._gethash()

    def _apktool(self, extract_folder):
        proc = subprocess.Popen("java -jar '{}' d '{}' -f -o '{}'".format(Config.Config["apktool"], self.detect_file, extract_folder), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        #log.info(r)

        return

    def _apktool_no_decode_source(self, extract_folder):
        proc = subprocess.Popen("java -jar '{}' d '{}' -f -s -o '{}'".format(Config.Config["apktool"], self.detect_file, extract_folder), shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        #log.info(r)

        return

    def _format_working_folder(self, working_folder):
        if os.path.isabs(working_folder):
            extract_folder = os.path.join(working_folder, self.hash, Config.Config["local_res_folder"])
        else:
            extract_folder = os.path.join(os.getcwd(), working_folder, self.hash, Config.Config["local_res_folder"])
        return extract_folder

    def _dump_info(self, extract_folder, launch_path):
        info = {"detect_file": self.detect_file, "start_page": launch_path}
        json.dump(info, open(os.path.join(extract_folder, Config.Config["local_res_info"]), 'w', encoding='utf-8'), ensure_ascii=False)
        return

    def _aapt(self):
        if platform.system() == 'Darwin':
            return Config.Config["aapt_osx"]
        elif platform.system() == 'Linux':
            return Config.Config["aapt_linux"]
        elif platform.system() == 'Windows':
            return Config.Config["aapt_windows"]

    # find signature
    def _find_main_activity(self, sig):
        if platform.system() == 'Darwin':
            aapt = Config.Config["aapt_osx"]
        elif platform.system() == 'Linux':
            aapt = Config.Config["aapt_linux"]
        elif platform.system() == 'Windows':
            aapt = Config.Config["aapt_windows"]

        proc = subprocess.Popen("'{}' dump badging '{}'".format(aapt, self.detect_file), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        # e = (proc.communicate()[1]).decode()
        # print("'{}' dump badging '{}'".format(Config.Config["aapt"], self.detect_file))
        # print(e)
        if r.find(sig) != -1:
            return True
        return False

    def _gethash(self):
        with open(self.detect_file, "rb") as frh:
            sha1obj = hashlib.sha1()
            sha1obj.update(frh.read())
            return sha1obj.hexdigest()

    def _ipa_extract(self,working_folder):
        if zipfile.is_zipfile(self.detect_file)==False:
            return False
        target_zip_file = zipfile.ZipFile(self.detect_file)
        target_zip_file.extractall(working_folder)
        return True
    
    def _ipa_app_path(self):
        target_app_path = os.path.dirname(zipfile.ZipFile(self.detect_file).namelist()[1])
        return target_app_path
    
    def _dir_info_plist(self,tar_dir):
        plist_path = os.path.join(tar_dir,"Info.plist")
        #print(plist_path)
        if os.path.exists(plist_path):
            return biplist.readPlist(plist_path)
        return None

    def _dir_info_plist_from_ipa(self,tar_dir):
        plist_path = os.path.join(tar_dir,"Info.plist")
        #print(plist_path)
        target_zip_file = zipfile.ZipFile(self.detect_file)
        #print(target_zip_file.namelist())
        if plist_path in target_zip_file.namelist():
            return plistlib.load(target_zip_file.open(plist_path))
        return None

    def _check_file_exists(self,target_file_name, is_dir=False):
        if zipfile.is_zipfile(self.detect_file)==False:
            return False
        target_zip_file = zipfile.ZipFile(self.detect_file)
        target_file_path = os.path.join(self._ipa_app_path(),target_file_name)
        if is_dir:
            target_file_path +="/"
        return target_file_path in target_zip_file.namelist() 
    
    def _convert_list_to_int(self, target_list):
        target_int = 0
        for tmp_i in range(len(target_list)):
            target_int += target_list[tmp_i]*pow(0x100,tmp_i)
        return target_int

    def _get_target_method_add(self, macho_path,target_class_name,target_method_name):
        if not lief.is_macho(macho_path):
            log.error("executable not macho ? for {}".format(macho_path))
            sys.exit()
        fat_binary = lief.MachO.parse(macho_path,config=lief.MachO.ParserConfig.deep)
        arm64_binary = None 
        for tmp_i in range(fat_binary.size):
            tmp_Binary = fat_binary.at(tmp_i)
            if tmp_Binary.header.cpu_type == lief.MachO.CPU_TYPES.ARM64:
                arm64_binary = tmp_Binary
        if arm64_binary == None:
            log.error("no arm 64 binary in macho {}".format(self.main_macho_path))
            sys.exit()
        for tmp_symbol in arm64_binary.symbols:
            if "["+target_class_name + " " + target_method_name + "]" in tmp_symbol.name:
                return tmp_symbol.value
        class_list_section = arm64_binary.get_section("__objc_classlist")
        
        class_size = class_list_section.size // 0x8
        for tmp_i in range(class_size):
            tmp_class_data_add = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(class_list_section.virtual_address+tmp_i*0x8,0x8))
            '''
            struct cd_objc2_class {
	            uint64_t isa; // point to metaclass need to serch too
	            uint64_t superclass;
	            struct cache_t{
                    uint64_t buckets;
                    uint32_t _mask;
                    uint32_t _occupied
                } cache;
	            uint64_t data; // points to class_ro_t
	        }
            '''
            #get metaclass from class and search method in the metaclass
            tmp_class_metaclass_data_add = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(tmp_class_data_add,0x8))
            tmp_class_ro_t_add = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(tmp_class_metaclass_data_add + 0x4*0x8,0x8))
            '''
            struct cd_objc2_class_ro_t {
	            uint32_t flags;
	            uint32_t instanceStart;
	            uint32_t instanceSize;
	            uint32_t reserved; // *** this field does not exist in the 32-bit version ***
	            uint64_t ivarLayout;
	            uint64_t name;
	            uint64_t baseMethods;
	            uint64_t baseProtocols;
	            uint64_t ivars;
	            uint64_t weakIvarLayout;
	            uint64_t baseProperties;
	        };
            '''
            tmp_class_name_add = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(tmp_class_ro_t_add + 0x3*0x8,0x8))
            tmp_class_baseMethods_add = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(tmp_class_ro_t_add + 0x4*0x8,0x8))
            

            #read class name 
            cur_str_add = tmp_class_name_add
            tmp_class_name = ""
            #print(hex(tmp_class_data_add))
            #print(hex(tmp_class_ro_t_add)) 
            #print(hex(cur_str_add))
            while True:
                #print(hex(cur_str_add))
                if (arm64_binary.get_content_from_virtual_address(cur_str_add,0x1)[0]==0):
                    break
                tmp_class_name +=str(bytes(arm64_binary.get_content_from_virtual_address(cur_str_add,0x1)),"utf-8")
                cur_str_add += 0x1
            #print(tmp_class_name)
            #print(hex(tmp_class_data_add))
            #print(hex(tmp_class_ro_t_add))  
            #print(hex(tmp_class_baseMethods_add))
            if tmp_class_name != target_class_name:
                continue
            if tmp_class_baseMethods_add == 0:
                continue
            # read method array from baseMethods
            tmp_struct_size = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(tmp_class_baseMethods_add,0x4))
            tmp_method_size = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(tmp_class_baseMethods_add+0x4,0x4))

            tmp_method_array_add = tmp_class_baseMethods_add+0x8

            if tmp_struct_size != 0x18:
                log.error("struct size :  {} not 0x18 something wrong".format(tmp_struct_size))
                sys.exit()

            tmp_method_add = None
            for tmp_j in range(tmp_method_size):
                tmp_method_name_add = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(tmp_method_array_add + tmp_j*tmp_struct_size,0x8))
                tmp_method_name = ""
                cur_str_add = tmp_method_name_add
                while True:
                    if (arm64_binary.get_content_from_virtual_address(cur_str_add,0x1)[0]==0):
                        break
                    tmp_method_name +=str(bytes(arm64_binary.get_content_from_virtual_address(cur_str_add,0x1)),"utf-8")
                    cur_str_add += 0x1
                if tmp_method_name == target_method_name:
                    tmp_method_add = self._convert_list_to_int(arm64_binary.get_content_from_virtual_address(tmp_method_array_add + tmp_j*tmp_struct_size + 0x10,0x8))
                    return tmp_method_add
        return None

    def _get_cfstring_char(self, target_binary, target_address):
        is_target_in_cfstring_section = False
        for tmp_section in target_binary.sections:
            if (target_address > tmp_section.virtual_address) & (target_address < (tmp_section.virtual_address + tmp_section.size)):
                if "_cfstring" in tmp_section.name:
                    is_target_in_cfstring_section = True
                    break
        if is_target_in_cfstring_section == False:
            return None
        #cfstring  [ CFString PTR
        #            +8 type
        #            +0x10 String_address
        #            +0x18 string_size
        
        # get string address 
        string_add = self._convert_list_to_int(target_binary.get_content_from_virtual_address(target_address))



    def _log_error(self, module, file, msg):
        log_file = os.path.join(Config.Config["log_folder"], "ModuleError.csv")
        if not os.path.exists(log_file):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'w', newline='') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(['Module', 'Instance', 'Message'])
                f_csv.writerow([module, file, msg])
        else:
            with open(log_file, 'a', newline='') as f:
                f_csv = csv.writer(f)
                f_csv.writerow([module, file, msg])

    def __str__(self):
        return "{} file: {}".format(self.host_os, self.detect_file)

    @abc.abstractmethod
    def doSigCheck(self):
        pass

    @abc.abstractmethod
    def doExtract(self, working_folder):
        pass

