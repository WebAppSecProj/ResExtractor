import os 
import sys 
import logging
import datetime
import _thread
import threading
import requests
import importlib
import argparse
from Config import Config
import EnvChecker

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
from contextlib import closing
import zipfile

from libs.downloader.AndroidApplicationDownloader import AndroidApplicationDownloader
logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

JanusConfig = {
    "file_info_logger": os.path.join(os.getcwd(), "ExtractorJanus", "file_module_list.txt")

    "workfile": {
        "res_output_list_file": os.path.join(os.getcwd(), "output", "apk_module_list.txt")
    },
    "workdir": {
        "working_folder": os.path.join(os.getcwd(), "working_folder"),
        "tmp_folder": os.path.join(os.getcwd(), "temp"),
        "lib_folder": os.path.join(os.getcwd(), "libs"),
        "apk_folder": os.path.join(os.getcwd(), "apks"),
        "output_folder": os.path.join(os.getcwd(), "output"),
        "res_output_folder": os.path.join(os.getcwd(), "output", "res_output")
    },
    "market": ["huawei"],
    "market_list": ["googleplay", "apkpure", "yandex", "uptodown", "wandoujia", "baidu", "360", "qq", "appchina", "eoe",
                    "huawei", "anzhi", "yidong", "meizu", "xiaomi", "lianxiang", "kupai", "jinli", "hiapk", "ppzhushou",
                    "nduo", "mumayi", "dianxin", "sogou", "liqu", "zol"],
    "secret_key": "",
    "user_id": "bxmwr91j04t1121c",
    "max_query_days": 364,
    "max_thread": 5,
    "need_to_delete_apk": True,
    "max_request_page_size": 100,
    "janus_url": "http://priv.api.appscan.io",
    "apk_query_address": "/apk/query",
    "apk_download_address": "/apk/download",
    "start_date": str(datetime.date.today() - datetime.timedelta(days=2)),
    "end_date": str(datetime.date.today() - datetime.timedelta(days=1)),
}



    

def checkModuleExists():
    #check module in config is in libs or not 
    if "modules" not in main_config.Config:
        log.error("main_config file is wrong, no modules in config")
        sys.exit()
    else:
        for tar_module_name in main_config.Config["modules"]:
            tmp_module_path = os.getcwd()
            for tmp_path_name in tar_module_name.split("."):
                tmp_module_path = os.path.join(tmp_module_path,tmp_path_name)
            tmp_module_path = tmp_module_path + ".py"
            if not os.path.exists(tmp_module_path):
                log.error("module {} is not exists, is there some thing wrong".format(tmp_module_path))
                sys.exit()
            try:
                tmp_module = getattr(importlib.import_module(tar_module_name), main_config.Config["modules"][tar_module_name])
            except AttributeError:
                log.error("no attr {} in module {}".format(main_config.Config["modules"][tar_module_name],tar_module_name))
                sys.exit()
            try:
                getattr(tmp_module,"doSigCheck")
                getattr(tmp_module,"doExtract")
            except AttributeError:
                log.error("no doSigCheck or doExract in module {}".format(tar_module_name))
                sys.exit()

def cleanTmpDir():
    tmp_dir_path = main_config.Config["workdir"]["tmp_folder"]
    if os.path.exists(tmp_dir_path):
        os.rmdir(tmp_dir_path)
    os.mkdir(tmp_dir_path)

# check the validation of the query
def checkTargetDateInRange(target_date):
    today = datetime.date.today()
    if (target_date > today):
        log.error("oops! reset the data {}".format(target_date))
        sys.exit()
    if ((target_date - today).days > JanusConfig["max_query_days"]):
        log.error("allow query across {} days".format(JanusConfig["max_query_days"]))
        sys.exit()


def checkEnv():
    checkExist()
    checkModuleExists()
    cleanTmpDir()


