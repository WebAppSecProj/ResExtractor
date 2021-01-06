# WebApp Resource Extractor

For separating the low-code from boilerplate code of web apps.  
Check the Module list [here](https://github.com/WebAppSecProj/ResExtractor/tree/master/libs/modules). 


# HOWTO Use

```
$ git clone --recurse-submodules https://github.com/WebAppSecProj/ResExtractor.git
$ cd ResExtractor
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

## 3 ways to extract the low-code
1. Use the following command to retrieve and parse apk files from [janus](https://www.appscan.io).
```
$ usage: ExtractorJanus.py [-h] --secret-key SECRET_KEY [--target-date TARGET_DATE]
               [--start-date START_DATE] [--end-date END_DATE]
               [--market MARKET] [--show-market]

optional arguments:
  -h, --help            show this help message and exit
  --secret-key SECRET_KEY
                        Secret key for connecting janus.
  --target-date TARGET_DATE
                        Target date to query, default is yesterday, a query
                        period exceeding 364 days is not allowed.
  --start-date START_DATE
                        Start date of the query.
  --end-date END_DATE   End date of the query.
  --market MARKET       APP market in query. Huawei APP market is set if no
                        argument supplemented; Use `,' to split multiple
                        markets; Use `all' to query all markets.
  --show-market         To list supported APP markets.
```
e.g., :
```
$ python3 ExtractorJanus.py --secret-key=123456 --start-date=2020-10-01 --end-date=2020-10-02
```
2. use a bunch of local apk files for analyzing.
```
$ python3 ExtractorBatch.py path_to_the_directory
```
3. to process a single instance.
```
$ python3 Extractor.py path_to_the_file
```

# layout of the folder
```python
├─working folder
│  ├─task name
│  │  ├─module name  
│  │  │  ├─00a95f0e62afc81ec6a138d5b5c4c16607d2d3e8 (hash of app)  
│  │  │  │  ├─local res 
│  │  │  │  ├─date1 
│  │  │  │  │  ├─aaa95f0e62afc81ec6a138d5b5c4c16607d2d3e8 (hash of url1) 
│  │  │  │  │  │  ├─remote res 
│  │  │  │  │  ├─bba95f0e62afc81ec6a138d5b5c4c16607d2d3e8 (hash of url2)
│  │  │  │  │  │  ├─remote res 
│  │  │  │  ├─date2
│  │  │  │  │  ├─aaa95f0e62afc81ec6a138d5b5c4c16607d2d3e8 (hash of url1)  
│  │  │  │  │  │  ├─remote res 
│  │  │  │  │  ├─bba95f0e62afc81ec6a138d5b5c4c16607d2d3e8 (hash of url2)
│  │  │  │  │  │  ├─remote res 
```

# HOWTO Debug
1. Use ExtractorJanus.py and keep all apk files (set `need_to_delete_apk' flag to True)
2. Use ExtractorBatch.py to find bugs and then fix them.
