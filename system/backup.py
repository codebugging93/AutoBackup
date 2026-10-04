import os
from pathlib import Path
from time import sleep, time

from system.SystemValues import SystemValues
from system.depth import get_depth
from system.compare import CompareResult
from system.path import cut_path, merge_path
from system.file import copy_dir, copy_file, move_dir, move_file
from system.path import merge_path
from system.Trashbin import Trashbin


def backup(compare_result: CompareResult):
    SystemValues.backup_progress_val = 0
    SystemValues.backup_progress_max = 0
    SystemValues.backup_progress_msg = ""
    SystemValues.backup_progress_path = ""
    
    # 삭제, 갱신 등의 작업이 있다면 휴지통을 만듦
    if not (len(compare_result.files_rmv) == 0 and 
            len(compare_result.dirs_rmv) == 0 and 
            len(compare_result.files_renew) == 0):
        root = compare_result.tar_path
        Trashbin.make_trashbin(Path(root).anchor) # 같은 드라이브 폴더에 휴지통을 만듦

    # 대소문자 관련 버그때문에 삭제를 먼저 수행해야함
    SystemValues.backup_progress_msg = "파일 삭제 중"   
    remove_files(
        compare_result.tar_path, # 절대로 원본의 것을 삭제하지 않음
        compare_result.files_rmv)

    SystemValues.backup_progress_msg = "파일 갱신 중"
    renew_files(
        compare_result.org_path, 
        compare_result.tar_path,
        compare_result.files_renew
    )
    
    SystemValues.backup_progress_msg = "파일 복사 중"
    copy_files(
        compare_result.org_path, 
        compare_result.tar_path,
        compare_result.files_copy)

    # 대소문자 관련 버그때문에 삭제를 먼저 수행해야함
    SystemValues.backup_progress_msg = "폴더 삭제 중"
    SystemValues.copy_working = True 
    remove_dirs( 
        compare_result.tar_path, # 절대로 원본의 것을 삭제하지 않음
        compare_result.dirs_rmv
    )

    SystemValues.backup_progress_msg = "폴더 복사 중"
    copy_dirs(
        compare_result.org_path, 
        compare_result.tar_path,
        compare_result.dirs_copy
    )
    SystemValues.copy_working = False





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
        try:
            move_file(src, dst)
        except OSError:
            pass # 실패한 파일은 건너뜀 
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
        SystemValues.backup_progress_path = src
        try:
            copy_file(src, dst)
        except OSError:
            pass # 실패한 파일은 건너뜀 
        SystemValues.backup_progress_val += 1


def renew_files(org_path, tar_path, files: list):
    """ 
    tar_path에 존재하는 절대경로 리스트 files의 파일들을 삭제하고,
    org_path에 존재하는 파일들을 복사한다.
    """
    # 이전 파일 보관 중
    remove_files(tar_path, files)
    
    # 새로운 파일 복사 중 
    SystemValues.backup_progress_val = 0  
    SystemValues.backup_progress_max = len(files)
    for dst in files:
        cut = cut_path(dst, get_depth(tar_path))
        src = os.path.join(org_path, cut)
        SystemValues.backup_progress_path = cut
        try:
            copy_file(src, dst)
        except OSError:
            pass # 실패한 파일은 건너뜀 
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
        try:
            move_dir(src, dst)
        except OSError:
            pass # 실패한 폴더는 건너뜀 (aftercheck에서 다시 걸러짐)
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
        try:
            copy_dir(src, dst)
        except OSError:
            pass # 실패한 폴더는 건너뜀 (aftercheck에서 다시 걸러짐)
        SystemValues.backup_progress_val += 1
        

# 최적화 만들기
def boost(compare_result: CompareResult):
    """ 
    org_path와 tar_path에 들어있는 동일한 파일이 담긴 
    상대 경로 리스트 same_files에 대해서
    다음 검사시에 속도를 줄일 수 있도록 최적화를 진행한다.

    org_path의 파일의 수정된 시간을 tar_path쪽의 파일로 복사하는 작업이다.
    """
    SystemValues.backup_progress_val = 0  
    SystemValues.backup_progress_max = len(compare_result.files_same)
    count = 0
    
    for rel_path in compare_result.files_same:
        SystemValues.backup_progress_path = rel_path
        file1 = merge_path(compare_result.org_path, rel_path)
        file2 = merge_path(compare_result.tar_path, rel_path)

        try:
            time1 = os.stat(file1).st_mtime
            time2 = os.stat(file2).st_mtime
            if time1 != time2:
                # 원본 파일의 수정된 시간을 대상 파일에 덮어씌움 
                # -> 다음에 검사할때 검사 시간이 단축됨
                os.utime(file2, (time1, time1))
            count += 1 # 위 if문을 지나면 결국 time1 == time2이므로 카운팅함
        except OSError:
            pass # 최적화에 실패한 파일은 건너뜀 
        
        SystemValues.backup_progress_val += 1

    if len(compare_result.files_same) != 0:
        compare_result.optimized_percent = count / len(compare_result.files_same) * 100
    else:
        compare_result.optimized_percent = 0


# 최적화 테스트용 함수
def check_opti_rate(compare_result: CompareResult):
    SystemValues.backup_progress_val = 0  
    SystemValues.backup_progress_max = len(compare_result.files_same)

    count = 0
    for rel_path in compare_result.files_same:
        SystemValues.backup_progress_path = rel_path
        file1 = merge_path(compare_result.org_path, rel_path)
        file2 = merge_path(compare_result.tar_path, rel_path)

        time1 = os.stat(file1).st_mtime
        time2 = os.stat(file2).st_mtime
        if time1 == time2:
            count += 1
        # else:
        #     # 원본 파일의 수정된 시간을 대상 파일에 덮어씌움 
        #     # -> 다음에 검사할때 검사 시간이 단축됨
        #     os.utime(file2, (time1, time1))
            
        SystemValues.backup_progress_val += 1

    if len(compare_result.files_same) != 0:
        compare_result.optimized_percent = count / len(compare_result.files_same) * 100
    else:
        compare_result.optimized_percent = 0