'''
def downloadAppAndExtractRes(tar_app_sha1,tar_app_info):
    with thread_num_lock:
        app_sha1 = tar_app_sha1
        app_download_url = tar_app_info["download"]
        request = requests.get(app_download_url)
        tar_apk_path = os.path.join(main_config.Config["workdir"]["apk_folder"],app_sha1+".apk")
        with open(tar_apk_path,"wb") as apk:
            apk.write(request.content)
        log.info("end download")
        for to_check_module_name in main_config.Config["modules"]:
            target_framework_check_class = getattr(importlib.import_module(to_check_module_name),main_config.Config["modules"][to_check_module_name])
            target_check = target_framework_check_class(tar_apk_path,"android")
            if target_check.doSigCheck():
                tar_extract_folder = os.path.join(os.getcwd(),main_config.Config["workdir"]["res_output_folder"],app_sha1)
                log.info("module {} found in this application".format(main_config.Config["modules"][to_check_module_name]))
                if not os.path.exists(tar_extract_folder):
                    os.mkdir(tar_extract_folder)
                target_check.doExtract(tar_extract_folder)
            #else:
                #log.info("module {} sig not in this application".format(main_config.Config["modules"][to_check_module_name]))
        
        if main_config.Config["need_to_delete_apk"]:
            os.remove(tar_apk_path)
'''

