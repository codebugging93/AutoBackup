from filecmp import cmp
import os

from implemented.exFATcmp import cmp_filter
from implemented.DepthList import DepthList
from implemented.main_datas import configs, original, target, main_prog, sub_prog
from utils.path import get_filename_set



"""
이 모듈에서는 확장성을 위해 backup_data, aftercheck_data를 직접 참조하지 않았다.
"""





def aftercheck_file_copy(set_file_copy):
    """
    파일 복사 확인 : file_copy의 원소가 target의 것과 일치하는지 확인

    복사 실패 유형
    1. 파일 복사가 안 되었음
    2. 파일이 복사가 되었으나 손상된 형태
    """

    # 초기설정
    if configs.isexFAT:
        compare_file = cmp_filter
    else:
        compare_file = cmp
    copy, renew = set(), set()

    # 재검사
    for cut in set_file_copy:
        org = os.path.join(original.path, cut)
        tar = os.path.join(target.path, cut)

        if os.path.exists(tar):
            if not compare_file(org, tar):
                renew.add(cut)
        else: # 존재하지 않는 경우
            copy.add(cut)

        main_prog.num += 1

    return copy, renew


def aftercheck_file_rmv(set_file_rmv):
    """ 파일 삭제 확인 : file_rmv의 원소가 target에 존재하지 않는지 확인   
    원본 파일이 대상 폴더에 존재하면 실패한 것으로 처리한다.


    #1 대소문자 버그
        folder.py를 삭제하고 Folder.py란 파일을 복사했다고 치자.
        그러면 folder.py가 삭제되었는지 확인할 것이고, 
        윈도우는 대소문자를 구분하지 않기 때문에 
        대상 폴더에 Folder.py가 존재함에 따라 folder.py가 삭제되지 않았다고 오판하게 된다.
        이처럼 파일의 소문자명은 같으나 대소문자가 달라진 경우에 문제가 생긴다. 
        
        그래서 "삭제 검사"를 할 때만 대소문자가 다르면 다른 파일로 간주하기로 했다.



        
    """

    rmv = set()

    # 재검사
    for cut in set_file_rmv:
        p = os.path.normpath(os.path.join(target.path, cut)) # 삭제를 시도했던 파일

        # 존재하지 않으면 잘 삭제된 것임
        if not os.path.exists(p):
            continue

        # 존재하지만, 대소문자 구성이 다르므로 다른 파일로 간주함 
        if p != os.path.realpath(p): # realpath는 실제 파일의 경로를 제공함(대소문자까지 일치하는)
            continue 

        # 존재하며, 대소문자 구성도 같은 경우 삭제에 실패한 것으로 취급
        rmv.add(cut) 
        main_prog.num += 1

    return rmv


def aftercheck_file_renew(set_file_renew):
    """ 
    파일 갱신 확인 : file_renew의 원소가 original과 target의 위치에서 일치하는지 확인 
    
    갱신 실패 유형
    1. 파일 없음  2. 파일 다름
    """

    # 초기설정
    if configs.isexFAT:
        compare_file = cmp_filter
    else:
        compare_file = cmp
    copy, renew = set(), set()

    # 재검사
    for cut in set_file_renew:
        org = os.path.join(original.path, cut)
        tar = os.path.join(target.path, cut)

        if os.path.exists(tar):
            if not compare_file(org, tar):
                renew.add(cut)
        else:  # 존재하지 않는 경우
            copy.add(cut)

        main_prog.num += 1

    return copy, renew
    

def aftercheck_tree_copy(tree_copy):
    """
    폴더 복사 확인; 폴더들이 제대로 복사가 되었는지 확인해야 한다. 즉 폴더 비교 작업은 필수불가결
    1. tree_copy의 원소가 target에 존재하는지 확인
        존재하지 않으면 FAILED_DIRS로 보냄
    2. tree_copy에서 FAILED_DIRS를 제외한 집합을 data.file_same으로 잡고, 복사/삭제해야할 파일을 다시 구함(compare 사용)
        결과물은 FAILED_FILES_COPY, FAILED_FILES_RMV로 보냄
    """

    # 초기설정
    if configs.isexFAT:
        compare_file = cmp_filter
    else:
        compare_file = cmp
    failed_tree_copy = DepthList()
    failed_files_copy = set()
    failed_files_renew = set()

    # 복사되지 않은 폴더 색출
    for dirs in tree_copy:
        for cut in dirs:
            tar = os.path.join(target.path, cut)
            if not os.path.exists(tar):
                failed_tree_copy.attach(cut, 0)
                
            main_prog.num += 1

    # 복사되지 않은 파일 색출
    main_prog.config(prefix="[폴더 복사 확인]", num=0)
    sub_prog.reset(prefix="[파일 복사 확인]")

    for dirs in tree_copy:
        for cut in dirs:
            """
            if failed_tree.exists(cut):
                main_prog.num += 1
                continue
            여기에 이 코드를 넣을 필요가 없는게
            어차피 존재하지 않는 폴더면 files가 빈 집합이 되므로 
            failed_copy가 중복될 일이 전혀 없다.
            """

            org_dir = os.path.join(original.path, cut)
            tar_dir = os.path.join(target.path, cut)
            files = get_filename_set(org_dir)
            sub_prog.config(num=0, total=len(files)) # sub_prog 수정

            for f in files:
                org_file = os.path.join(org_dir, f)
                tar_file = os.path.join(tar_dir, f)
                cut_file = os.path.join(cut, f)

                if os.path.exists(tar_file):
                    if not compare_file(org_file, tar_file):
                        failed_files_renew.add(cut_file)
                else:
                    failed_files_copy.add(cut_file)

                sub_prog.num += 1

            main_prog.num += 1

    return failed_files_copy, failed_files_renew, failed_tree_copy


# 폴더 삭제 확인
def aftercheck_tree_rmv(tree_rmv):
    """
    폴더 삭제 확인 : tree_rmv의 원소가 target에 존재하지 않는지 확인
    """

    failed_tree = DepthList()

    # 복사되지 않은 폴더 색출
    for dirs in tree_rmv:
        for cut in dirs:
            tar = os.path.join(target.path, cut)
            if os.path.exists(tar):
                failed_tree.attach(cut, 0)

            main_prog.num += 1

    return failed_tree
