import os

from system.byte import convert_byte
from system.filecmp_modified import auto_set_filter, cmp_filter
from system.path import get_dirname_set, get_filename_set, merge_path


class CompareResult:
    """
    dirs_copy: 복사할 폴더가 포함된 절대경로 리스트
    dirs_rmv: 삭제할 폴더가 포함된 절대경로 리스트
    dirs_same: 공통된 디렉토리가 포함된 상대경로 리스트

    dirs_copy와 dirs_rmv에 들어있는 디렉토리는 서브디렉토리를 포함한 폴더이며,
    dirs_same은 서브디렉토리를 모두 따로따로 저장하여 길이가 길다.

    files_copy: 복사할 파일이 포함된 절대경로 리스트
    files_rmv: 삭제할 파일이 포함된 절대경로 리스트
    files_renew: 갱신할 파일이 포함된 상대경로 리스트
    files_same: 동일한 파일이 포함된 상대경로 리스트

    상대경로/절대경로의 기준
        원본 폴더와 대상 폴더중 한쪽에만 들어있는 요소(복사/삭제)는 절대경로
        양쪽에 들어있는 요소(갱신/동일)의 경우에는 상대경로
    """

    def __init__(self):
        self.org_path = ""
        self.tar_path = ""

        self.dirs_copy = [] 
        self.dirs_rmv = []
        self.dirs_same = []

        self.files_copy = []
        self.files_rmv = []
        self.files_renew = []
        self.files_same = []


    def print(self):
        print("원본 폴더: ", self.org_path)
        print("대상 폴더: ", self.tar_path)

        print("복사할 폴더 수:", len(self.dirs_copy))
        print("삭제할 폴더 수:", len(self.dirs_rmv))
        print("동일한 폴더 수:", len(self.dirs_same))
        
        print("복사할 파일 수:", len(self.files_copy))
        print("삭제할 파일 수:", len(self.files_rmv))
        print("갱신할 파일 수:", len(self.files_renew))
        print("동일한 파일 수:", len(self.files_same))



def compare(org_path, tar_path, fast_scan=True):
    auto_set_filter(tar_path) # 검사 속도 향상

    # 복사/삭제할 폴더와 공통된 폴더를 구함 
    result = compare_dirs(org_path, tar_path)
    result_files = compare_files(
        org_path, 
        tar_path, 
        result.dirs_same, 
        fast_scan=fast_scan
        )

    result.files_copy = result_files.files_copy
    result.files_rmv = result_files.files_rmv
    result.files_renew = result_files.files_renew
    result.files_same = result_files.files_same

    return result


def compare_files(org_path, tar_path, dirs_same: list, fast_scan=True):
    """ 
    org_path가 백업하고자 하는 원본 폴더(original),
    tar_path가 덮어씌우고자 하는 사본 폴더(target) 경로이다.
    둘 다 절대 경로여야 한다.
    
    dirs_same은 compare_dirs()를 토대로 얻어낸 결과이다.

    dirs_same의 값 하나하나에 대해서 파일들을 비교하여 차이점을 저장하고,
    복사/갱신/삭제/공통 파일 리스트를 반환한다.
    """
    copy, renew, rmv, same = [], [], [], []

    # dirs_same은 depth가 오름차순이 되도록 정렬되어 있다고 상정한다.
    for rel_path in dirs_same: # rel_path: 상대경로
        # 원본과 사본에 동시에 존재하는 폴더의 절대경로
        org_dir = merge_path(org_path, rel_path)
        tar_dir = merge_path(tar_path, rel_path)

        # 이름이 같은 파일을 추출함
        org_files = get_filename_set(org_dir)
        tar_files = get_filename_set(tar_dir)
        common_names = org_files & tar_files

        # 이름이 동일하면서 내용까지 동일한지 검사함
        for fname in common_names:
            # 파일 경로
            file1 = os.path.join(org_dir, fname)
            file2 = os.path.join(tar_dir, fname)

            # 비교
            fpath = os.path.join(rel_path, fname) # 상대 경로로 저장
            if cmp_filter(file1, file2, fast_scan): # 내용이 동일하면 같은 파일
                same.append(fpath) 
            else: # 내용이 다르다면 갱신할 파일
                renew.append(fpath) 

        # 복사할 파일을 추출함 (A - S)
        for fname in (org_files - common_names):
            fpath = os.path.join(org_dir, fname) # 복사할 파일은 원본에 존재함 
            copy.append(fpath) # 절대 경로로 저장

        # 삭제할 파일을 추출함 (B - S)
        for fname in (tar_files - common_names):
            fpath = os.path.join(tar_dir, fname) # 삭제할 파일은 타겟에 존재함
            rmv.append(fpath) # 절대 경로로 저장
    
    result = CompareResult()
    result.org_path = org_path
    result.tar_path = tar_path
    result.files_copy = copy
    result.files_renew = renew
    result.files_rmv = rmv 
    result.files_same = same
    return result