def startToWork():
    apk_downloader = AndroidApplicationDownloader(main_config.Config)
    #target_date_application_list = apk_downloader.queryTargetDateApplications()
    apk_downloader.downloadAndExtractApplications()
    #sub_thread_list = []
    '''
    for target_app_sha1 in target_date_application_list:
        log.info("start new thread to download and extract res of {}".format(target_app_sha1))
        sub_thread = threading.Thread(target=downloadAppAndExtractRes,args = (target_app_sha1,target_date_application_list[target_app_sha1]))
        sub_thread_list.append(sub_thread)
        sub_thread.start()
     
    log.info("wait till all sub thread finish its download and extract job")

    for sub_thread in sub_thread_list:
        sub_thread.join()
    
    log.info("finish all the job")
    '''
    

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

    def __init__(self, main_config):
        self.Config = main_config
        self.secret_key = self.Config["secret_key"]
        self.userid = self.Config["user_id"]
        self.thread_num_lock = threading.Semaphore(self.Config["max_thread"])
        self.result_write_file_path = self.Config["workfile"]["res_output_list_file"]

    def generateNonce(self):
        sample_str = "abcdefghijklmnopqrstuvwxyz!@#$%^&*()"
        rand_length = random.randint(5, 30)
        self.nonce = "".join(random.sample(sample_str, rand_length))

    def generateSign(self, request_content):
        sign = hashlib.md5(
            ("".join([str(request_content[i]) for i in sorted(request_content.keys())]) + self.secret_key).encode(
                "utf-8")).hexdigest()
        request_content["sign"] = sign

    def generateTime(self):
        self.cur_time = str(int(time.time()))

    def generatequery(self):

        # the main.py will check if config["market"]has at least one market
        query_str = "stime:\"{}\" and etime:\"{}\" and market:\"".format(self.Config["start_date"],
                                                                         self.Config["end_date"])
        for tmp_market in self.Config["market"]:
            query_str += (tmp_market + ",")
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
        result_json = requests.post(self.Config["janus_url"] + self.Config["apk_query_address"],
                                    data=page_size_request_json)
        result_content = json.loads(result_json.text)
        log.info("result : {}".format(result_content))
        time.sleep(1.5)
        if "status" not in result_content:
            log.error("no status in request result : {}".format(result_json))
            sys.exit()
        if result_content["status"] != 200:
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
                target_application_sha1_list[tmp_app["sha1"]] = {"name": tmp_app["name"]}
            return target_application_sha1_list
        if "page_total" not in result_content["paging"]:
            log.error("no page total in request paging {}".format(result_json))
            sys.exit()
        page_total = result_content["paging"]["page_total"]

        for cur_page in range(page_total):
            request_content = {}
            request_content["page"] = cur_page + 1
            self.constructBasicRequest(request_content)
            application_request_json = json.dumps(request_content)
            log.info("each page request : {}".format(application_request_json))
            result_json = requests.post(self.Config["janus_url"] + self.Config["apk_query_address"],
                                        data=application_request_json)
            result_content = json.loads(result_json.text)
            log.info("result json : {}".format(result_content))
            if "data" not in result_content:
                log.error("query nothing from janus , result data {}".format(result_content))
                sys.exit()
            for tmp_app in result_content["data"]:
                if ("sha1" not in tmp_app) | ("name" not in tmp_app):
                    log.error("request result no sha1 {}".format(tmp_app))
                    sys.exit()
                target_application_sha1_list[tmp_app["sha1"]] = {"name": tmp_app["name"]}
            time.sleep(1.5)

        # log.info(request_content)
        # log.info(request_json)

        return target_application_sha1_list

    def downloadAppAndExtractRes(self, tar_app_sha1, tar_app_info, index, total):
        with self.thread_num_lock:

            log.info("{}/{}: processing {}".format(index, total, tar_app_sha1))

            tar_apk_path = os.path.join(self.Config["workdir"]["apk_folder"], tar_app_sha1 + ".apk")

            r = requests.get(url=tar_app_info["download"], verify=False, stream=True)
            if r.status_code != 200:
                return

            with closing(r) as res:
                with open(tar_apk_path, 'wb') as fd:
                    for chunk in res.iter_content(chunk_size=10*1024*1024):
                        if chunk:
                            fd.write(chunk)
                    fd.flush()

            try:
                zf = zipfile.ZipFile(tar_apk_path, "r")
            except:
                return
            if "AndroidManifest.xml" not in zf.namelist():
                return

            for to_check_module_name in self.Config["modules"]:
                target_framework_check_class = getattr(importlib.import_module(to_check_module_name),
                                                       self.Config["modules"][to_check_module_name])
                target_check = target_framework_check_class(tar_apk_path, "android")
                if target_check.doSigCheck():
                    log.info("module {} found in this application".format(self.Config["modules"][to_check_module_name]))

                    tar_module_folder = os.path.join(os.getcwd(), self.Config["workdir"]["res_output_folder"],
                                                     self.Config["modules"][to_check_module_name])
                    if not os.path.exists(tar_module_folder):
                        os.mkdir(tar_module_folder)

                    tar_extract_folder = os.path.join(tar_module_folder, tar_app_sha1)
                    if not os.path.exists(tar_extract_folder):
                        os.mkdir(tar_extract_folder)

                    try:
                        target_check.doExtract(tar_extract_folder)
                    except:
                        log.error("processing {} error".format(tar_app_sha1))
                        # exit(0)
                        continue
                    # extract_info.json
                    extract_info_path = os.path.join(tar_extract_folder, tar_app_sha1, self.Config["extract_info_file"])
                    if os.path.exists(extract_info_path):
                        extract_info_file = open(extract_info_path, "r")
                        result = json.load(extract_info_file)
                        result["apkname"] = tar_app_info["name"]
                        result["apksha1"] = tar_app_sha1
                        result["modulename"] = self.Config["modules"][to_check_module_name]
                        extract_info_file.close()
                        json.dump(result, open(extract_info_path, "w", encoding='utf-8'), ensure_ascii=False)
                    # write apk name and its module to file
                    if self.result_write_lock.acquire():
                        tmp_file = open(self.result_write_file_path, "a")
                        tmp_file.write("apk: {} sha1 {} module : {} \n".format(tar_app_info["name"], tar_app_sha1,
                                                                               self.Config["modules"][
                                                                                   to_check_module_name]))
                        tmp_file.close()
                        self.result_write_lock.release()

                # del(to_check_module_name)

            # else:
            # log.info("module {} sig not in this application".format(main_config.Config["modules"][to_check_module_name]))

            if self.Config["need_to_delete_apk"]:
                os.remove(tar_apk_path)

    def downloadAndExtractApplications(self):

        target_application_sha1_list = self.queryApplicationList()

        sub_thread_list = []
        counter = 0

        for tmp_sha1 in target_application_sha1_list:
            counter += 1
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
            result_json = requests.post(self.Config["janus_url"] + self.Config["apk_download_address"],
                                        data=request_json)

            try:
                result_content = json.loads(result_json.text)
            except:
                continue

            #log.info("download url : {}".format(request_json))
            #log.info("download result : {}".format(result_content))

            if "status" not in result_content:
                log.error("request result no status for {} : {}".format(request_json, result_content))
                # sys.exit()
                continue

            if result_content["status"] != 200:
                print("cannot request download address for {} reson : {}".format(
                    target_application_sha1_list[tmp_sha1]["name"], result_content["msg"]))
                continue

            if "download_url" not in result_content:
                log.error("request result no download_url for {} : {}".fomat(request_json, result_content))
                # sys.exit()
                continue

            target_application_sha1_list[tmp_sha1]["download"] = result_content["download_url"]
            # threading.Thread(target=self.downloadAppAndExtractRes,
            #                  args=(tmp_sha1, target_application_sha1_list[tmp_sha1])).start()
            sub_thread = threading.Thread(target=self.downloadAppAndExtractRes,args = (tmp_sha1, target_application_sha1_list[tmp_sha1], counter, len(target_application_sha1_list)))
            sub_thread_list.append(sub_thread)
            sub_thread.start()
            # janus allows 40 queries per minute
            time.sleep(2)

        for tmp_sub_thread in sub_thread_list:
            tmp_sub_thread.join()


