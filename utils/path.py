""" 상위 모듈에서 FileNotFoundError를 처리해야 함 """

import os
from pathlib import Path


class DepthError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"depth는 음수일 수 없음 : {self.value}"
    

def split_path(path_string) -> list:
    """
    경로를 경로 구분자를 기준으로 쪼개어 리스트로 저장
    복호화는 Path(*path_list)

    "/storage/emulated/0/DCIM/abcde.txt"는 
    ['\\', 'storage', 'emulated', '0', 'DCIM', 'abcde.txt']가 됨
    """
    p = Path(path_string)
    return list(p.parts)


def get_depth(path):
    """ 
    A/B/C/D에서 depth = 4
    /A/B/C/D에서 depth = 5

    return len(split_path(path))를 실행할 뿐임.
    그래서 이미 path list가 있을때는 쓰지 말 것.
    """
    return len(split_path(path))


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
        return_dirs = set(dirs)
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


def add_dir_num(path, folder):
    """
    폴더가 어떤 폴더에 이미 있으면
    그 뒤에 번호를 붙인 경로를 반환한다.
    """
    return add_file_num(path, folder)


if __name__ == "__main__":
    pass






# 경로 분해/합체 테스트 코드

# p = "D:\\내 파일\\바탕화면\\스크린샷.jpg"
# o = "D:\\내 파일\\바탕화면\\스크린샷.jpg"
# cut = cut_path(p, get_depth(o))
# print(cut) # 자름

# print(merge_path(o, cut))