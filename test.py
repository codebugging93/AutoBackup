from tkinter.filedialog import askdirectory
from system.backup import backup
from system.AppData import AppData, CheckMode
from system.compare import CompareResult, compare
from tkinter import *

root = Tk()


# AppData.original_path = askdirectory()
# AppData.target_path = askdirectory()

# AppData.check_mode = CheckMode.DEEP

# if AppData.check_mode == CheckMode.FAST: # 사용자가 빠른 검사 버튼을 누르면 
#     fast_scan = True 
# elif AppData.check_mode == CheckMode.DEEP: # 사용자가 정밀 검사 버튼을 누르면 
#     fast_scan = False
# else: # 기본값
#     fast_scan = True 


AppData.original_path = r"e:\test_a"
AppData.target_path = r"e:\test_b"
result = compare(
    AppData.original_path, 
    AppData.target_path, 
    )

AppData.compare_result = result
result.print()

# for i in AppData.compare_result.dirs_same:
    # print(i)

backup(AppData.compare_result)

"""

a b 
result = compare(a, b)
backup(result)
failed = aftercheck(result)

backup(failed)

boost_files(a, b, result.files_same)
"""