# 1. WebApp Resource Extractor
Features:
1. Separate the low-code from boilerplate code of web apps.
2. Retrieve remote resource of web apps.
   
Check the supported module list [here](https://github.com/WebAppSecProj/ResExtractor/tree/master/libs/modules). 
And technique report [here](https://webappsecproj.github.io/ResExtractor/).
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
e.g.,
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
e.g.,
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
e.g.,
```
$ python3 Extractor.py --apk-file=/home/demo/Desktop/WebAppSec/ResExtractor/test_case/AppYet/example.apk --task-name=foo
```

## 2.3 To retrieve remote resource

Use the following command to parse local resource and then retrieve the remote resource.
```buildoutcfg
# usage: RemoteExtractor.py [-h] --task-name TASK_NAME

optional arguments:
  -h, --help            show this help message and exit
  --task-name TASK_NAME
                        Provide name of the task, such that we can reach the
                        local resource.
```
e.g.,
```
$ python3 RemoteExtractor.py --task-name="xingyuan.2020.01.05"
```

## 2.4 To retrieve snapshot
Follow the [instruction](https://github.com/WebAppSecProj/RemovePermissionGrant) to build your own rom firstly.  
Then use `SnapShotExtractor.py` to retrieve snapshot. The results reside in `working_folder/snapshot`
```commandline
$usage: SnapShotExtractor.py [-h] --apk-folder APK_FOLDER

optional arguments:
  -h, --help            show this help message and exit
  --apk-folder APK_FOLDER
                        Folder contains apk files.
```
e.g., 
```commandline
python3 SnapShotExtractor.py --apk-folder="/Users/panmac/Desktop/workspace/WebAppSecProj/sample/xingyuan/2021-01-14"
```
                        
## 2.5 layout of the folder
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
├─screenshot
│  ├─hash~of~app.png
```

# 3. Applications

## 3.1 Screen shot similarity analysis

```commandline
$ usage: ScreenShotSimilarity.py [-h] [--img-folder IMG_FOLDER]
                               [--img-file IMG_FILE] --db-file DB_FILE
                               [--DEBUG DEBUG]

optional arguments:
  -h, --help            show this help message and exit
  --img-folder IMG_FOLDER
                        Folder contains img files.
  --img-file IMG_FILE   img file for searching.
  --db-file DB_FILE     db file for preserving keypoint of images.
  --DEBUG DEBUG         show designate number of similar img.
```
There are 2 steps to lunch screen shot similarity analysis.
1. build database containing keypoint of all images. e.g., 
```commandline
$ python3 ScreenShotSimilarity.py --img-folder="working_folder/snapshot" --db-file="Applications/ScreenShotSimilarity/All.pkl"
```
2. search similar img, you can use `--DEBUG` argument for observing the analysis result. e.g., 
```commandline
$ python3 ScreenShotSimilarity.py --img-file="working_folder/snapshot/3eca26b5485de89b2f122634d51a7dbd9c50af19.png" --db-file="Applications/ScreenShotSimilarity/All.pkl" --DEBUG=10
```
also, you can use them all such that the built db file can be used next time.
e.g.,
```commandline
$ python3 ScreenShotSimilarity.py --img-folder="working_folder/snapshot" --img-file="working_folder/snapshot/3eca26b5485de89b2f122634d51a7dbd9c50af19.png" --db-file="Applications/ScreenShotSimilarity/All.pkl" --DEBUG=10
```
Also, you can use:
```commandline
$ ScreenShotSimilarityCluster.py [-h] [--img-folder IMG_FOLDER] --db-file
                                      DB_FILE [--sim-threshold SIM_THRESHOLD]

optional arguments:
  -h, --help            show this help message and exit
  --img-folder IMG_FOLDER
                        Folder contains img files.
  --db-file DB_FILE     db file for preserving keypoint of images.
  --sim-threshold SIM_THRESHOLD
                        similarity threshold.
```

e.g., 
```commandline
$ python3 ScreenShotSimilarityBatch.py --img-folder="working_folder/snapshot" --db-file="Applications/ScreenShotSimilarity/screenshot.pkl" --sim-threshold=0.3
```

## 3.2 HTML similarity analysis

```commandline
$ usage: HTMLSimilarity.py [-h] [--html-folder HTML_FOLDER]
                         [--html-file HTML_FILE] --db-file DB_FILE

optional arguments:
  -h, --help            show this help message and exit
  --html-folder HTML_FOLDER
                        Folder containing html files.
  --html-file HTML_FILE
                        html file for searching.
  --db-file DB_FILE     db file for preserving eigenvector of html files.
```
There are 2 steps to lunch html similarity analysis.
1. build database containing eigenvector of all html files. e.g., 
```commandline
$ python3 HTMLSimilarity.py --html-folder="working_folder" --db-file="Applications/HTMLSimilarity/All.pkl"
```
2. search similar html file. e.g., 
```commandline
$ python3 HTMLSimilarity.py --html-file="/Users/panmac/Desktop/workspace/WebAppSecProj/ResExtractor/working_folder/yingyuan.2021.01.12/APICloud/882f9292700f68b221f7716b7bceec9b50b1892f/localres/widget/error/error.html" --db-file="Applications/HTMLSimilarity/All.pkl"
```
also, you can use them all such that the built db file can be used later.
e.g.,
```commandline
$ python3 HTMLSimilarity.py --html-folder="working_folder" --html-file="/Users/panmac/Desktop/workspace/WebAppSecProj/ResExtractor/working_folder/yingyuan.2021.01.12/APICloud/882f9292700f68b221f7716b7bceec9b50b1892f/localres/widget/error/error.html" --db-file="Applications/HTMLSimilarity/All.pkl"
```

## 3.3 Web resource monitor

## 3.4 Grayware classification




# A1. HOWTO Debug
1. Use ExtractorJanus.py and keep all apk files (set `need_to_delete_apk' flag to True)
2. Use ExtractorBatch.py to find bugs and then fix them.
