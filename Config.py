#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
common config, app specific configuration should reside in related module.
'''

import collections

Config = {
    "aapt_osx": "./libs/bin/aapt2-osx",
    "aapt_linux": "./libs/bin/aapt2-linux",
    "aapt_windows": "./libs/bin/aapt2-windows.exe",

    "apktool": "./libs/bin/apktool_2.4.0.jar",

    "decrypt_jar": "./libs/bin/ResDecode.jar",

    "working_folder": "working_folder",
    "snapshot_folder": "snapshot",

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
        ("libs.modules.SeattleCloud.SeattleCloud", "SeattleCloud"),
        ("libs.modules.Biznessapps.Biznessapps", "Biznessapps"),
        ("libs.modules.yunedit.yunedit", "yunedit"),
        ("libs.modules.apkeditor.apkeditor", "apkeditor"),
        ("libs.modules.AppPark.AppPark", "AppPark"),
        ("libs.modules.yimen.yimen", "yimen"),
        ("libs.modules.Mobincube.Mobincube", "Mobincube"),
        ("libs.modules.MobileRoadie.MobileRoadie", "MobileRoadie"),
        # there are some quirks when using jvm to load different modules.
        # https://jpype.readthedocs.io/en/latest/install.html#known-bugs-limitations
        # enable this module until the problem solved
        ("libs.modules.AppYet.AppYet", "AppYet"),
        ("libs.modules.Ofcms.Ofcms", "Ofcms"),
        ("libs.modules.NativeScript.NativeScript", "NativeScript"),
        ("libs.modules.GoodBarber.GoodBarber", "GoodBarber"),
        ("libs.modules.YunDaBao.YunDaBao", "YunDaBao"),
        ("libs.modules.Ionic.Ionic", "Ionic"),
        ("libs.modules.Appmakr.Appmakr", "Appmakr"),
        ("libs.modules.appery.appery", "appery"),
        # should put the low-level boilerplate framework at the end of this list
        ("libs.modules.Cordova.Cordova", "Cordova"),
        ("libs.modules.AppMachine.AppMachine", "AppMachine"),
    ]),

}
