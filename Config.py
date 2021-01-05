#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
common config, app specific configuration should reside in related module.
'''

import collections

Config = {
    "aapt": "./libs/bin/aapt-30.0.1",
    "aapt_ubuntu": "./libs/bin/ubuntu_aapt",
    "apktool": "./libs/bin/apktool_2.4.0.jar",
    "logging_file": "extract_info.json",
    "working_folder": "working_folder",
    "server_port": 8081,
    "modules": collections.OrderedDict([
        ("libs.modules.DCloud.DCloud", "DCloud"),
        ("libs.modules.APICloud.APICloud", "APICloud"),
        ("libs.modules.BSLApp.BSLApp", "BSLApp"),
        ("libs.modules.BufanApp.BufanApp", "BufanApp"),
        ("libs.modules.AppCan.AppCan", "AppCan"),
        ("libs.modules.Trigger.Trigger", "Trigger"),
        ("libs.modules.OnsenUI.OnsenUI", "OnsenUI"),
        ("libs.modules.Andromo.Andromo", "Andromo"),
        ("libs.modules.AppsGeyser.AppsGeyser", "AppsGeyser"),
        ("libs.modules.AppInventor.AppInventor", "AppInventor"),
        # there are some quirks when using jvm to load different modules.
        # https://jpype.readthedocs.io/en/latest/install.html#known-bugs-limitations
        # add this module until the problem solved
        # ("libs.modules.AppYet.AppYet", "AppYet"),
        ("libs.modules.Ofcms.Ofcms", "Ofcms"),
        # should put the low-level boilerplate framework at the end of this list
        ("libs.modules.Ionic.Ionic", "Ionic"),
        ("libs.modules.Cordova.Cordova", "Cordova"),
        ("libs.modules.NativeScript.NativeScript", "NativeScript"),
    ]),
}
