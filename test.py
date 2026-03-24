# from utils.exFATcmp import auto_set_filter, _get_filter


# auto_set_filter("G:\\")
# print(_get_filter())
import os
import time

for root, dirs, files in os.walk("D:/Studying"):
    print(root)
    print(dirs)
    print(files)
    print("---------------------")
    time.sleep(10)
