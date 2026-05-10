import os
from pathlib import Path
import shutil

from system.DepthList import get_depth
from system.compare import CompareResult
from system.path import cut_path, merge_path
from system.file import copy_dir, copy_file, move_file
from system.path import merge_path
from system.Trashbin import Trashbin


def backup(compare_result: CompareResult):
    root = compare_result.tar_path
    Trashbin.make_trashbin(Path(root).anchor) # 같은 드라이브 폴더에 휴지통을 만듦

    copy_files(
        compare_result.org_path, 
        compare_result.tar_path,
        compare_result.files_copy)
    
    remove_files(
        compare_result.tar_path, # 절대로 원본의 것을 삭제하지 않음
        compare_result.files_rmv)
    
    renew_files(
        compare_result.org_path, 
        compare_result.tar_path,
        compare_result.files_renew
    )

    copy_dirs(
        compare_result.org_path, 
        compare_result.tar_path,
        compare_result.dirs_copy
    )

    remove_dirs( 
        compare_result.tar_path, # 절대로 원본의 것을 삭제하지 않음
        compare_result.dirs_rmv
    )



def remove_files(root, files: list | set):
    """ 
    root 안의 절대경로 리스트 files의 파일들을 휴지통으로 보내고 삭제한다.
    """
    for src in files:
        cut = cut_path(src, get_depth(root))
        dst = os.path.join(Trashbin.get_remove_path(), cut)
        move_file(src, dst)


def copy_files(org_path, tar_path, files: list | set):
    """ 
    org_path 내의 절대경로 리스트 files의 파일들을 tar_path로 복사한다.
    """
    for src in files:
        cut = cut_path(src, get_depth(org_path))
        dst = os.path.join(tar_path, cut)
        copy_file(src, dst)


def renew_files(org_path, tar_path, files: list):
    """ 
    org_path와 tar_path에 동시에 존재하는 상대경로 리스트 files의 파일들을
    org_path -> tar_path 방향으로 덮어씌운다.
    갱신되기 전의 파일은 휴지통에 보관한다.
    """
    # # 이전 파일 보관 중
    for rel_path in files:
        src = merge_path(tar_path, rel_path)
        dst = os.path.join(Trashbin.get_remove_path(), rel_path)
        move_file(src, dst)
    
    # 새로운 파일 복사 중 
    for rel_path in files:
        src = merge_path(org_path, rel_path)
        dst = merge_path(tar_path, rel_path)
        copy_file(src, dst)


def remove_dirs(root, dirs: list):
    """ 
    root 안의 절대경로 리스트 dirs의 폴더들을 휴지통으로 보내고 삭제한다.
    """ 
    for src in dirs: 
        # src 폴더를 dst로 옮겨야함
        cut = cut_path(src, get_depth(root))
        dst = os.path.join(Trashbin.get_remove_path(), cut)
        shutil.move(src, dst)
    

def copy_dirs(org_path, tar_path, dirs: list):
    """ 
    src 안의 상대경로 리스트 dirs의 폴더들을 
    dst로 통째로 복사한다.
    """
    for src in dirs: 
        # src 폴더를 dst로 통복사함
        cut = cut_path(src, get_depth(org_path))
        dst = os.path.join(tar_path, cut)
        copy_dir(src, dst)
        

# 최적화 만들기
def boost_files(org_path, tar_path, same_files: list | set):
    """ 
    org_path와 tar_path에 들어있는 동일한 파일이 담긴 
    상대 경로 리스트 same_files에 대해서
    다음 검사시에 속도를 줄일 수 있도록 최적화를 진행한다.

    org_path의 파일의 수정된 시간을 tar_path쪽의 파일로 복사하는 작업이다.
    """
    for rel_path in same_files:
        file1 = merge_path(org_path, rel_path)
        file2 = merge_path(tar_path, rel_path)

        # 원본 파일의 수정된 시간을 대상 파일에 덮어씌움 
        # -> 다음에 검사할때 검사 시간이 단축됨
        st_mtime = os.stat(file1).st_mtime
        os.utime(file2, (st_mtime, st_mtime))


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

