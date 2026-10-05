""" 상위 모듈에서 FileNotFoundError를 처리해야 함 """

import os
import stat
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

    
def get_filename_set(path):
    """
    os.listdir(path)에서 파일만 반환한다.
    """
    with os.scandir(path) as iterator:
        return {entry.name for entry in iterator if entry.is_file(follow_symlinks=False)}
        # entry.name은 파일의 이름을 의미함
        # follow_symlinks가 False이므로 심링크는 제외됨
    

def get_dirname_set(path):
    """
    os.listdir(path)에서 폴더만 반환한다.
    """
    with os.scandir(path) as iterator: 
        return {entry.name for entry in iterator if entry.is_dir(follow_symlinks=False)} 
        # entry.name은 폴더의 이름을 의미함
        # follow_symlinks가 False이므로 링크 파일은 제외됨


def get_symlink_set(path): # AI로 만들고, 검수는 하지 않았음
    """
    os.listdir(path)에서 심링크만 반환한다.
    """
    with os.scandir(path) as iterator:
        return {entry.name for entry in iterator if entry.is_symlink()}
        # is_symlink()에는 follow_symlinks 인자가 없음 (링크 자체만 보는 검사라 불필요)

# (위 세 함수를 실행한 것의 합집합) == set(os.listdir(path)) 가 성립함



class ListdirSplitResult:
    """
    get_listdir_split의 반환값. path 안의 내용물을 종류별로 나눠 담는다.

    네 개 모두 "이름 -> DirEntry" 형태의 dict이다.
    집합이 아니라 dict인 이유는 이름으로 교집합을 구하면서
    엔트리도 같이 들고 있기 위해서이다. get_listdir_split의 설명을 참고하라.
    """

    def __init__(self, path):
        self.path = path # 절대경로
        self.files: dict[str, os.DirEntry] = dict() # 파일 이름:엔트리 쌍
        self.dirs: dict[str, os.DirEntry] = dict() # 폴더 이름:엔트리 쌍
        self.links: dict[str, os.DirEntry] = dict() # 링크 이름:엔트리 쌍
        self.unknowns: dict[str, os.DirEntry] = dict() # 파일, 폴더, 링크도 아닌 것들 (처리 곤란)


def get_listdir_split(path, skip_hidden=False) -> ListdirSplitResult:
    """
    절대경로 path 안의 내용물을 파일/폴더/링크/그 외로 나눠서 ListdirSplitResult에 담아 반환한다.
        files    : 정규 파일
        dirs     : 폴더
        links    : 심볼릭 링크 (파일인지 폴더인지 따지지 않고 먼저 걸러낸다)
        unknowns : 위 셋 중 어느 것도 아닌 것 (처리 곤란)

    skip_hidden=True이면 숨김 속성이 붙은 항목을 담지 않는다.
        예: $RECYCLE.BIN, System Volume Information 등

    주의: dict끼리는 & 나 - 가 되지 않으므로 반드시 keys()를 거쳐야 한다.
        org.files.keys() & tar.files.keys() 으로 공통 key를 추출하거나 
        org.files.keys() - tar.files.keys() 으로 원본 파일에만 존재하는 key들을 추출할 수 있다.
    """

    result = ListdirSplitResult(path)

    with os.scandir(path) as iterator:
        for entry in iterator:
            if skip_hidden:
                # 링크인지 아직 모르므로 링크를 따라가지 않고 항목 자체의 속성을 본다.
                attributes = getattr(entry.stat(follow_symlinks=False), "st_file_attributes", 0)
                if attributes & stat.FILE_ATTRIBUTE_HIDDEN:
                    continue

            if entry.is_symlink():
                result.links[entry.name] = entry
            elif entry.is_file(follow_symlinks=False): 
                result.files[entry.name] = entry
            elif entry.is_dir(follow_symlinks=False):
                result.dirs[entry.name] = entry
            else:
                result.unknowns[entry.name] = entry

    return result


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


def get_drive_display_name(path: str) -> str:
    """
    path가 들어있는 장치의 이름을 윈도우 탐색기 "내 PC"에 보이는 문자열 그대로 반환한다.
    예) "로컬 디스크 (C:)", "내 USB (E:)"

    윈도우가 아니거나 이름을 얻지 못하면 빈 문자열을 반환한다.
    """
    if os.name != 'nt':
        return ""

    import ctypes
    from ctypes import wintypes

    drive = os.path.splitdrive(os.path.abspath(path))[0] # "C:" 또는 네트워크 경로면 "\\서버\공유폴더"
    if not drive:
        return ""

    class SHFILEINFOW(ctypes.Structure):
        _fields_ = [
            ("hIcon", wintypes.HANDLE),
            ("iIcon", ctypes.c_int),
            ("dwAttributes", wintypes.DWORD),
            ("szDisplayName", wintypes.WCHAR * 260),
            ("szTypeName", wintypes.WCHAR * 80),
        ]

    SHGFI_DISPLAYNAME = 0x200 # 탐색기에 보이는 이름을 달라는 옵션

    shell32 = ctypes.windll.shell32
    shell32.SHGetFileInfoW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(SHFILEINFOW), wintypes.UINT, wintypes.UINT,
    ]
    shell32.SHGetFileInfoW.restype = ctypes.c_size_t

    info = SHFILEINFOW()
    ok = shell32.SHGetFileInfoW(drive + "\\", 0, ctypes.byref(info), ctypes.sizeof(info), SHGFI_DISPLAYNAME)
    return info.szDisplayName if ok else ""






