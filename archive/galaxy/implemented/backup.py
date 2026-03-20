import os
from datetime import datetime

from galaxy.paths import RESULT_PATH
from galaxy.widgets import *

from implemented.main_datas import original, target, backup_data, main_prog
from utils.file import copy_file



__all__ = [
    "make_result_date_folder",
    "mkdir_in_result_date_path",
    "get_result_date_path",
    "backup_copy",
    "backup_remove",
    "backup_boost",
    ]

    
result_date_path = None

def make_result_date_folder():
    """ x월 y일_hhmmss 폴더를 만든다. """
    global result_date_path
    # 이름 만들기
    format_spec = "%m월 %d일_%H%M%S"
    time_str = datetime.now().strftime(format_spec)
    
    # 값 할당, 생성
    result_date_path = os.path.join(RESULT_PATH, time_str)
    os.makedirs(result_date_path, exist_ok=True)
    return result_date_path
    
    
def mkdir_in_result_date_path(name):
    """ 시간이 쓰여진 result 폴더 안에 name 폴더를 생성한다. """
    p = get_result_date_path()
    new = os.path.join(p, name)
    os.makedirs(new, exist_ok=True)
    return new 
    
    
def get_result_date_path():
    # None일때 사용하는걸 의도하지 않았기 때문에 Exception을 일으킴
    if result_date_path is None:
        raise Exception("result_date has not created")
    return result_date_path


def backup_copy():
    """
    원본의 set_file_copy를 전부 result_date로 복사한다.
    
    더 자세히
        set_file_copy는 상대경로의 모음이다.
        그래서 original.path + (set_file_copy의 원소)를 
        result_date_path + (set_file_copy의 원소)로 복사하면 된다.
        
    """
    # 파일 복사
    tar_dir = mkdir_in_result_date_path("복사할 폴더")
    for i in backup_data.set_file_copy: 
        copy_file(original.path, tar_dir, i, True)
        main_prog.num += 1
        

def backup_remove():
    """ "<original폴더명>.txt"를 만든다. """
    # 파일 삭제 데이터 작성
    file_name = os.path.basename(original.path) + "_rmv.txt" # 루트 폴더명만 떼오는거라 target이든 original이든 상관없음
    rmv_file_path = os.path.join(get_result_date_path(), file_name)
    with open(rmv_file_path, "w", encoding="utf8") as file:
        for cut in backup_data.set_file_rmv:
            file.write(cut + "\n")
            main_prog.num += 1
    

def backup_boost():
    """ 최적화 데이터를 만든다. """
    # 최적화 데이터 작성
    file_name = os.path.basename(original.path) + "_bst.txt"
    bst_file_path = os.path.join(get_result_date_path(), file_name)
    with open(bst_file_path, "w", encoding="utf8") as file:
        for cut in backup_data.set_file_same:
            _org_file = os.path.join(original.path, cut)
            _tar_file = os.path.join(target.path, cut)
            org_mtime = os.stat(_org_file).st_mtime
            tar_mtime = os.stat(_tar_file).st_mtime
            if org_mtime != tar_mtime:
                file.write(f"{cut}:{org_mtime}\n")
    
    




