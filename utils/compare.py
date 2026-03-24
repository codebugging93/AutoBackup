import os

from utils.filecmp_modified import auto_set_filter, cmp_filter
from utils.path import get_dir_size, get_filename_set, cut_path, get_path_info, get_root_files_count, get_root_size, merge_path
from utils.DepthList import DepthList, get_depth, is_dlist_equal
from utils.constants import CMP_STATS, CMP_MODES



def compare(path1, path2, compare_mode):
    # path1, path2에 대해 수행
    dlist1, folders1, files1, size1 = load_folder(path1, compare_mode)
    dlist2, folders2, files2, size2 = load_folder(path2, compare_mode)

    # check_folder에 해당하는 코드 
    dlist_same = dlist1.intersection(dlist2) # 공통의 폴더. S = A & B
    dlist_copy = dlist1.difference(dlist_same) # 복사할 폴더. A - S
    dlist_rmv = dlist2.difference(dlist_same) # 삭제할 폴더. B - S

    result_copy, result_renew, result_rmv, result_same = checkfile(path1, path2, dlist_same)

    return result_copy, result_renew, result_rmv, result_same


def load_folder(path, compare_mode):
    # 트리, 폴더수, 파일수   
    if compare_mode == CMP_MODES.ALL:
        dlist, folders, files = get_path_info(path) 
    elif compare_mode == CMP_MODES.TOP_ONLY:
        dlist = DepthList()
        dlist.add("")
        folders = 0
        files = get_root_files_count(path)
    
    # 크기
    if compare_mode == CMP_MODES.ALL:
        size = get_dir_size(path)
    elif compare_mode == CMP_MODES.TOP_ONLY:
        size = get_root_size(path)

    return dlist, folders, files, size


def checkfile(path1, path2, dlist_intersection: DepthList) -> tuple[list, list, list, list]:
    """ 
    file_list를 토대로 복사/삭제/갱신/동일한 파일을 
    data에 등록한다.
    compare_file는 cmp 함수와 비슷하다.
    """
    path1_depth = get_depth(path1)
    path2_depth = get_depth(path2)
    result_copy, result_renew, result_rmv, result_same = [], [], [], []

    auto_set_filter() # 검사 속도 향상

    # 오름차순으로 탐색. dlist의 첫번째 항목부터 차례로 순회한다.
    for cut in dlist_intersection.flatten():
        # 폴더 절대경로
        folder1 = merge_path(path1, cut)
        folder2 = merge_path(path2, cut)

        # 이름만 같은 파일을 추출함
        org_set = get_filename_set(folder1)
        tar_set = get_filename_set(folder2)
        same_set = org_set & tar_set

        # 같은 파일중에서 진짜 같은 파일을 추려냄
        for f in same_set:
            # 파일 경로
            file1 = os.path.join(folder1, f)
            file2 = os.path.join(folder2, f)
            cut = cut_path(file1, path1_depth) # 경로를 잘라서 보관함 (메모리 절약)

            # 비교
            if cmp_filter(file1, file2): # 내용이 동일함
                result_same.append(cut) # 같은 파일로 넣음
            else: # 내용이 다름
                result_renew.append(cut) # 갱신할 파일로 넣음

        # 복사할 파일을 추출함 (A - S)
        temp = org_set - same_set
        for fname in temp:
            fpath = os.path.join(folder1, fname)
            cut = cut_path(fpath, path1_depth)
            result_copy.append(cut)

        # 삭제할 파일을 추출함 (B - S)
        temp = tar_set - same_set
        for fname in temp:
            fpath = os.path.join(folder2, fname)
            cut = cut_path(fpath, path2_depth)
            result_rmv.append(cut)

    return result_copy, result_renew, result_rmv, result_same



def get_intersection_result(dlist_1: DepthList, 
                dlist_2: DepthList,
                dlist_intersect: DepthList) -> CMP_STATS:
    # 트리 비교
    folders = dlist_intersect.count()

    if is_dlist_equal(dlist_1, dlist_2, dlist_intersect):
        return CMP_STATS.SAME
    elif folders == 1:
        return CMP_STATS.NOTSAME
    else:
        return CMP_STATS.PARTIAL
    

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
    

def get_state_message(state) -> str:
    if state == CMP_STATS.SAME:
        msg = "완전 일치"
    elif state == CMP_STATS.NOTSAME:
        msg = "불일치"
    elif state == CMP_STATS.PARTIAL:
        msg = "부분 일치"
    elif state == CMP_STATS.ROOT:
        msg = "단일 폴더"
    else:
        msg = "CMP_STATS 오류"
        
    return "폴더 구조 : " + msg


