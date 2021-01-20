# ScreenShotSimilarity.py
This module is used to search img
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
e.g.,
```commandline
python3 ScreenShotSimilarity.py --img-folder="working_folder/snapshot" --img-file="working_folder/snapshot/e59fda3a65ad05b4df834a66db32818a52c82320.png" --db-file="Applications/ScreenShotSimilarity/screenshot_signature_db.pkl" --DEBUG=10
```

# ScreenShotSimilarityCluster.py
This module is used to cluster similar img

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
$ python3 ScreenShotSimilarityBatch.py --db-file="Applications/ScreenShotSimilarity/screenshot_signature_db.pkl" --img-folder="working_folder/snapshot" --sim-threshold=0.3
```

# Format of db file
{hash-of-apk, {"des": signature-of-img}}

# TODO
A fine strategy is needed, e.g., remove the pic without enough keypoint. take snapshot per minute and remove the useless image by using template.  
Or pursue a new similarity analysis algorithm.   