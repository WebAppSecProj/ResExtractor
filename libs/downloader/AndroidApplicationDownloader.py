import os
import urllib
import json
import requests
import threading
import importlib
import random
import time
import datetime
import hashlib
import sys
import logging
logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


class AndroidApplicationDownloader:
    Config = None
    secret_key = None
    userid = None
    nonce = None
    cur_time = None
    date_str = None
    thread_num_lock = None
    result_write_lock = threading.Lock()
    result_write_file_path = None
    def __init__(self,main_config):
        self.Config = main_config
        self.secret_key = self.Config["secret_key"]
        self.userid = self.Config["user_id"]
        self.thread_num_lock = threading.Semaphore(self.Config["max_thread"])
        self.result_write_file_path = self.Config["workfile"]["res_output_list_file"]

    
    def generateNonce(self):
        sample_str = "abcdefghijklmnopqrstuvwxyz!@#$%^&*()"
        rand_length = random.randint(5,30)
        self.nonce = "".join(random.sample(sample_str,rand_length))
    
    def generateSign(self,request_content):
        sign = hashlib.md5(("".join([str(request_content[i]) for i in sorted(request_content.keys())])+self.secret_key).encode("utf-8")).hexdigest()
        request_content["sign"] = sign
    
    def generateTime(self):
        self.cur_time = str(int(time.time()))

    def generatequery(self):
        
        #the main.py will check if config["market"]has at least one market
        query_str = "stime:\"{}\" and etime:\"{}\" and market:\"".format(self.Config["start_date"],self.Config["end_date"])
        for tmp_market in self.Config["market"]:
            query_str += (tmp_market+",")
        query_str = query_str[:-1]
        query_str = query_str + "\""
        self.date_str = query_str

    def constructBasicRequest(self, request_content):
        request_content["userid"] = self.userid
        self.generateNonce()
        request_content["nonce"] = self.nonce
        self.generateTime()
        request_content["time"] = self.cur_time
        request_content["version"] = "1.0"
        self.generatequery()
        request_content["query"] = self.date_str
        request_content["pagesize"] = self.Config["max_request_page_size"]
        self.generateSign(request_content)

    def queryApplicationList(self):
        request_content = {}
        target_application_sha1_list = {}
        self.constructBasicRequest(request_content)
        page_size_request_json = json.dumps(request_content)
        log.info("page size request : {}".format(page_size_request_json))
        result_json = requests.post(self.Config["janus_url"]+self.Config["apk_query_address"],data=page_size_request_json)
        result_content = json.loads(result_json.text)
        log.info("result : {}".format(result_content))
        time.sleep(1.5)
        if "status" not in result_content:
            log.error("no status in request result : {}".format(result_json))
            sys.exit()
        if result_content["status"]!=200:
            log.error("request result error : {}".format(result_json))
            sys.exit()
        if 'paging' not in result_content:
            if "data" not in result_content:
                log.error("query nothing from janus , result data {}".format(result_content))
                sys.exit()
            for tmp_app in result_content["data"]:
                if ("sha1" not in tmp_app) | ("name" not in tmp_app):
                    log.error("request result no sha1 {}".format(tmp_app))
                    sys.exit()
                target_application_sha1_list[tmp_app["sha1"]] = {"name":tmp_app["name"]} 
            return target_application_sha1_list
        if "page_total" not in  result_content["paging"]:
            log.error("no page total in request paging {}".format(result_json))
            sys.exit()
        page_total = result_content["paging"]["page_total"]

        for cur_page in range(page_total):
            request_content = {}
            request_content["page"] = cur_page+1
            self.constructBasicRequest(request_content)
            application_request_json = json.dumps(request_content)
            log.info("each page request : {}".format(application_request_json))
            result_json = requests.post(self.Config["janus_url"]+self.Config["apk_query_address"],data=application_request_json)
            result_content = json.loads(result_json.text)
            log.info("result json : {}".format(result_content))
            if "data" not in result_content:
                log.error("query nothing from janus , result data {}".format(result_content))
                sys.exit()
            for tmp_app in result_content["data"]:
                if ("sha1" not in tmp_app) | ("name" not in tmp_app):
                    log.error("request result no sha1 {}".format(tmp_app))
                    sys.exit()
                target_application_sha1_list[tmp_app["sha1"]] = {"name":tmp_app["name"]} 
            time.sleep(1.5)


        #log.info(request_content)
        #log.info(request_json)
        
        return target_application_sha1_list

    def downloadAppAndExtractRes(self,tar_app_sha1,tar_app_info):
        with self.thread_num_lock:
            app_sha1 = tar_app_sha1
            app_download_url = tar_app_info["download"]
            request = requests.get(app_download_url)
            tar_apk_path = os.path.join(self.Config["workdir"]["apk_folder"],app_sha1+".apk")
            with open(tar_apk_path,"wb") as apk:
                apk.write(request.content)
            log.info("end download")
            for to_check_module_name in self.Config["modules"]:
                target_framework_check_class = getattr(importlib.import_module(to_check_module_name),self.Config["modules"][to_check_module_name])
                target_check = target_framework_check_class(tar_apk_path,"android")
                if target_check.doSigCheck():
                    tar_module_folder = os.path.join(os.getcwd(),self.Config["workdir"]["res_output_folder"],self.Config["modules"][to_check_module_name])
                    if not os.path.exists(tar_module_folder):
                        os.mkdir(tar_module_folder)
                    tar_extract_folder = os.path.join(tar_module_folder,app_sha1)
                    log.info("module {} found in this application".format(self.Config["modules"][to_check_module_name]))
                    if not os.path.exists(tar_extract_folder):
                        os.mkdir(tar_extract_folder)
                    else:
                        continue
                    target_check.doExtract(tar_extract_folder)
                    #extract_info.json
                    extract_info_path = os.path.join(tar_extract_folder,tar_app_sha1,self.Config["extract_info_file"])
                    if os.path.exists(extract_info_path):
                        extract_info_file = open(extract_info_path,"r")
                        result = json.load(extract_info_file)
                        result["apkname"] = tar_app_info["name"]
                        result["apksha1"] = tar_app_sha1
                        result["modulename"] = self.Config["modules"][to_check_module_name]
                        extract_info_file.close()
                        json.dump(result,open(extract_info_path,"w",encoding='utf-8'),ensure_ascii=False)
                    #write apk name and its module to file 
                    if self.result_write_lock.acquire():
                        tmp_file = open(self.result_write_file_path,"a")
                        tmp_file.write("apk: {} sha1 {} module : {} \n".format(tar_app_info["name"],tar_app_sha1,self.Config["modules"][to_check_module_name]))
                        tmp_file.close()
                        self.result_write_lock.release()

            #else:
                #log.info("module {} sig not in this application".format(main_config.Config["modules"][to_check_module_name]))
        
            if self.Config["need_to_delete_apk"]:
                os.remove(tar_apk_path)


    def downloadAndExtractApplications(self):

        target_application_sha1_list = self.queryApplicationList()

        sub_thread_list = []
        
        for tmp_sha1 in target_application_sha1_list:
            download_request_content = {}
            download_request_content["userid"] = self.userid
            self.generateNonce()
            download_request_content["nonce"] = self.nonce
            self.generateTime()
            download_request_content["time"] = self.cur_time
            download_request_content["version"] = "1.0"
            download_request_content["sha1"] = tmp_sha1
            self.generateSign(download_request_content)

            request_json = json.dumps(download_request_content)
            result_json = requests.post(self.Config["janus_url"] + self.Config["apk_download_address"],data=request_json)
            result_content = json.loads(result_json.text)
            log.info("download url : {}".format(request_json))
            log.info("download result : {}".format(result_content))

            if "status" not in result_content:
                log.error("request result no status for {} : {}".format(request_json,result_content))
                sys.exit()
            
            if result_content["status"]!=200:
                print("cannot request download address for {} reson : {}".format(target_application_sha1_list[tmp_sha1]["name"],result_content["msg"]))
                continue
            
            if "download_url" not in result_content:
                log.error("request result no download_url for {} : {}".fomat(request_json,result_content))
                sys.exit()

            target_application_sha1_list[tmp_sha1]["download"] = result_content["download_url"]
            sub_thread = threading.Thread(target=self.downloadAppAndExtractRes,args = (tmp_sha1,target_application_sha1_list[tmp_sha1]))
            sub_thread_list.append(sub_thread)
            sub_thread.start()
            time.sleep(1.4)
        
        for tmp_sub_thread in sub_thread_list:
            tmp_sub_thread.join()
        
            


