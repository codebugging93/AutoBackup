""" 상위 모듈에서 FileNotFoundError를 처리해야 함 """

import os
from pathlib import Path
from system.depth import DepthError, get_depth, split_path



PREFIX_MAX_PATH = "\\\\?\\"


def norm_max_path(path: str):
    """ 윈도우에서만 동작하며, 
        다른 운영체제에서 실행하면 그대로 리턴한다."""
    # if len(path) < 261:
    #     return path

    if os.name != 'nt' or path.startswith(PREFIX_MAX_PATH):
        return path 
    
    return PREFIX_MAX_PATH + path


def is_dest_in_src(src, dst):
    """ 
    shutil.py의 _destinsrc 함수를 그대로 가져옴 
    src가 dst를 포함하면 True를 반환함.
    """
    src = os.path.realpath(src)
    dst = os.path.realpath(dst)
    if not src.endswith(os.path.sep):
        src += os.path.sep
    if not dst.endswith(os.path.sep):
        dst += os.path.sep
    return dst.startswith(src)


def cut_path(path, depth):
    """ 
    path에서 depth만큼 경로를 앞부분에서 자름.
    
    path = "A/B/C"이고 depth=1이면
    결과는 "B/C" 
    
    depth = 0이면 변화 X
    """
    # 음수이면 예외
    if depth < 0:
        raise DepthError(depth)

    # 경로를 자름
    tree = split_path(path)
    tree = tree[depth:]

    if len(tree) > 0:
        return str(Path(*tree)) # 상대 경로로 만듦
    else:
        return "" # len(tree) == 0일때는 아무것도 남지 않았으므로 공백으로 둠.

    # try:
    #     newpath = tree[0]
    # except IndexError:
    #     return ""

    # for f in tree[1:]:
    #     newpath = newpath + os.sep + f

    # return newpath


def merge_path(*paths):
    """ cut_path했던걸 다시 합치는 함수 """
    return str(Path(*paths))


# 경로 분해/합체 테스트 코드

# p = "D:\\내 파일\\바탕화면\\스크린샷.jpg"
# o = "D:\\내 파일\\바탕화면\\스크린샷.jpg"
# cut = cut_path(p, get_depth(o))
# print(cut) # 자름

# print(merge_path(o, cut)) # 원상복귀됨

    
def get_filename_set(path) -> set: 
    """
    os.listdir와 비슷하게, path 내의 파일 이름을 모아서 주는 함수
    """
    
    path = os.path.normpath(path)
    return_files = set()
    
    for root, dirs, files in os.walk(path):
        return_files = set(files)
        break
            
    return return_files
    

def get_dirname_set(path): 
    """ 
    os.listdir에서 폴더만 반환한다.
    """
    
    path = os.path.normpath(path)
    return_dirs = set()
    
    for root, dirs, files in os.walk(path):
        for i in dirs:
            p = os.path.join(root, i)
            if not os.path.islink(p):
                return_dirs.add(i)
        break    
        
    return return_dirs


def get_root_files_count(path):
    """ 
    최상위 폴더에 들어있는 내용중에서 
    폴더를 제외한 파일의 개수만 구한다.
    """
    res = 0

    for root, dirs, files in os.walk(path):
        res = len(files)
        break

    return res

 
def get_root_dirs_count(path):
    """ 
    최상위 폴더에 들어있는 내용중에서 
    폴더를 제외한 파일의 개수만 구한다.
    """
    res = 0

    for root, dirs, files in os.walk(path):
        res = len(dirs)
        break

    return res

def add_file_num(fname, folder):
    """
    파일이 어떤 폴더에 이미 있으면
    그 뒤에 번호를 붙인 경로를 반환한다.
    * 중복된 파일이 있을때 덮어쓰기를 방지할 수 있다.
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


def add_dir_num(path, folder):
    """
    폴더가 어떤 폴더에 이미 있으면
    그 뒤에 번호를 붙인 경로를 반환한다.
    """
    return add_file_num(path, folder)



#####################
# 다소 무거운 작업들 
#####################

# def get_path_info(path) -> tuple[DepthList, int, int]:
#     """
#     depthlist, 폴더 수, 파일 수 를 한번에 구하는 함수

#     counter.num1을 사용한다.
#     """
#     path = os.path.normpath(path)
#     path_depth = get_depth(path)

#     dlist = DepthList()
#     files = 0
#     folders = 0

#     # counter.num1 = 0
#     for root, dirs, _files in os.walk(path):
#         cut = cut_path(root, path_depth) # 처음 주어진 path의 depth만큼 경로를 자름
#         dlist.add(cut) # dlist[0]에는 처음에 빈 문자열이 들어간다. root에서 root만큼 잘라냈기 때문이다. 나중에 merge_path로 합칠 수 있으니 이상현상이 아님을 알린다.
        
#         files += len(_files)
#         folders += 1
#         # counter.num1 = folders 
#         # UI가 읽을 값

#     return dlist, folders, files


# def get_relpath_dlist(path) -> DepthList:
#     """
#     path에서부터 하위 폴더를 탐색하여
#     상대 경로(relative path, 줄여서 relpath)가 들어있는 DepthList를 반환한다.

#     counter.num1을 사용한다.
#     """

#     path = os.path.normpath(path)
#     path_depth = get_depth(path)
#     dlist = DepthList()

#     # counter.num1 = 0
#     for root, dirs, files in os.walk(path):
#         cut = cut_path(root, path_depth) 
#         dlist.add(cut) 
#         # counter.num1 += 1

#     return dlist


def get_files_relpath(path) -> list:
    """
    path에 속한 모든 파일들의 상대경로를 리스트로 반환한다.
    depth는 오름차순이다.
    """
    path = os.path.normpath(path)
    path_depth = get_depth(path)
    result = []

    for root, dirs, files in os.walk(path):
        for i in files:
            file_path = os.path.join(root, i)
            cut = cut_path(file_path, path_depth) 
            result.append(cut) 

    return result


def get_dirs_relpath(path) -> list:
    """
    path에 속한 모든 폴더들의 상대경로를 리스트로 반환한다.
    depth는 오름차순이다.
    """
    path = os.path.normpath(path)
    path_depth = get_depth(path)
    result = []

    for root, dirs, files in os.walk(path):
        cut = cut_path(root, path_depth) 
        result.append(cut) 

    return result


def get_dir_size(path) -> int:
    """ 
    폴더 path의 용량 측정 
    counter.num1을 사용한다.
    """
    total_size = 0

    # counter.num1 = 0
    for root, dirs, files in os.walk(path):
        for i in files:
            path = os.path.join(root, i)
            total_size += os.path.getsize(path)
            # counter.num1 = total_size

    return total_size


def get_root_size(path) -> int:
    """ 
    루트 폴더의 파일 용량만 측정 
    counter.num1을 사용한다.
    """
    # get_dir_size에서 break만 추가한 코드다.

    total_size = 0

    # counter.num1 = 0
    for root, dirs, files in os.walk(path):
        for i in files:
            path = os.path.join(root, i)
            total_size += os.path.getsize(path)
            # counter.num1 = total_size
        break # 여기가 추가됨

    return total_size






