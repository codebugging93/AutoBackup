import os

from implemented.main_datas import original, target, main_prog, sub_prog
from utils.path import get_filename_set, merge_path
from utils.file import copy_file, move_file
from implemented.trashbin import RemovePathNotExists, get_backup_remove_path
from utils.Classes.Progress import Progress
      

    

def remove_files(prog: Progress, path_set):
    """ 
    target.path 안의 상대경로 리스트 path_set의 
    파일들을 휴지통으로 보내고 삭제한다.
    """

    if get_backup_remove_path() == "":
        raise RemovePathNotExists

    for cut in path_set:
        move_file(target.path, get_backup_remove_path(), cut)
        prog.num += 1
        

def copy_files(prog, path_set):
    """ 
    original.path 안의 상대경로 리스트 path_set의 파일들을 target.path로 복사한다.
    단, 폴더 구조가 완전히 일치해야만 사용이 가능하다.
    """
    for cut in path_set:
        org_path = merge_path(original.path, cut)
        tar_path = merge_path(target.path, cut)
        copy_file(org_path, tar_path)
        prog.num += 1
        

def renew_files(prog, path_set):
    """
    original.path, target.path 사이의
    상대경로 리스트 path_set 파일들을 갱신한다.
    """

    if get_backup_remove_path() == "":
        raise RemovePathNotExists

    for cut in path_set:
        move_file(target.path, get_backup_remove_path(), cut)
        copy_file(original.path, target.path, cut)
        prog.num += 1
        

def remove_folders(tree):
    """
    target.path 안의 상대경로 트리 tree에 대하여
    cut이라는 상대경로 폴더를 통째로 remove_path로 보낸다.
    """

    if get_backup_remove_path() == "":
        raise RemovePathNotExists

    length = len(tree)
    for i in range(1, length): 
        i = length - i

        # 맨 끝부터 폴더 지정
        for cut in tree[i]:
            # 폴더 선언, 생성
            org = os.path.join(target.path, cut)
            dst = os.path.join(get_backup_remove_path(), cut)
            os.makedirs(dst, exist_ok=True)

            # 파일 이동 작업
            files = get_filename_set(org)  # 이동할 파일 이름 집합
            sub_prog.config(num=0, total=len(files))  # prog 설정
            for f in files:
                move_file(org, dst, f)
                sub_prog.num += 1
            
            # 폴더 삭제 (끝)
            os.rmdir(org)
            main_prog.num += 1
    

def copy_folders(tree):
    """
    original.path 안의 상대경로 트리 tree에 대하여
    cut이라는 상대경로 폴더를 통째로 target.path로 복사한다.
    """
    
    for _list in tree:
        for cut in _list:
            # 폴더 선언, 생성
            org = os.path.join(original.path, cut)
            dst = os.path.join(target.path, cut)
            os.makedirs(dst, exist_ok=True)

            # 파일 복사 작업
            files = get_filename_set(org) # 복사할 파일 이름 집함
            sub_prog.config(num=0, total=len(files)) # prog 설정
            for f in files:
                copy_file(org, dst, f)
                sub_prog.num += 1 
                
            # 폴더 복사 끝
            main_prog.num += 1


def boost_files(_set):
    """ file1 -> file2 방향으로 작업한다. 즉 file1이 원본인 셈 """
    for i in _set:
        file1 = os.path.join(original.path, i)
        file2 = os.path.join(target.path, i)

        st_mtime = os.stat(file1).st_mtime
        os.utime(file2, (st_mtime, st_mtime))
        main_prog.num += 1


def add_file_num(fname, folder):
    """
    파일이 어떤 폴더에 이미 있으면
    그 뒤에 번호를 붙인 경로를 반환한다.
    """

    name, ext = os.path.splitext(fname)
    newpath = os.path.join(folder, fname)

    # 이름 재설정
    idx = 0
    while os.path.exists(newpath):
        idx += 1
        fname = f"{name} ({idx}){ext}"
        newpath = os.path.join(folder, fname)

    return fname
    