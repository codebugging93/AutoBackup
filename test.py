from tkinter.filedialog import *
import time
import os
from system.filecmp_modified import auto_set_filter, cmp_filter 


a = askopenfilename()
b = askopenfilename()



at = time.time()
auto_set_filter(os.path.dirname(b))
print(cmp_filter(a, b))
print(time.time() - at)