# 1. WebApp Resource Extractor
Features:
1. Separate the low-code from boilerplate code of web apps.
2. Retrieve remote resource of web apps.
   
Check the supported module list [here](https://github.com/WebAppSecProj/ResExtractor/tree/master/libs/modules). 
And technique report [here](ttps://webappsecproj.github.io/ResExtractor/).
# 2. Get started
## 2.1 Prerequisites
```
$ git clone --recurse-submodules https://github.com/WebAppSecProj/ResExtractor.git
$ cd ResExtractor
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

## 2.2 3 ways to extract the low-code
I. Use the following command to retrieve and parse apk files from [janus](https://www.appscan.io).
```
$ usage: ExtractorJanus.py [-h] --secret-key SECRET_KEY
                         [--target-date TARGET_DATE] [--start-date START_DATE]
                         [--end-date END_DATE] [--market MARKET]
                         [--show-market] --task-name TASK_NAME

optional arguments:
  -h, --help            show this help message and exit
  --secret-key SECRET_KEY
                        Secret key for connecting janus.
  --target-date TARGET_DATE
                        Target date to query, default date is yesterday, a
                        query period exceeding 364 days is not allowed.
  --start-date START_DATE
                        Start date of the query.
  --end-date END_DATE   End date of the query.
  --market MARKET       APP market in query. Huawei APP market is set if no
                        argument supplemented; Use `,' to split multiple
                        markets; Use `all' to query all markets.
  --show-market         To list supported APP markets.
  --task-name TASK_NAME
                        Provide name of this task, such that we can classify
                        the analysis result.
```
e.g., :
```
$ python3 ExtractorJanus.py --secret-key=123456 --start-date=2020-10-01 --end-date=2020-10-02 --task-name=janus.2020.10.01-2020.10.02
```
II. use a bunch of local apk files for extracting.
```
$ usage: ExtractorBatch.py [-h] --apk-folder APK_FOLDER --task-name TASK_NAME

optional arguments:
  -h, --help            show this help message and exit
  --apk-folder APK_FOLDER
                        Folder contains apk files.
  --task-name TASK_NAME
                        Provide name of this task, such that we can classify
                        the analysis result.
```
e.g., :
```
python3 ExtractorBatch.py --apk-folder="/home/demo/Desktop/sample/xingyuan/2021-01-04" --task-name="xingyuan.2020.01.05"
```

III. to process a single instance.
```
$ usage: Extractor.py [-h] --apk-file APK_FILE --task-name TASK_NAME

optional arguments:
  -h, --help            show this help message and exit
  --apk-file APK_FILE   The apk file.
  --task-name TASK_NAME
                        Provide name of this task, such that we can classify
                        the analysis result.
```
e.g., :
```
$ python3 Extractor.py --apk-file=/home/demo/Desktop/WebAppSec/ResExtractor/test_case/AppYet/example.apk --task-name=foo
```

## 2.2 To retrieve remote resource

Use the following command to parse local resource and then retrieve the remote resource.
```buildoutcfg
# usage: RemoteExtractor.py [-h] --task-name TASK_NAME

optional arguments:
  -h, --help            show this help message and exit
  --task-name TASK_NAME
                        Provide name of the task, such that we can reach the
                        local resource.
```
e.g., :
```
$ python3 RemoteExtractor.py --task-name="xingyuan.2020.01.05"
```
                        
## 2.3 layout of the folder
```python
├─working folder
│  ├─task name
│  │  ├─module name  
│  │  │  ├─00a95f0e62afc81ec6a138d5b5c4c16607d2d3e8 (hash of the app)  
│  │  │  │  ├─localres
│  │  │  │  |  ├─local_res_info.json
│  │  │  │  |  ├─local res 
│  │  │  │  ├─remoteres
│  │  │  │  |  ├─remote_res_info.csv 
│  │  │  │  │  ├─date1 
│  │  │  │  │  │  ├─url1
│  │  │  │  │  │  │  ├─remote res 
│  │  │  │  │  │  ├─url2
│  │  │  │  │  │  │  ├─remote res 
│  │  │  │  │  ├─date2
│  │  │  │  │  │  ├─url3  
│  │  │  │  │  │  │  ├─remote res 
│  │  │  │  │  │  ├─url4
│  │  │  │  │  │  │  ├─remote res 
│  │  │  │  ├─screenshot
```

# 3. Applications

## 3.1 Web resource monitor

## 3.2 Grayware classification

## 3.3 Web resource similarity analysis

## 3.4 Screen shot similarity analysis


# A1. HOWTO Debug
1. Use ExtractorJanus.py and keep all apk files (set `need_to_delete_apk' flag to True)
2. Use ExtractorBatch.py to find bugs and then fix them.
