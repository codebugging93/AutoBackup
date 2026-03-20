import os

from implemented.exFATcmp import cmp_filter, cmp
from utils.path import get_filename_set, cut_path
from implemented.main_datas import configs, original, target, main_prog, sub_prog
from implemented.DepthList import DepthList


"""
이 모듈에서는 확장성을 위해서 backup_data를 직접 참조하지 않았다.

console에서 비교를 수행하려면 
(반드시) checkloading -> checkfolder or checkfile
순서로 함수를 써야 한다.
"""


def checkloading(sametree: DepthList) -> tuple[list, int]:
    """
    original과 target사이에서 
    sametree에 들어있는 폴더만 로딩한다.
    
    사용하는 변수
    original.path, 
    target.path,
    main_prog
    """

    file_list = list()
    total = 0

    # depth가 차례대로 증가함
    for _list in sametree:
        # 특정 depth의 상대경로를 꺼냄
        for cut in _list:
            # 폴더 절대경로
            folder1 = os.path.join(original.path, cut)
            folder2 = os.path.join(target.path, cut)

            # 파일 이름만 추출
            org_set = get_filename_set(folder1)
            tar_set = get_filename_set(folder2)

            # 이름이 같은 파일 로딩
            same_set = org_set & tar_set

            # 미리 로딩
            file_list.append((cut, org_set, tar_set, same_set))

            main_prog.num += 1
            total += len(same_set)

    return file_list, total


def checkfolder(sametree: DepthList) -> tuple[DepthList, DepthList]:
    """ 
    원본 트리와 대상 트리를 비교하여 
    복사할 폴더와 삭제할 폴더를 data에 등록한다.
    이때, 상대 경로로 추가된다.
    
    사용하는 변수
    original.tree, target.tree
    """

    # ORIGINAL_SET - SAME_SET is faster than ORIGINAL_SET - TARGET_SET

    copy = original.tree.diff(sametree)
    rmv = target.tree.diff(sametree)

    return copy, rmv


def checkfile(file_list: list) -> tuple[set, set, set, set]:
    """ 
    file_list를 토대로 복사/삭제/갱신/동일한 파일을 
    data에 등록한다.
    compare_file는 cmp 함수와 비슷하다.
    
    파라미터
    original.path, target.path
    original.depth, target.depth
    main_prog, sub_prog
    """

    if configs.isexFAT:
        compare_file = cmp_filter
    else:
        compare_file = cmp

    result_copy, result_renew, result_rmv, result_same = set(), set(), set(), set()

    for values in file_list:
        root = values[0]
        org_set = values[1]  # folder1의 파일
        tar_set = values[2]  # folder2의 파일
        same_set = values[3]  # org & tar

        # 폴더 경로
        folder1 = os.path.join(original.path, root)
        folder2 = os.path.join(target.path, root)

        # 갱신/복사/삭제할 파일 선정

        # 갱신
        for f in same_set:
            # 파일 경로
            file1 = os.path.join(folder1, f)
            file2 = os.path.join(folder2, f)
            cut = cut_path(file1, original.depth)

            # 비교
            if not compare_file(file1, file2): # 갱신
                result_renew.add(cut)
            else: # 동일
                result_same.add(cut)

            main_prog.num += 1

        # 상태창 ON
        # (A | B) - (A & B)
        number = len(org_set) + len(tar_set) - 2 * len(same_set)
        sub_prog.config(num=0, total=number)
        sub_prog.on()

        # 복사
        temp = org_set - same_set
        for fname in temp:
            file_path = os.path.join(folder1, fname)
            cut = cut_path(file_path, original.depth)
            result_copy.add(cut)

            sub_prog.num += 1

        # 삭제
        temp = tar_set - same_set
        for fname in temp:
            file_path = os.path.join(folder2, fname)
            cut = cut_path(file_path, target.depth)
            result_rmv.add(cut)

            sub_prog.num += 1

        # UI 감춤
        sub_prog.off()

    return result_copy, result_renew, result_rmv, result_same
