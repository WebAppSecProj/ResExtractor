# img_similarity.py

## usage:

1. init 
```python
m = SIFTFlannBasedMatcher()
```
2. build the keypoint db firstly. Feed build_db with searching path and path of the `pkl` file
```python
m.build_db("../../working_folder", "../../img.db.pkl")
```
3. Then feed an img file and get the result.
```python
img = "/home/demo/Desktop/WebAppSec/ResExtractor/working_folder/xingyuan.2020.01.05/DCloud/7f467367a1d9991436cec337daf30dc945fd33c7/localres/images/src_images_toux01.png"
res = m.search_img(img, "../../img.db.pkl")
showTime = 0
for i in sorted(res.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
    if showTime < 10:
        showTime += 1
        m.debug_(img, i[0]) # will show the result one by one
    log.info(i)
```
