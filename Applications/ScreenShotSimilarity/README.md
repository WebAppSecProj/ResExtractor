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
python3 ScreenShotSimilarity.py --img-folder="working_folder/snapshot" --img-file="working_folder/snapshot/841d85d5c6460e629134433c8200811fb58b4970.png" --db-file="Applications/ScreenShotSimilarity/search_result.pkl" --DEBUG=10
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
$ python3 ScreenShotSimilarityBatch.py --img-folder="working_folder/snapshot" --db-file="Applications/ScreenShotSimilarity/screenshot.pkl" --sim-threshold=0.3
```