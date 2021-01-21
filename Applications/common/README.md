# img_similarity.py

## usage:

1. init 
```python
m = SIFTFlannBasedMatcher()
```
2. build the keypoint db firstly. Feed build_db with searching path and path of the `pkl` file
```python
m.build_signature_db("../../working_folder", "../../img.db.pkl", incremental = False)
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

# HTMLSimilarityWrapper

## usage:
```python
    m = HTMLSimilarityWrapper()

    # "build db firstly"
    m.build_signature_db("../../working_folder", "All.pkl", incremental = False)

    "compare one by one"
    html = "/Users/panmac/Desktop/workspace/WebAppSecProj/ResExtractor/working_folder/yingyuan.2021.01.12/APICloud/882f9292700f68b221f7716b7bceec9b50b1892f/localres/widget/error/error.html"
    res = m.search_img(html, "../../img.db.pkl")
    for i in sorted(res.items(), key=lambda kv: (kv[1], kv[0]), reverse=False):
        log.info(i)
```

# OCR

## usage:
select a module and feed an image, then get the result. e.g.,  
```python
    file = '/home/demo/Desktop/WebAppSec/ResExtractor/working_folder/snapshot/0d648ac6b03cb7d152efe533a4a7d3544cfaa79a.png'
    o = OCR_tesseract()
    R = o.get_literal(file)
    log.info(R)

    o = OCR_baiduAI()
    R = o.get_literal(file)
    # process error
    if R.__contains__("error_code"):
        log.error("check https://ai.baidu.com/ai-doc/OCR/zkibizyhz for reason.")
    for r in R["words_result"]:
        log.info(r["words"])
```
Other framework:
https://github.com/chineseocr/chineseocr