# parse the argument
def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--secret-key', required=True, help="Secret key for connecting janus.")
    parser.add_argument('--target-date', help="Target date to query, default is yesterday, a query period exceeding {} days is not allowed.".format(JanusConfig["max_query_days"]))
    parser.add_argument('--start-date', help="Start date of the query.")
    parser.add_argument('--end-date', help="End date of the query.")
    parser.add_argument('--market', type=str, help="APP market in query. Huawei APP market is set if no argument supplemented; Use `,' to split multiple markets; Use `all' to query all markets.")
    parser.add_argument('--show-market', action='store_true', help="To list supported APP markets.")

    args = parser.parse_args()
    JanusConfig["secret_key"] = args.secret_key

    if args.target_date and (args.start_date or args.end_date):
        log.error("overlapping date setting")
        parser.print_help()
        sys.exit()

    if args.target_date:
        try:
            format_target_date = datetime.datetime.strptime(args.target_date, "%Y-%m-%d")
        except ValueError:
            log.error("wrong argument for --target-date, should follow the format `year-month-day'")
            parser.print_help()
            sys.exit()

        checkTargetDateInRange(format_target_date.date())
        checkTargetDateInRange(format_target_date.date() - datetime.timedelta(days = 1))

        JanusConfig["end_date"] = args.target_date
        JanusConfig["start_date"] = format_target_date.date() - datetime.timedelta(days = 1)

    if args.show_market:
        print("market list:")
        print("{}".format(JanusConfig["market_list"]))
        sys.exit()
    if args.market:
        JanusConfig["market"] = []
        lst_market = args.market.split(",")

        if "all" in lst_market:
            JanusConfig["market"]=JanusConfig["market_list"]
        else:
            for tmp_market in lst_market:
                if tmp_market not in JanusConfig["market_list"]:
                    log.error("market {} is not in market list, current supported marks: {}.".format(tmp_market, JanusConfig["market_list"]))
                    sys.exit()
                JanusConfig["market"].append(tmp_market)
            if JanusConfig["market"] == []:
                log.error("no market set")
                parser.print_help()
                sys.exit()
    else:
        # default configuration
        JanusConfig["market"].append("huawei")

    if args.start_date and args.end_date:
        checkTargetDateInRange(datetime.datetime.strptime(args.start_date, "%Y-%m-%d"))
        checkTargetDateInRange(datetime.datetime.strptime(args.end_date, "%Y-%m-%d"))

        try:
            start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            log.error("invalid --start-date argument, use the date format: year-month-day")
            parser.print_help()
            sys.exit()

        try:
            end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            log.error("invalid --end-date argument, use the date format: year-month-day")
            parser.print_help()
            sys.exit()

        if start_date > end_date:
            log.error("switch the --start-date and --end-date argument")
            parser.print_help()
            sys.exit()

        JanusConfig["start_date"] = args.start_date
        JanusConfig["end_date"] = args.end_date

    elif args.start_date or args.end_date:
        log.error("should provide --target-date and --end-date in a pair.")
        sys.exit(1)


def check_env():
    # common checker
    if EnvChecker.doCheck() == False:
        sys.exit(1)

    #check work file exists
    if "workfile" not in main_config.Config:
        log.error("main_config file is wrong,no workfile in config")
        sys.exit()
    else:
        for work_file in main_config.Config["workfile"]:
            if not os.path.exists(main_config.Config["workfile"][work_file]):
                log.error("work file {} does not exist".format(main_config.Config["workfile"][work_file]))
                sys.exit()
    #check work dir exists
    if "workdir" not in main_config.Config:
        log.error("main_config file is wrong, no workdir in config")
        sys.exit()
    else:
        for work_dir in main_config.Config["workdir"]:
            if not os.path.exists(main_config.Config["workdir"][work_dir]):
                log.error("work dir {} does not exist".format(main_config.Config["workdir"][work_dir]))
                sys.exit()


def main():
    parse_args()
    check_env()


    checkEnv()
    startToWork()

if __name__ == "__main__":
    sys.exit(main())
