#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import abc
import logging
import sys
import hashlib
import subprocess
import json
import os

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

    def _format_working_folder(self, working_folder):
        if os.path.isabs(working_folder):
            extract_folder = os.path.join(working_folder, self.hash)
        else:
            extract_folder = os.path.join(os.getcwd(), working_folder, self.hash)
        return extract_folder

    def _dump_info(self, extract_folder, launch_path):
        info = {"detect_file": self.detect_file, "start_page": launch_path}
        json.dump(info, open(os.path.join(extract_folder, Config.Config["logging_file"]), 'w'))
        return

    # find signature
    def _find_main_activity(self, sig):
        if platform.system() == 'Darwin':
            aapt = Config.Config["aapt"]
        else:
            aapt = Config.Config["aapt_ubuntu"]

        proc = subprocess.Popen("'{}' dump badging '{}'".format(aapt, self.detect_file), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        # e = (proc.communicate()[1]).decode()
        print("'{}' dump badging '{}'".format(Config.Config["aapt"], self.detect_file))
        # print(e)
        if r.find(sig) != -1:
            return True
        return False

    def _gethash(self):
        with open(self.detect_file, "rb") as frh:
            sha1obj = hashlib.sha1()
            sha1obj.update(frh.read())
            return sha1obj.hexdigest()


    def __str__(self):
        return "{} file: {}".format(self.host_os, self.detect_file)

    @abc.abstractmethod
    def doSigCheck(self):
        pass

    @abc.abstractmethod
    def doExtract(self, working_folder):
        pass

