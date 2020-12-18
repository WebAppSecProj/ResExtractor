import os 
import sys 
import main_config
import logging
import datetime
import _thread
import threading
import requests
import importlib
import argparse

from libs.downloader.AndroidApplicationDownloader import AndroidApplicationDownloader
logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

def checkPythonVersion():
    log.info("start to check python version")
    if sys.version_info.major<3:
        log.error("python version should > 3")
        sys.exit()
    
def checkExist():
    #check tool exists
    if "tool" not in main_config.Config:
        log.error("main_config file is wrong, no tool in config")
        sys.exit()
    #if no need to exit then just delete sys.exit()
    else:
        for tar_tool in main_config.Config["tool"]:
            if not os.path.exists(main_config.Config["tool"][tar_tool]):
                log.error("tool {} does not exist".format(main_config.Config["tool"][tar_tool]))
                sys.exit()
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

def checkTargetDateInQueryRange(target_date):
    today = datetime.date.today()
    if (target_date > today):
        log.error("cannot query future date")
        sys.exit()
    if ((target_date - today).days > main_config.Config["max_query_days"]):
        log.error("query too long till today")
        sys.exit()

def checkAndSetDate(start_date_str, end_date_str):
    if (start_date_str == None) & (end_date_str == None):
        return 
    if (start_date_str == None):
        log.error("if you set end date, you must set start date")
        sys.exit()
    if (end_date_str == None):
        log.error("if you set start date, you must set end date")
        sys.exit()
    try:
        start_date = datetime.datetime.strptime(start_date_str,"%Y-%M-%d")
    except ValueError:
        log.error("date format for --start-date is wrong, sholuld be year-month-day")
        sys.exit()
    
    try:
        end_date = datetime.datetime.strptime(end_date_str,"%Y-%M-%d")
    except ValueError:
        log.error("date format for --end-date is wrong, sholuld be year-month-day")
        sys.exit()

    if start_date>end_date:
        log.error("start date must be erlier than end date")
        sys.exit()
    
    main_config.Config["start_date"] = start_date_str
    main_config.Config["end_date"] = end_date_str
        
    

def parseArgs():
    start_date_str = None
    end_date_str = None

    parser = argparse.ArgumentParser()
    parser.add_argument('--secret-key', required=True, help="Secret key for connecting janus.")
    parser.add_argument('--target-date', help="Target date to query, default is yesterday, a query period exceeding {} days is not allowed.".format(main_config.Config["max_query_days"]))
    parser.add_argument('--start-date', help="Start date of the query.")
    parser.add_argument('--end-date', help="End date of the query.")
    parser.add_argument('--market', type=str, help="APP market in query. Huawei APP market is set if no argument supplemented; Use `,' to split multiple markets; Use `all' to query all markets.")
    parser.add_argument('--show-market', action='store_true', help="To list supported APP markets.")

    args = parser.parse_args()
    main_config.Config["secret_key"] = args.secret_key

    if args.target_date and (args.start_date or args.end_date):
        log.error("overlapping data setting")
        sys.exit()

    if args.target_date:
        try:
            target_date = datetime.datetime.strptime(args.target_date,"%Y-%M-%d")
        except ValueError:
            log.error("date format for --target-date is wrong, sholuld be year-month-day")
            sys.exit()
        checkTargetDateInQueryRange(target_date.date())
        checkTargetDateInQueryRange(target_date.date() - datetime.timedelta(days = 1))
        main_config.Config["end_date"] = args.target_date
        main_config.Config["start_date"] = target_date.date() - datetime.timedelta(days = 1)

    if args.show_market:
        print("market list:")
        print("{}".format(main_config.Config["market_list"]))
        sys.exit()
    if args.market:
        main_config.Config["market"] = []
        lst_market = args.market.split(",")

        if "all" in lst_market:
            main_config.Config["market"]=main_config.Config["market_list"]
        for tmp_market in lst_market:
            if tmp_market not in main_config.Config["market_list"]:
                print("market {} not in market list, use --show-market to show the market list ".format(tmp_market))
                sys.exit()
            main_config.Config["market"].append(tmp_market)
        if main_config.Config["market"] == []:
            log.error("no market is choosen")
            sys.exit()
    else:
        main_config.Config["market"].append("huawei")

    if args.start_date and args.end_date:
        start_date_str = args.start_date
        end_date_str = args.end_date
        checkAndSetDate(start_date_str, end_date_str)
    elif args.start_date or args.end_date:
        log.error("provide target-date and end-date in a pair.")
        sys.exit()

def checkEnv():
    checkPythonVersion()
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
    




def main():


    parseArgs()
    checkEnv()
    startToWork()



if __name__ == "__main__":
    main()