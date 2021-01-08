#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
common config, app specific configuration should reside in related module.
'''

import collections

Config = {
    "aapt_osx": "./libs/bin/aapt2-osx",
    "aapt_linux": "./libs/bin/aapt2-linux",
    "apktool": "./libs/bin/apktool_2.4.0.jar",

    "decrypt_jar": "./libs/bin/ResDecode.jar",

    "working_folder": "working_folder",
    "local_res_folder": "localres",
    "local_res_info": "local_res_info.json",
    "remote_res_folder": "remoteres",
    "remote_res_info": "remote_res_info.csv",
    "filtered_remote_res_info": "filtered_remote_res_info.csv",

    "log_folder": "Logger",

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
        # enable this module until the problem solved
        ("libs.modules.AppYet.AppYet", "AppYet"),
        ("libs.modules.Ofcms.Ofcms", "Ofcms"),
        ("libs.modules.NativeScript.NativeScript", "NativeScript"),
        ("libs.modules.GoodBarber.GoodBarber", "GoodBarber"),
        # should put the low-level boilerplate framework at the end of this list
        ("libs.modules.Ionic.Ionic", "Ionic"),
        ("libs.modules.Cordova.Cordova", "Cordova"),
        ("libs.modules.YunDaBao.YunDaBao", "YunDaBao"),
    ]),

}
