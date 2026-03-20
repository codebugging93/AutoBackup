import os
from tkinter.filedialog import askdirectory


def cut_path(path, depth):
    """ 
    path에서 depth만큼 경로를 앞부분에서 자름.
    
    path = "A/B/C"이고 depth=1이면
    결과는 "B/C" 
    
    depth = 0이면 변화 X
    """

    tree = split_path(path)

    # 레이즈
    if depth < 0:
        raise DepthError(DepthError.NEGATIVE)
    elif depth > len(tree):
        raise DepthError(DepthError.UNCUTABLE)

    # 자름
    tree = tree[depth:]
    try:
        newpath = tree[0]
    except IndexError:
        return ""

    for f in tree[1:]:
        newpath = newpath + os.sep + f
    return newpath


class DepthError(Exception):
    DEEP = 0
    NEGATIVE = -1
    UNCUTABLE = 100

    def __init__(self, case):
        """ available case:
            DepthError.DEEP
            DepthError.NEGATIVE
            DepthError.UNCUTABLE """

        if case == DepthError.DEEP:
            self.msg = "The depth of the path is too deep"
        elif case == DepthError.NEGATIVE:
            self.msg = "depth must be 0 or positive"
        elif case == DepthError.UNCUTABLE:
            self.msg = "depth to cut must be smaller than or equal to the depth of the path"
        else:
            ValueError("wrong argument passed : " + str(case))

    def __str__(self):
        return self.msg
    

def split_path(path):
    """ 
    path를 os.sep을 기준으로 나눈다.
    """
    path = os.path.normpath(path)
    tree = path.split(os.sep)

    # 드라이브를 선택하는 경우 (len(tree) == 2 인 경우)
    if tree[-1] == '':
        return tree[:-1]
    elif tree[-1] == '.':
        return []
    else:
        return tree
    
    
def get_depth(path):
    """ 
    A/B/C/D에서 depth = 4
    /A/B/C/D에서 depth = 5
    """
    tree = split_path(path)
    depth = len(tree)

    return depth




def backup_boost(folder):
    """ 최적화 데이터를 만든다. """
    # 최적화 데이터 작성
    file_name = folder + "_mtime.txt"
    DEPTH = get_depth(folder)
    with open(file_name, "w", encoding="utf8") as file:
        for root, dirs, files in os.walk(folder):
            for f in files:
                org_file = os.path.join(root, f)
                org_mtime = os.stat(org_file).st_mtime
                path_cut = cut_path(org_file, DEPTH)
                file.write(f"{path_cut}:{org_mtime}\n") 

backup_boost(askdirectory())