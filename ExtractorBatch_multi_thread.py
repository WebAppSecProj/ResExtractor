#!/usr/bin/env python3
# leverage multi thread to handle extractor batch.
# avoid an apk crash whole extractor


import sys
import Config
import importlib
import logging
import os
import argparse
import libs.Stats as Stats
#import libs.modules.AppCan.AppCan
import threading

import Checker



logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%a %d %b %Y %H:%M:%S')
log = logging.getLogger(__name__)

stats = Stats.Stats()
thread_num_lock = threading.Semaphore(8) #max_thread = 8
stats_lock = threading.Lock()
error_except_file_list = {}
error_lock = threading.Lock()

def doCheck(file_in_check, task_name):

    distill_modules = []
    # load each module
    for k in Config.Config["modules"].keys():
        m = getattr(
            importlib.import_module(k),
            Config.Config["modules"][k]
        )
        # TODO:: verify each module
        if getattr(m, "doSigCheck") and getattr(m, "doExtract"):
            mod_inst = m(file_in_check, "android")
            if mod_inst.doSigCheck():
                if stats_lock.acquire():
                    stats.add_entity(mod_inst.__class__)
                    stats_lock.release()
                logging.info("{} signature Match".format(mod_inst.__class__))
                extract_folder, launch_path = mod_inst.doExtract(os.path.join(Config.Config["working_folder"], task_name, Config.Config["modules"][k]))
                log.info("{} is extracted to {}, the start page is {}".format(file_in_check, extract_folder, launch_path))

    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apk-folder', required=True, help="Folder contains apk files.")
    parser.add_argument('--task-name', required=True, help="Provide name of this task, such that we can classify the analysis result.")

    whole_args = parser.parse_args()

    if Checker.doEnvCheck() == False:
        sys.exit(1)

    sub_thread_list = []

    for dirpath, dirnames, ifilenames in os.walk(whole_args.apk_folder):
        for fs in ifilenames:
            file_in_check = os.path.join(dirpath, fs)
            if not os.path.isfile(file_in_check):
                continue
            log.info(file_in_check)
            sub_thread = threading.Thread(
                    target=_work_thread,
                    args=(file_in_check, whole_args)
                )

            sub_thread_list.append(sub_thread)
            sub_thread.start()
    for tmp_thread in sub_thread_list:
        tmp_thread.join()
    stats.doState()
    #log out all the error method 
    if error_except_file_list != {}:
        log.error("there are some mistakes in handling file ")
        for tmp_path in error_except_file_list:
            log.error("file : {}".format(tmp_path))
            log.error(error_except_file_list[tmp_path])
            log.error("________________________________")

def _work_thread(file_in_check,args):
    
    with thread_num_lock:
        if Checker.doAPKCheck(file_in_check):
            if stats_lock.acquire():
                stats.add_entity()
                stats_lock.release()
            try:
                doCheck(file_in_check, args.task_name)
            except Exception:
                if error_lock.acquire():
                    error_except_file_list[file_in_check] = Exception.__str__()
                    error_lock.release()



if __name__ == "__main__":
    sys.exit(main())
