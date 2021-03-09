import os 
import sys 
import time
import datetime
import logging
import threading
import requests
import importlib
import argparse
import json
import random
import hashlib
from contextlib import closing

from Config import Config
import Checker
import libs.Stats as Stats
import csv

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

stats = Stats.Stats()

JanusConfig = {
    "janus_output_dir": Config["log_folder"],
    "file_list_info_logger": os.path.join(Config["log_folder"], "janus_file_list_info.txt"),
    "apk_folder": os.path.join(Config["log_folder"], "apks"),
    "size_threshold": 100,      # the threshold of the apk file, file size over this quota will not be downloaded.
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
    "start_date": str(datetime.date.today() - datetime.timedelta(days=1)),
    "end_date": str(datetime.date.today() - datetime.timedelta(days=1)),
}


def log_error(module, file, msg):
    log_file = os.path.join(Config["log_folder"], "JanusError.csv")
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


'''
I do not know why we use a class :(
anyway, that's not important
'''
class DownloadAndExtract:

    def __init__(self, JConfig):
        self._secret_key = JConfig["secret_key"]
        self._user_id = JConfig["user_id"]
        self._thread_num_lock = threading.Semaphore(JConfig["max_thread"])
        self._file_list_info_logger = JConfig["file_list_info_logger"]
        self._apk_folder = JConfig["apk_folder"]
        self._janus_url = JConfig["janus_url"]
        self._apk_query_address = JConfig["apk_query_address"]
        self._apk_download_address = JConfig["apk_download_address"]
        self._start_date = JConfig["start_date"]
        self._end_date = JConfig["end_date"]
        self._market = JConfig["market"]
        self._max_request_page_size = JConfig["max_request_page_size"]
        self._need_to_delete_apk = JConfig["need_to_delete_apk"]
        self._result_write_lock = threading.Lock()

    def _generate_nonce(self):
        return "".join(random.sample("abcdefghijklmnopqrstuvwxyz!@#$%^&*()", random.randint(5, 30)))

    def _generate_sign(self, request_content):
        sign = hashlib.md5(
            ("".join([str(request_content[i]) for i in sorted(request_content.keys())]) + self._secret_key).encode(
                "utf-8")).hexdigest()

        return sign

    def _generate_query(self, cur_date):
        query_str = "stime:\"{}\" and etime:\"{}\" and market:\"{}\"".format(cur_date,
                                                                             cur_date,
                                                                             ",".join(self._market))
        return query_str

    def _query_app_list(self, cur_date):

        request_content = {}
        target_application_sha1_list = {}

        request_content["userid"] = self._user_id
        request_content["nonce"] = self._generate_nonce()
        request_content["time"] = str(int(time.time()))
        request_content["version"] = "1.0"
        request_content["query"] = self._generate_query(cur_date)
        request_content["pagesize"] = self._max_request_page_size
        request_content["sign"] = self._generate_sign(request_content)

        list_request_json = json.dumps(request_content)
        log.info("list request: {}".format(list_request_json))
        result_json = requests.post(self._janus_url + self._apk_query_address,
                                    data=list_request_json)
        result_content = json.loads(result_json.text)
        log.info("list response: {}".format(result_content))
        time.sleep(1.5)

        if ("status" not in result_content) \
            or (result_content["status"] != 200):
            log.error("retrieving app list error: {}".format(result_json))
            sys.exit(1)

        # just one page?
        if 'paging' not in result_content:
            if "data" not in result_content:
                log.error("query nothing from janus, result data: {}".format(result_content))
                sys.exit(1)
            for tmp_app in result_content["data"]:
                if ("sha1" not in tmp_app) | ("name" not in tmp_app):
                    log.error("no sha1 in request response: {}".format(tmp_app))
                    sys.exit(1)
                target_application_sha1_list[tmp_app["sha1"]] = {
                    "name": tmp_app["name"],
                    "appid": tmp_app["appid"],
                    "size": tmp_app["size"]
                }
            return target_application_sha1_list


        if "page_total" not in result_content["paging"]:
            log.error("no page_total in response: {}".format(result_json))
            sys.exit(1)
        page_total = result_content["paging"]["page_total"]

        if page_total > 100:
            log.error("response over 100 pages, reset to 100")
            page_total = 100

        for cur_page in range(1, page_total + 1):
            request_content = {}
            request_content["userid"] = self._user_id
            request_content["nonce"] = self._generate_nonce()
            request_content["time"] = str(int(time.time()))
            request_content["version"] = "1.0"
            request_content["query"] = self._generate_query(cur_date)
            request_content["pagesize"] = self._max_request_page_size
            request_content["page"] = cur_page          # add an additional arg
            request_content["sign"] = self._generate_sign(request_content)

            application_request_json = json.dumps(request_content)
            result_json = requests.post(self._janus_url + self._apk_query_address,
                                        data=application_request_json)
            result_content = json.loads(result_json.text)
            log.info("page list request result: {}".format(result_content))

            if "data" not in result_content:
                log.error("get nothing from janus, response: {}".format(result_content))
                sys.exit(1)
            for tmp_app in result_content["data"]:
                if ("sha1" not in tmp_app) | ("name" not in tmp_app):
                    log.error("no sha1 in response: {}".format(tmp_app))
                    sys.exit(1)
                # if target_application_sha1_list.__contains__(tmp_app["sha1"]):
                #     log.info("duplicate sha1")
                target_application_sha1_list[tmp_app["sha1"]] = {
                    "name": tmp_app["name"],
                    "appid": tmp_app["appid"],
                    "size": tmp_app["size"]
                }

            time.sleep(1.5)

        # log.info(request_content)
        # log.info(request_json)

        return target_application_sha1_list

    def _work_thread(self, tar_app_sha1, tar_app_info, cur_date, index, total):
        with self._thread_num_lock:

            log.info("{}: {}/{}: processing {}".format(cur_date, index, total, tar_app_sha1))

            tar_apk_path = os.path.join(self._apk_folder, tar_app_sha1 + ".apk")

            try:
                r = requests.get(url=tar_app_info["download"], verify=False, stream=True)
            except:
                log.error("[1] download error: {}".format(tar_app_sha1))
                return

            if r.status_code != 200:
                log.error("[2] download error: {}".format(tar_app_sha1))
                return

            with closing(r) as res:
                with open(tar_apk_path, 'wb') as fd:
                    for chunk in res.iter_content(chunk_size=10*1024*1024):
                        if chunk:
                            fd.write(chunk)
                    fd.flush()

            new_apk_file = Checker.doAPKCheck(tar_apk_path)
            if new_apk_file == False:
                return

            stats.add_entity()
            for to_check_module_name in Config["modules"]:
                target_framework_check_class = getattr(importlib.import_module(to_check_module_name),
                                                       Config["modules"][to_check_module_name])
                target_check = target_framework_check_class(new_apk_file, "android")
                if target_check.doSigCheck():

                    log.info("module {} found in this application".format(Config["modules"][to_check_module_name]))
                    stats.add_entity(target_check.__class__)

                    tar_module_folder = os.path.join(os.getcwd(), Config["working_folder"], Config["task_name"],
                                                     Config["modules"][to_check_module_name])
                    if not os.path.exists(tar_module_folder):
                        os.makedirs(tar_module_folder)

                    tar_extract_folder = os.path.join(tar_module_folder, tar_app_sha1)
                    if not os.path.exists(tar_extract_folder):
                        os.makedirs(tar_extract_folder)

                    try:
                        target_check.doExtract(tar_module_folder)
                    except:
                        log_error(target_check.__class__, tar_app_sha1, "doExtract")
                        log.error("process error: {}".format(tar_app_sha1))
                        # exit(0)
                        continue
                    # extract_info.json
                    extract_info_path = os.path.join(tar_extract_folder, tar_app_sha1, Config["local_res_info"])
                    if os.path.exists(extract_info_path):
                        extract_info_file = open(extract_info_path, "r")
                        result = json.load(extract_info_file)
                        result["apkname"] = tar_app_info["name"]
                        result["apksha1"] = tar_app_sha1
                        result["modulename"] = Config["modules"][to_check_module_name]
                        extract_info_file.close()
                        json.dump(result, open(extract_info_path, "w", encoding='utf-8'), ensure_ascii=False)

                    # write apk name and its module to file
                    if self._result_write_lock.acquire():
                        tmp_file = open(self._file_list_info_logger, "a")
                        tmp_file.write("apk: {} sha1 {} module : {} \n".format(tar_app_info["name"],
                                                                               tar_app_sha1,
                                                                               Config["modules"][to_check_module_name]))
                        tmp_file.close()
                        self._result_write_lock.release()

                # del(to_check_module_name)

            # else:
            # log.info("module {} sig not in this application".format(main_config.Config["modules"][to_check_module_name]))

            if self._need_to_delete_apk:
                os.remove(new_apk_file)

    def doDownloadAndExtract(self):

        # janus return 100 pages in total per query.
        # so I split the query into day.
        format_end_date = datetime.datetime.strptime(self._end_date, "%Y-%m-%d")
        format_cur_date = datetime.datetime.strptime(self._start_date, "%Y-%m-%d")

        while format_cur_date <= format_end_date:
            cur_date = datetime.datetime.strftime(format_cur_date, '%Y-%m-%d')

            app_sha1_list = self._query_app_list(cur_date)

            sub_thread_list = []
            counter = 0

            for tmp_sha1 in app_sha1_list:
                counter += 1

                if app_sha1_list[tmp_sha1]["size"] > JanusConfig["size_threshold"] * 1024 * 1024:
                    log.info("file: {} exceeds the quota, process the next one".format(tmp_sha1))
                    continue

                download_request_content = {}
                download_request_content["userid"] = self._user_id
                download_request_content["nonce"] = self._generate_nonce()
                download_request_content["time"] = str(int(time.time()))
                download_request_content["version"] = "1.0"
                download_request_content["sha1"] = tmp_sha1
                download_request_content["sign"] = self._generate_sign(download_request_content)

                request_json = json.dumps(download_request_content)
                try:
                    result_json = requests.post(self._janus_url + self._apk_download_address,
                                                data=request_json)
                except:
                    log.error("[1] can't retrieve download address of {}".format(tmp_sha1))
                    continue

                try:
                    result_content = json.loads(result_json.text)
                except:
                    log.error("[2] can't retrieve download address of {}".format(tmp_sha1))
                    continue

                # log.info("download url : {}".format(request_json))
                # log.info("download result : {}".format(result_content))

                if ("status" not in result_content) \
                        or (result_content["status"] != 200) \
                        or ("download_url" not in result_content):
                    log.error("[3] can't retrieve download address of {}".format(
                        app_sha1_list[tmp_sha1]["name"]))
                    continue

                app_sha1_list[tmp_sha1]["download"] = result_content["download_url"]

                sub_thread = threading.Thread(
                    target=self._work_thread,
                    args=(tmp_sha1, app_sha1_list[tmp_sha1], cur_date, counter, len(app_sha1_list))
                )

                sub_thread_list.append(sub_thread)
                sub_thread.start()
                # janus allows 40 queries per minute
                time.sleep(2)

            for tmp_sub_thread in sub_thread_list:
                tmp_sub_thread.join()

            # move to the next day
            format_cur_date += datetime.timedelta(days=1)


