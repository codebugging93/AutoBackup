import os
from pathlib import Path
import shutil

from system.DepthList import get_depth
from system.path import cut_path, get_dirs_relpath, get_filename_set, get_files_relpath, merge_path
from system.file import copy_file, move_file, move_folder
from system.path import merge_path
from system.Trashbin import Trashbin


def remove_files(root, files: list | set):
    """ 
    root 안의 상대경로 리스트 files의 파일들을 휴지통으로 보내고 삭제한다.
    """
    Trashbin.make_trashbin(Path(root).anchor) # 드라이브 폴더에 휴지통을 만듦

    for rel_path in files:
        src = merge_path(root, rel_path)
        dst = os.path.join(Trashbin.get_remove_path(), rel_path)
        move_file(src, dst)


def copy_files(org_path, tar_path, files: list | set):
    """ 
    org_path 내의 상대경로 리스트 files의 파일들을
    tar_path로 복사한다.
    """
    for rel_path in files:
        file1 = merge_path(org_path, rel_path)
        file2 = merge_path(tar_path, rel_path)
        copy_file(file1, file2)


def renew_files(org_path, tar_path, files: list):
    """ 
    org_path 내의 상대경로 리스트 files의 파일들을
    tar_path로 덮어씌운다(갱신한다).
    갱신되기 전의 파일은 휴지통에 보관한다.
    """
    # 파일 갱신 중

    # 이전 파일 보관 중
    remove_files(tar_path, files)

    # 새로운 파일 복사 중 
    copy_files(org_path, tar_path)


def remove_folders(root, dirs: list):
    """ 
    root 안의 상대경로 리스트 dirs의 폴더들을 휴지통으로 보내고 삭제한다.
    """ 
    Trashbin.make_trashbin(Path(root).anchor) # 같은 드라이브 폴더에 휴지통을 만듦

    for rel_path in dirs: 
        # src 폴더를 dst로 옮겨야함
        src_dir = merge_path(root, rel_path)
        dst_dir = os.path.join(Trashbin.get_remove_path(), rel_path)
        shutil.move(src_dir, dst_dir)
    

def copy_folders(org_path, tar_path, dirs: list):
    """ 
    src 안의 상대경로 리스트 dirs의 폴더들을 
    dst로 통째로 복사한다.
    """
    for rel_path in dirs: 
        # src 폴더를 dst로 복사해야함
        src_dir = merge_path(org_path, rel_path)
        dst_dir = merge_path(tar_path, rel_path)
        
        src_depth = get_depth(src_dir)
        for src, _dirs, _files in os.walk(src_dir):
            cut = cut_path(src, src_depth)
            dst = merge_path(dst_dir, cut) # 복사 목적지 경로
            os.makedirs(dst, exist_ok=True) # 폴더 생성
            copy_files(src, dst, _files) # 파일이 있는 경우 복사


            


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

        st_mtime = os.stat(file1).st_mtime
        os.utime(file2, (st_mtime, st_mtime))

    