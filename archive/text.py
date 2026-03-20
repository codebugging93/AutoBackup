import threading
from shutil import copy2
import os
from pkg.Path import get_file_size
from pkg.Byte import convert
# 복사현황 실시간 표시
s = "/storage/emulated/0/vv.zip"
p = "/storage/emulated/0/Virtual Partition/새 폴더"

def check():
    while True:
        a = os.path.basename(s)
        b = os.path.join(p, a)
        print(convert(get_file_size(b)))
        
        
def copy():
    copy2(s, p)
    

threading.Thread(target=check).start()
threading.Thread(target=copy).start()

            

            
    