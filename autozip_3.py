import shutil
import os
import subprocess
from time import sleep
from datetime import datetime
import zipfile


def make_zip_name(filepath):
    root, ext = os.path.splitext(os.path.basename(filepath))
    date = datetime.strftime(datetime.now(), "%y%m%d")

    result = f"{root} {date}{ext}"
    return result


def attach_number_at_file(filepath):
    root, ext = os.path.splitext(filepath)
    i = -1
    while os.path.isfile(filepath):
        i += 1
        filepath = f"{root} {i}{ext}"
    return filepath


root_dir = os.path.dirname(__file__)
try:
    target = root_dir + ".zip"
    os.remove(target)
    print(target + " 삭제 완료")
except FileNotFoundError:
    pass


# 압축파일 생성
result_path = root_dir + ".zip"


# root_dir을 기준으로 한 상대경로를 paths_to_zip에 모음 
paths_to_zip = []
for root, dirs, files in os.walk(root_dir):
    if root.startswith(os.path.join(root_dir, "build")):
        continue 

    for i in dirs:
        path = os.path.join(root, i)
        paths_to_zip.append(path)

    for i in files:
        path = os.path.join(root, i)
        paths_to_zip.append(path)



with zipfile.ZipFile(result_path, "w") as my_zip:
    i:str
    for i in paths_to_zip:
        my_zip.write(
            filename=i, # 실제로 읽어들일 파일 주소
            arcname=i.replace(root_dir, "").removeprefix(os.sep) 
            # 압축파일 내에 바로 root_dir의 내용물이 들어있도록 하기 위해서
            # arcname에 상대경로 입력
        )
    my_zip.close()

print(result_path + " 생성 완료")


dir_target = "C:\\Users\\intel123\\OneDrive\\작업물"
if not os.path.isdir(dir_target):
    print("OneDrive 폴더가 존재하지 않아 복사하지 않았습니다.")

else:
    path_tar = os.path.join(dir_target, make_zip_name(result_path))
    path_tar = attach_number_at_file(path_tar)
    shutil.copy2(result_path, path_tar)
    print("복사 완료")
    subprocess.run(["cmd", "/c", "start", dir_target])






sleep(1)

    