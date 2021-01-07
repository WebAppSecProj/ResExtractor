## Web Resource Monitor 

Web Monitor is designed for download remote source, query sever information and web resource changes.

### Folder structure:

Total wen resource

```python
├─00a95f0e62afc81ec6a138d5b5c4c16607d2d3e8  
│  ├─cordova-js-src  
│  │  ├─android  
│  │  └─plugin  
│  │      └─android  
│  ├─icons  
│  ├─plugins  
│  │  ├─cordova-plugin-appminimize  
│  │  │  └─www  
│  │  └─cordova-plugin-camera  
│  │      └─www  
│  └─**Remote**(**where we store remote web resource**)  
│      ├─03ba67568336c85bac3d47a80a924181  
│      ├─4c705510d041a366fbe25996e1c40e85  
│      ├─5fc05ef60c578d22d1eee6b6a34aa853  
│      └─dd90e725166065b8e428c5e05a9c6d16  
└─0b69ea19490b407537175575a717d6a7fd5bd696  
    ├─css  
    ├─html  
    ├─script  
    └─**Remote**  
        └─fd96577ee1ca9b82c8ce1d57c753b3a3(**where we store remote web resource**)
```


It is equivalent to creating a new label folder under the local web resource folder, and use md5 for each URL to create a URL folder to store remote information.

### Usage:

1. Initialization time `Runner`, you must set up a default file to store the URL, now only support `csv` type
2. Then use function `add_websource` can add the folder where parser is required
3. If you need to add a URL filter, use `add_filter`, now we support `txt` and `csv` format
4. Perform parser on all files that have been added. Use `parser`, and don't forget specify a storage file, the default one is the initial storage location.
5. `add_monitorfile` can add different URL store file entry the `Runner`
6. `run` is the core function of `demo`, `run` can update all urls in all URL store files.

```python
from RemoteExtractor import *
if __name__ == "__main__":
    a = Runner(r'The file path that stores the URL,only support csv type')
    a.add_websource(DirInput(r'folder that stores local web resources'),"The tag you want to set")
    a.add_filter(r'CN.csv')
    a.add_filter(r'my_filter.txt')
    #a.add_filter('any filter your want')
    a.parser(r'The specified storage path')
    a.run()
    a.add_monitorfile(r'Another file path that stores the URLS')
    a.run()
```

### TODO:
1. I find aliyun.com etc. in CN.cvs.
