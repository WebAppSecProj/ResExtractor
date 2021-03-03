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
import re

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
        proc = subprocess.Popen(
            "java -jar '{}' d '{}' -f -o '{}'".format(Config.Config["apktool"], self.detect_file, extract_folder),
            shell=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        # log.info(r)

        return

    def _apktool_no_decode_source(self, extract_folder):
        proc = subprocess.Popen(
            "java -jar '{}' d '{}' -f -s -o '{}'".format(Config.Config["apktool"], self.detect_file, extract_folder),
            shell=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        # log.info(r)

        return

    def _format_working_folder(self, working_folder):
        if os.path.isabs(working_folder):
            extract_folder = os.path.join(working_folder, self.hash, Config.Config["local_res_folder"])
        else:
            extract_folder = os.path.join(os.getcwd(), working_folder, self.hash, Config.Config["local_res_folder"])
        return extract_folder

    def _dump_info(self, extract_folder, launch_path):
        info = {"detect_file": self.detect_file, "start_page": launch_path}
        json.dump(info, open(os.path.join(extract_folder, Config.Config["local_res_info"]), 'w', encoding='utf-8'),
                  ensure_ascii=False)
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
        proc = subprocess.Popen("'{}' dump badging '{}'".format(self._aapt(), self.detect_file), shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        # e = (proc.communicate()[1]).decode()
        # print("'{}' dump badging '{}'".format(Config.Config["aapt"], self.detect_file))
        # print(e)
        if r.find(sig) != -1:
            return True
        return False

    def _get_main_activity(self):
        proc = subprocess.Popen("'{}' dump badging '{}'".format(self._aapt(), self.detect_file), shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        regex = "launchable-activity: name='(.+?)'"
        main_activity = re.findall(regex, r)
        return main_activity[0]

    def _gethash(self):
        with open(self.detect_file, "rb") as frh:
            sha1obj = hashlib.sha1()
            sha1obj.update(frh.read())
            return sha1obj.hexdigest()

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
