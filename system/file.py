import shutil
import os

from system.depth import get_depth
from system.SystemValues import SystemValues
from system.path import cut_path, merge_path


def copy_file(src, dst, mkdirs=True, metadata=True):
    """
    src, dst는 절대경로를 받는다.
    dst에 이미 파일이 있는 경우 FileExistsError를 발생시킨다.

    mkdirs: 어떤 파일이 속할 폴더를 자동 생성하는 기능
    metadata: 파일의 메타데이터까지 복사하는 기능(수정된 시간 포함)     
    
    metadata는 shutil.copystat을 호출하며, 권한까지 복사하려고 try해본다.
    권한 복사 실패시 pass된다.
    """

    if os.path.exists(dst):
        raise FileExistsError(f"이미 파일이 존재합니다: {dst}")

    if mkdirs:
        os.makedirs(os.path.dirname(dst), exist_ok=True)

    shutil.copyfile(src, dst, follow_symlinks=False) # 파일 복사
    if metadata:
        try: 
            shutil.copystat(src, dst, follow_symlinks=False) # 메타데이터 복사
        except PermissionError:
            # chmod를 사용할 권한이 없는 경우 PermissionError가 발생함 
            pass 


def move_file(src, dst, mkdirs=True, metadata=True):
    """
    src 파일을 dst로 옮긴다.

    같은 드라이브 내라면 os.rename으로 옮기고(이게 더욱 빠름),
    다른 드라이브라면 copy_file(src, dst)로 파일을 복사하고 src 파일을 os.remove로 삭제한다.
    """
    # 같은 드라이브라면 os.rename으로 빠르게 옮김 
    if os.path.splitdrive(src)[0].lower() == os.path.splitdrive(dst)[0].lower():
        if mkdirs:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.rename(src, dst)
    # 다른 드라이브라면 copy_file을 호출함
    else:
        copy_file(src, dst, mkdirs=mkdirs, metadata=metadata)
        os.remove(src)


def copy_dir(src, dst, metadata=True):
    """
    src 폴더를 dst로 통째로, 재귀적으로 복사한다.
    src, dst는 절대경로이다.
    """
    SystemValues.bottom_progress_msg = "파일 복사 중"
    SystemValues.bottom_progress_max = 0
    SystemValues.bottom_progress_val = 0
    SystemValues.bottom_progress_path = ""

    # os.walk를 이용해서 각 root마다 files를 복사해야함
    for _, _, files in os.walk(src):
        SystemValues.bottom_progress_max += len(files)

    src_depth = get_depth(src)
    for src_dir, dirs, files in os.walk(src):
        cut = cut_path(src_dir, src_depth) 
        dst_dir = merge_path(dst, cut) # 복사 목적지 경로
        # src의 내부 폴더 src_dir을 dst의 내부 폴더 dst_dir로 복사함

        os.makedirs(dst_dir, exist_ok=True) 

        for name in files:
            src_file = merge_path(src_dir, name)
            dst_file = merge_path(dst_dir, name)
            SystemValues.bottom_progress_path = src_file
            try:
                copy_file(src_file, dst_file, metadata=metadata)
            except OSError:
                pass # 실패한 파일은 건너뛰고 폴더의 나머지 파일을 계속 복사함
            SystemValues.bottom_progress_val += 1


def move_dir(src, dst, mkdirs=True, metadata=True):
    """
    폴더를 src에서 dst로 옮긴다.

    같은 드라이브라면 os.rename으로 빠르게 옮겨지지만, 
    다른 드라이브라면 copy_dir을 실행후 원본 폴더는 제거한다.
    """
    # 같은 드라이브라면 os.rename으로 빠르게 옮김
    if os.path.splitdrive(src)[0].lower() == os.path.splitdrive(dst)[0].lower():
        SystemValues.bottom_progress_visible = False # 이땐 하단바 보여줄 필요가 없다.
        if mkdirs:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.rename(src, dst)
        return

    """ 아래 코드는 copy_dir을 그대로 갖고와서 일부 수정한 것이다. """

    # 다른 드라이브라서 파일을 하나씩 옮겨야 할 때만 아랫줄을 켠다.
    SystemValues.bottom_progress_visible = True
    SystemValues.bottom_progress_msg = "파일 이동 중"
    SystemValues.bottom_progress_max = 0
    SystemValues.bottom_progress_val = 0
    SystemValues.bottom_progress_path = ""

    # os.walk를 이용해서 각 root마다 files를 복사해야함
    for _, _, files in os.walk(src):
        SystemValues.bottom_progress_max += len(files)

    src_depth = get_depth(src)
    for src_dir, dirs, files in os.walk(src, topdown=False):
        cut = cut_path(src_dir, src_depth) 
        dst_dir = merge_path(dst, cut) # 복사 목적지 경로
        # src의 내부 폴더 src_dir을 dst의 내부 폴더 dst_dir로 복사함

        os.makedirs(dst_dir, exist_ok=True) # 의도적인 try-except 미사용

        for name in files:
            src_file = merge_path(src_dir, name)
            dst_file = merge_path(dst_dir, name)
            SystemValues.bottom_progress_path = src_file
            try:
                move_file(src_file, dst_file, metadata=metadata)
            except OSError:
                pass # 실패한 파일은 건너뛰고 폴더의 나머지 파일을 계속 복사함
            SystemValues.bottom_progress_val += 1

        try: # 전부 비운 폴더 삭제 시도
            os.rmdir(src_dir)
        except OSError: # 실패시 넘김
            pass



    