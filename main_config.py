#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os 
import datetime

Config ={
    "tool":{
        "aapt": os.path.join(os.getcwd(),"libs","bin","aapt-30.0.1"),
        "apktool": os.path.join(os.getcwd(),"libs","bin","apktool_2.4.0.jar")
        },
    "workfile":{
        #"logging_file": os.path.join(os.getcwd(),"extract_info.json")
    },
    "workdir":{
        "working_folder": os.path.join(os.getcwd(),"working_folder"),
        "tmp_folder": os.path.join(os.getcwd(),"temp"),
        "lib_folder": os.path.join(os.getcwd(),"libs"),
        "apk_folder": os.path.join(os.getcwd(),"apks"),
        "res_output_folder": os.path.join(os.getcwd(),"res_output")
    },
    "market":["huawei"],
    "market_list":["googleplay","apkpure","yandex","uptodown","wandoujia","baidu","360","qq","appchina","eoe","huawei","anzhi","yidong","meizu","xiaomi","lianxiang","kupai","jinli","hiapk","ppzhushou","nduo","mumayi","dianxin","sogou","liqu","zol"],
    "secret_key": "",
    "user_id":"bxmwr91j04t1121c",
    "server_port": 8081,
    "max_query_days":364,
    "max_thread":256,
    "need_to_delete_apk":True,
    "max_request_page_size":100,
    "janus_url":"http://priv.api.appscan.io",
    "apk_query_address":"/apk/query",
    "apk_download_address":"/apk/download",
    "start_date": str(datetime.date.today() - datetime.timedelta(days = 2)),
    "end_date": str(datetime.date.today()- datetime.timedelta(days = 1)),
    "modules": {
        "libs.modules.DCloud.DCloud": "DCloud",
        #"libs.modules.APICloud.APICloud": "APICloud",
        "libs.modules.BSLApp.BSLApp": "BSLApp",
        "libs.modules.Ionic.Ionic": "Ionic",
        "libs.modules.BufanApp.BufanApp": "BufanApp",
        "libs.modules.Cordova.Cordova": "Cordova",
    },
}