# check the validation of the query
def check_target_date_in_range(target_date):
    today = datetime.date.today()
    if (target_date > today):
        log.error("oops! reset the data {}".format(target_date))
        sys.exit()
    if ((target_date - today).days > JanusConfig["max_query_days"]):
        log.error("allow query across {} days".format(JanusConfig["max_query_days"]))
        sys.exit()


def go():
    download_and_extract = DownloadAndExtract(JanusConfig)
    #target_date_application_list = apk_downloader.queryTargetDateApplications()
    download_and_extract.doDownloadAndExtract()

# parse the argument
def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--secret-key', required=True, help="Secret key for connecting janus.")
    parser.add_argument('--target-date', help="Target date to query, default date is yesterday, a query period exceeding {} days is not allowed.".format(JanusConfig["max_query_days"]))
    parser.add_argument('--start-date', help="Start date of the query.")
    parser.add_argument('--end-date', help="End date of the query.")
    parser.add_argument('--market', type=str, help="APP market in query. Huawei APP market is set if no argument supplemented; Use `,' to split multiple markets; Use `all' to query all markets.")
    parser.add_argument('--show-market', action='store_true', help="To list supported APP markets.")
    parser.add_argument('--task-name', required=True, help="Provide name of this task, such that we can classify the analysis result.")

    args = parser.parse_args()
    JanusConfig["secret_key"] = args.secret_key

    Config["task_name"] = args.task_name

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

        check_target_date_in_range(format_target_date.date())
        check_target_date_in_range(format_target_date.date() - datetime.timedelta(days = 1))

        JanusConfig["end_date"] = args.target_date
        JanusConfig["start_date"] = datetime.datetime.strftime(format_target_date.date() - datetime.timedelta(days = 1),'%Y-%m-%d')


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
        check_target_date_in_range(datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date())
        check_target_date_in_range(datetime.datetime.strptime(args.end_date, "%Y-%m-%d").date())

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
    if Checker.doEnvCheck() == False:
        sys.exit(1)

    if not os.access(JanusConfig["janus_output_dir"], os.R_OK):
        os.makedirs(JanusConfig["janus_output_dir"], exist_ok=True)

    # ensure logger file exist
    if not os.access(JanusConfig["file_list_info_logger"], os.R_OK):
        open(JanusConfig["file_list_info_logger"], 'w').close()

    # ensure the folder exist
    if not os.access(JanusConfig["apk_folder"], os.R_OK):
        os.makedirs(JanusConfig["apk_folder"], exist_ok=True)

def main():
    parse_args()
    check_env()
    go()
    stats.doState()

if __name__ == "__main__":
    sys.exit(main())
