import os
from utils.path import get_depth
from implemented.DepthList import DepthList
from implemented.main_datas import main_prog


def get_path_info(path):
    """
    tree, 폴더 수, 파일 수 를 한번에 구하는 함수
    """
    path = os.path.normpath(path)
    depth = get_depth(path)

    tree = DepthList()
    files = 0
    folders = 0

    for root, dir_list, file_list in os.walk(path):
        tree.attach(root, depth) # tree[0]에 ''이 들어있는 것은 이상한 것이 아니다. tree는 메모리 절약을 위하여 각각의 값이 루트 폴더가 생략된 채로 저장된다.
        files += len(file_list)
        folders += 1
        
        main_prog.num += 1

    return tree, folders, files


def get_relative_DepthList(path):
    """
    path에서부터 하위 폴더를 탐색하여
    tree 구조로 반환한다.
    """

    path = os.path.normpath(path)
    depth = get_depth(path)
    tree = DepthList()

    for root, dirs, files in os.walk(path):
        tree.attach(root, depth)
        
        main_prog.num += 1

    return tree


def get_dir_size(path):
    """
    폴더 path의 용량 측정
    """

    total_size = 0

    for root, dirs, files in os.walk(path):
        for i in files:
            path = os.path.join(root, i)
            total_size += os.path.getsize(path)
            main_prog.num = total_size

    return total_size


def get_root_size(path):
    """ 루트 폴더 내의 파일 용량만 측정 """
    total_size = 0

    for root, _, files in os.walk(path):
        break 
    
    for i in files:
        path = os.path.join(root, i)
        total_size += os.path.getsize(path)
        main_prog.num = total_size

    return total_size


