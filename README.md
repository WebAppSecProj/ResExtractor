# WebApp Resource Extractor

For separating the low-code from boilerplate code of web apps.  
Check the Module list [here](https://github.com/WebAppSecProj/ResExtractor/tree/master/libs/modules). 


# HOWTO Use

```
$ git clone --recurse-submodules https://github.com/WebAppSecProj/ResExtractor.git
$ virtualenv -p python3 venv
$ cd ResExtractor
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```
In one thread, use the following command to parse apk files from [janus](https://www.appscan.io).
```
$ python3 main.py --secret-key=[secret key for connect to janus]
        		  --target-date=[target date to query, default yesturday, ]
        		  --start-date=[start date toquery, must be with end date. cover target-date]
        		  --end-date=[end date toquery, must be with start date. cover target-date]
        		  --market=[target market to query, default huawei,use , to split market; no blank space ; all means all market is selected]
        		  --show-market   [show all the market that can query]
e.g., :
$ python3 main.py --secret-key=123456 --start-date=2020-10-01 --end-date=2020-10-02
```

In another thread, use the following command to observe the result.
```
$ python3 ./loader/WebServerHelper.py
```


# HOWTO Develop


