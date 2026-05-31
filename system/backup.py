import os
from pathlib import Path
from time import sleep, time
import shutil

from system.SystemValues import SystemValues
from system.DepthList import get_depth
from system.compare import CompareResult
from system.path import cut_path, merge_path
from system.file import copy_dir, copy_file, move_file
from system.path import merge_path
from system.Trashbin import Trashbin


def backup(compare_result: CompareResult):
    SystemValues.backup_start_time = time()
    SystemValues.backup_progress_val = 0
    SystemValues.backup_progress_max = 0
    SystemValues.backup_progress_path = ""
    
    root = compare_result.tar_path
    Trashbin.make_trashbin(Path(root).anchor) # 같은 드라이브 폴더에 휴지통을 만듦


    # 대소문자 관련 버그때문에 삭제를 먼저 수행해야함
    SystemValues.backup_progress_msg = "파일 삭제 중"
    remove_files(
        compare_result.tar_path, # 절대로 원본의 것을 삭제하지 않음
        compare_result.files_rmv)
    if len(compare_result.files_rmv) != 0:
        sleep(0.5)
    
    SystemValues.backup_progress_msg = "파일 복사 중"
    copy_files(
        compare_result.org_path, 
        compare_result.tar_path,
        compare_result.files_copy)
    if len(compare_result.files_copy) != 0:
        sleep(0.5)
    
    SystemValues.backup_progress_msg = "파일 갱신 중"
    renew_files(
        compare_result.org_path, 
        compare_result.tar_path,
        compare_result.files_renew
    )
    if len(compare_result.files_renew) != 0:
        sleep(0.5)

    # 대소문자 관련 버그때문에 삭제를 먼저 수행해야함
    SystemValues.backup_progress_msg = "폴더 삭제 중"
    remove_dirs( 
        compare_result.tar_path, # 절대로 원본의 것을 삭제하지 않음
        compare_result.dirs_rmv
    )
    if len(compare_result.dirs_rmv) != 0:
        sleep(0.5)

    SystemValues.backup_progress_msg = "폴더 복사 중"
    SystemValues.copy_working = True 
    copy_dirs(
        compare_result.org_path, 
        compare_result.tar_path,
        compare_result.dirs_copy
    )
    SystemValues.copy_working = False
    if len(compare_result.dirs_copy) != 0:
        sleep(0.5)

    SystemValues.backup_run_time = time() - SystemValues.backup_start_time




def remove_files(root, files: list | set):
    """ 
    root 안의 절대경로 리스트 files의 파일들을 휴지통으로 보내고 삭제한다.
    """
    SystemValues.backup_progress_val = 0  
    SystemValues.backup_progress_max = len(files)
    for src in files:
        cut = cut_path(src, get_depth(root))
        dst = os.path.join(Trashbin.get_remove_path(), cut)
        SystemValues.backup_progress_path = src
        move_file(src, dst)
        SystemValues.backup_progress_val += 1
       

def copy_files(org_path, tar_path, files: list | set):
    """ 
    org_path 내의 절대경로 리스트 files의 파일들을 tar_path로 복사한다.
    """
    SystemValues.backup_progress_val = 0  
    SystemValues.backup_progress_max = len(files)
    for src in files:
        cut = cut_path(src, get_depth(org_path))
        dst = os.path.join(tar_path, cut)
        SystemValues.backup_progress_path = cut
        copy_file(src, dst)
        SystemValues.backup_progress_val += 1


def renew_files(org_path, tar_path, files: list):
    """ 
    tar_path에 존재하는 절대경로 리스트 files의 파일들을 삭제하고,
    org_path에 존재하는 파일들을 복사한다.
    """
    # 이전 파일 보관 중
    remove_files(tar_path, files)
    SystemValues.backup_progress_val = 0  
    SystemValues.backup_progress_max = len(files)
    
    # 새로운 파일 복사 중 
    for dst in files:
        cut = cut_path(dst, get_depth(tar_path))
        src = os.path.join(org_path, cut)
        SystemValues.backup_progress_path = cut
        copy_file(src, dst)
        SystemValues.backup_progress_val += 1

def remove_dirs(root, dirs: list):
    """ 
    root 안의 절대경로 리스트 dirs의 폴더들을 휴지통으로 보내고 삭제한다.
    """ 
    SystemValues.backup_progress_val = 0  
    SystemValues.backup_progress_max = len(dirs)
    for src in dirs: 
        # src 폴더를 dst로 옮겨야함
        cut = cut_path(src, get_depth(root))
        dst = os.path.join(Trashbin.get_remove_path(), cut)
        SystemValues.backup_progress_path = src
        shutil.move(src, dst)
        SystemValues.backup_progress_val += 1
    

def copy_dirs(org_path, tar_path, dirs: list):
    """ 
    src 안의 상대경로 리스트 dirs의 폴더들을 
    dst로 통째로 복사한다.
    """
    SystemValues.backup_progress_val = 0  
    SystemValues.backup_progress_max = len(dirs)
    for src in dirs: 
        # src 폴더를 dst로 통복사함
        cut = cut_path(src, get_depth(org_path))
        dst = os.path.join(tar_path, cut)
        SystemValues.backup_progress_path = src
        copy_dir(src, dst)
        SystemValues.backup_progress_val += 1
        

# 최적화 만들기
def boost_files(org_path, tar_path, same_files: list | set):
    """ 
    org_path와 tar_path에 들어있는 동일한 파일이 담긴 
    상대 경로 리스트 same_files에 대해서
    다음 검사시에 속도를 줄일 수 있도록 최적화를 진행한다.

    org_path의 파일의 수정된 시간을 tar_path쪽의 파일로 복사하는 작업이다.
    """
    SystemValues.backup_progress_val = 0  
    SystemValues.backup_progress_max = len(same_files)
    for rel_path in same_files:
        file1 = merge_path(org_path, rel_path)
        file2 = merge_path(tar_path, rel_path)

        # 원본 파일의 수정된 시간을 대상 파일에 덮어씌움 
        # -> 다음에 검사할때 검사 시간이 단축됨
        st_mtime = os.stat(file1).st_mtime
        SystemValues.backup_progress_path = rel_path
        os.utime(file2, (st_mtime, st_mtime))
        SystemValues.backup_progress_val += 1


# 최적화 테스트용 함수
def _check_files(org_path, tar_path, same_files: list | set):
    """ 
    org_path와 tar_path에 들어있는 동일한 파일이 담긴 
    상대 경로 리스트 same_files에 대해서
    다음 검사시에 속도를 줄일 수 있도록 최적화를 진행한다.

    org_path의 파일의 수정된 시간을 tar_path쪽의 파일로 복사하는 작업이다.
    """
    count = 0
    for rel_path in same_files:
        file1 = merge_path(org_path, rel_path)
        file2 = merge_path(tar_path, rel_path)

        # 원본 파일의 수정된 시간을 대상 파일에 덮어씌움 
        # -> 다음에 검사할때 검사 시간이 단축됨
        time1 = os.stat(file1).st_mtime
        time2 = os.stat(file2).st_mtime
        if time1 != time2:
            count += 1
        
    print("최적화되지 않은 파일의 개수:", count)

