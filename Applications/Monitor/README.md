## Web Resource Monitor 

Web Monitor is designed for download remote source, query sever information and web  resource changes.

### Folder structure:

#### Before:

Web resource:

--------->md5(00a95f0e62afc81ec6a138d5b5c4c16607d2d3e8)

​             | ------>html

​			 |------->js/css/img （**local web resource**)

--------->md5(0b69ea19490b407537175575a717d6a7fd5bd696)

​             |------>html

​			 |------->js/css/img

#### After:

Web resource:

--------->md5(00a95f0e62afc81ec6a138d5b5c4c16607d2d3e8)

​             | ------>html

​			 |------->js/css/img（**local web resource**)

​             | ------>labe one (**where we store remote web resource**)

​						|------>url1

​								|----->record.txt

​								|----->img

​								|----->js

​								|----->css

​								|----->js.txt/css.txt/img.txt

​             | ------>labe two

​						|------>url1

​								|----->record.txt

​								|----->img

​								|----->js

​								|----->css

​								|----->js.txt/css.txt/img.txt

--------->md5(0b69ea19490b407537175575a717d6a7fd5bd696)

​             |------>html

​			 |------->js/css/img

……

### Usage:

1. Initialization time `Runner`, you must set up a default file to store the URL, now only support `csv` type
2. Then use function `add_websource` can add the folder where parser is required
3. If you need to add a URL filter, use `add_filter`, now we support `txt` and `csv` format
4. Perform parser on all files that have been added. use `parser`, and don't forget specify a storage file, the default is the initial storage location.
5. `add_monitorfile` can add different URL store file entry the `Runner`
6. `run` is the core function of `demo`, `run` can update all urls in all URL store files.

```python
from demo import *
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