def compare_dirs(org_path, tar_path):

    """
    두 폴더를 비교하여 다음 결과를 반환한다.
    1. 복사할 폴더(절대경로)
    2. 삭제할 폴더(절대경로)
    3. 공통의 폴더(상대경로)
    
    폴더 안의 내용물은 고려하지 않으며, 폴더 비교 결과만 반환한다.
    결과물에는 파일은 하나도 없어야 한다. 
    
    dir_1과 dir_2는 비교하고자 하는 폴더의 절대경로(문자열)이다.
    """
    # sametree = DepthList()  # 리턴값
    # sametree[0].add("")  # 현재 폴더 추가

    # 리턴값 3개
    copy = []
    rmv = []
    same = [""] # 루트 폴더를 의미하는 공백 경로를 넣었다.
                # '.'이 아니라 공백인 이유는, same에 들어갈 경로들이 모두 상대 경로이기 때문이다.

    next_scan = [""] # 검사해야할 폴더이며, 루트 폴더를 의미하는 ""를 추가하였음
    while len(next_scan) > 0:  # 같은 폴더 산출
        folder = next_scan.pop(0) # 상대경로
        path1 = os.path.join(org_path, folder) # 절대경로 
        path2 = os.path.join(tar_path, folder) # 절대경로

        a = get_dirname_set(path1)
        b = get_dirname_set(path2)
        s = a & b

        # 복사할 폴더 a - s 
        for i in (a - s):
            p = os.path.join(path1, i) # 복사할것은 org쪽 저장장치에 있음
            copy.append(p) # 절대경로 

        # 삭제할 폴더 b - s
        for i in (b - s):
            p = os.path.join(path2, i) # 삭제할것은 tar쪽 저장장치에 있음
            rmv.append(p) # 절대경로 

        # 공통의 폴더 s 
        for i in s:
            p = os.path.join(folder, i)
            same.append(p) # 상대경로
            next_scan.append(p) # 다음 검사할 항목으로 추진

    result = CompareResult()
    result.org_path = org_path
    result.tar_path = tar_path
    result.dirs_copy = copy
    result.dirs_rmv = rmv 
    result.dirs_same = same
    return result




### 쓸모없는 쓰레기

# def load_folder(path, compare_mode):
#     # 트리, 폴더수, 파일수   
#     if compare_mode == CMP_MODES.ALL:
#         dlist, folders, files = get_path_info(path) 
#     elif compare_mode == CMP_MODES.TOP_ONLY:
#         dlist = DepthList()
#         dlist.add("")
#         folders = 0
#         files = get_root_files_count(path)
    
#     # 크기
#     if compare_mode == CMP_MODES.ALL:
#         size = get_dir_size(path)
#     elif compare_mode == CMP_MODES.TOP_ONLY:
#         size = get_root_size(path)

#     return dlist, folders, files, size



# def get_state_message(state) -> str:
#     if state == CMP_STATS.SAME:
#         msg = "완전 일치"
#     elif state == CMP_STATS.NOTSAME:
#         msg = "불일치"
#     elif state == CMP_STATS.PARTIAL:
#         msg = "부분 일치"
#     elif state == CMP_STATS.ROOT:
#         msg = "단일 폴더"
#     else:
#         msg = "CMP_STATS 오류"
        
#     return "폴더 구조 : " + msg



# def get_state(tree_same: DepthList):
#     """
#     original, target의 트리를 
#     data.tree_same에 의존하여 비교 상태를 얻는다.
#     1. original이나 target의 트리가 비어있는 경우
#     2. data.tree_same이 비어있는 경우
#     이 두가지 경우에선 반드시 불일치하는 결과가 나온다.
#     """
#     state = get_compare_state(
#         original.tree, 
#         target.tree, 
#         tree_same
#         )
#     return state


# def get_intersection_result(dlist_1: DepthList, 
#                 dlist_2: DepthList,
#                 dlist_intersect: DepthList) -> CMP_STATS:
#     # 트리 비교
#     folders = dlist_intersect.count()

#     if is_dlist_equal(dlist_1, dlist_2, dlist_intersect):
#         return CMP_STATS.SAME
#     elif folders == 1:
#         return CMP_STATS.NOTSAME
#     else:
#         return CMP_STATS.PARTIAL