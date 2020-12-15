import os
import urllib
import json
import requests
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
    target_date = None
    cur_time = None
    date_str = None
    def __init__(self,main_config):
        self.Config = main_config
        self.secret_key = self.Config["secret_key"]
        self.userid = self.Config["user_id"]
        self.target_date = self.Config["target_date"]
    
    def generateNonce(self):
        sample_str = "abcdefghijklmnopqrstuvwxyz!@#$%^&*()"
        rand_length = random.randint(5,30)
        self.nonce = "".join(random.sample(sample_str,rand_length))
    
    def generateSign(self,request_content):
        sign = hashlib.md5(("".join([str(request_content[i]) for i in sorted(request_content.keys())])+self.secret_key).encode("utf-8")).hexdigest()
        request_content["sign"] = sign
    
    def generateTime(self):
        self.cur_time = str(int(time.time()))

    def generateDate(self):
        cur_date = datetime.datetime.strptime(self.target_date,"%Y-%M-%d")
        before_date = cur_date - datetime.timedelta(days = 1)
        Date_str = "stime:\"{}\" and etime:\"{}\"".format(before_date,cur_date)
        self.date_str = Date_str


    
    def queryTargetDateApplications(self):
        #construct requset
        request_content = {}
        request_content["userid"] = self.userid
        self.generateNonce()
        request_content["nonce"] = self.nonce
        self.generateTime()
        request_content["time"] = self.cur_time
        request_content["version"] = "1.0"
        self.generateDate()
        request_content["query"] = self.date_str
        self.generateSign(request_content)

        request_json = json.dumps(request_content)
        log.info(request_content)
        print(request_json)
        result_json = requests.post(self.Config["janus_url"]+self.Config["apk_query_address"],data=request_json)
        result_content = json.loads(result_json.text)
        log.info("application list : {}".format(result_content))

        # analyze request result and request the download address one by one 
        if "data" not in result_content:
            log.error("query nothing from janus , result data {}".format(result_content))
            sys.exit()
        target_application_sha1_list = {}
        for tmp_app in result_content["data"]:
            if ("sha1" not in tmp_app) | ("name" not in tmp_app):
                log.error("request result no sha1 {}".format(tmp_app))
                sys.exit()
            target_application_sha1_list[tmp_app["sha1"]] = {"name":tmp_app["name"]} 
        # target_application_sha1_list[(application sha1)] = {"name"}
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
                log.error("request result no status for {} : {}".fomat(request_json,result_content))
                sys.exit()
            
            if result_content["status"]!=200:
                print("cannot request download address for {} reson : {}".format(target_application_sha1_list[tmp_sha1]["name"],result_content["msg"]))
                continue
            
            if "download_url" not in result_content:
                log.error("request result no download_url for {} : {}".fomat(request_json,result_content))
                sys.exit()

            target_application_sha1_list[tmp_sha1]["download"] = result_content["download_url"]
            time.sleep(1.4)
        return target_application_sha1_list
            


