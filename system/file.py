import shutil
import os

from system.DepthList import get_depth
from system.SystemValues import SystemValues
from system.path import cut_path, merge_path


def copy_file(src, dst, mkdirs=True, metadata=True):
    """
    src, dst는 절대경로를 받는다.

    mkdirs: 어떤 파일이 속할 폴더를 자동 생성하는 기능
    metadata: 파일의 메타데이터까지 복사하는 기능(수정된 시간 포함)

    권한이 없는 경우 metadata는 복사되지 않을 수 있다.
    가능한 한 chmod 권한까지 복사하려고 하기 때문이다.
    """

    if mkdirs:
        _dir = os.path.dirname(dst)
        os.makedirs(_dir, exist_ok=mkdirs)

    shutil.copyfile(src, dst) # 파일 복사
    if metadata:
        try: 
            shutil.copystat(src, dst) # 메타데이터 복사
        except PermissionError:
            # chmod를 사용할 권한이 없는 경우 PermissionError가 발생함 
            pass 


def move_file(src, dst, mkdirs=True, metadata=True):
    """
    copy_file(src, dst)로 파일을 복사하고
    src 파일을 os.remove로 삭제한다.
    """
    try: # 같은 드라이브 내에서는 이게 더욱 빠름
        _dir = os.path.dirname(dst)
        os.makedirs(_dir, exist_ok=mkdirs)
        os.rename(src, dst)
    except OSError:
        copy_file(src, dst, mkdirs=mkdirs, metadata=metadata)
        os.remove(src)


def copy_dir(src, dst, metadata=True):
    """
    src 폴더를 dst로 통째로, 재귀적으로 복사한다.
    src, dst는 절대경로이다.
    """
    SystemValues.copy_progress_max = 0
    SystemValues.copy_progress_val = 0
    SystemValues.copy_progress_path = ""

    # os.walk를 이용해서 각 root마다 files를 복사해야함
    for _, _, files in os.walk(src):
        SystemValues.copy_progress_max += len(files)

    src_depth = get_depth(src)
    for src_dir, dirs, files in os.walk(src):
        cut = cut_path(src_dir, src_depth) 
        dst_dir = merge_path(dst, cut) # 복사 목적지 경로
        # src의 내부 폴더 src_dir을 dst의 내부 폴더 dst_dir로 복사함

        os.makedirs(dst_dir, exist_ok=True) # 폴더 생성

        for name in files:
            src_file = merge_path(src_dir, name)
            dst_file = merge_path(dst_dir, name)
            SystemValues.copy_progress_path = src_file
            copy_file(src_file, dst_file, metadata=metadata)
            SystemValues.copy_progress_val += 1



def move_folder(src, dst):
    """ 나중에 Trashbin 사용자 선택 기능을 넣을 때 세부 구현. """
    shutil.move(src, dst)