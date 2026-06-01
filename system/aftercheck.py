import os
from time import sleep, time

from system.SystemValues import SystemValues
from system.compare import CompareResult, compare
from system.DepthList import get_depth
from system.path import cut_path
from system.filecmp_modified import cmp_filter


def aftercheck(compare_result: CompareResult, fast_scan=True):
    """ 
    CompareResult의 각 항목이 제대로 작업되었는지 확인한다.
    
    dirs_copy: 존재하지 않으면 failed.dirs_copy에 넣고,
        존재한다면 compare한 결과를 받은 후에, 모두 failed에 넣는다.(절대경로이므로)
    dirs_rmv: 삭제되지 않고 존재한다면 failed.dirs_rmv에 넣는다.
    files_copy: 존재하지 않으면 failed.files_copy에 넣고, 
        존재하는데 다르면 failed.files_renew에 넣는다. 
    files_rmv: 존재한다면 failed.files_rmv에 넣는다.
    files_renew: files_copy와 동일하게 처리한다.
    """
    SystemValues.backup_progress_val = 0
    SystemValues.backup_progress_max = 0
    SystemValues.backup_progress_msg = ""
    SystemValues.backup_progress_path = ""
    
    # 결과를 모으기 위한 지역 변수 리스트들
    files_rmv = []
    dirs_rmv = []
    files_copy = []
    files_renew = []
    dirs_copy = []

    # 1. 파일 삭제 확인
    SystemValues.backup_progress_msg = "파일 삭제 확인 중"
    files_rmv.extend(aftercheck_files_rmv(compare_result.files_rmv))

    # 2. 폴더 삭제 확인
    SystemValues.backup_progress_msg = "폴더 삭제 확인 중"
    dirs_rmv.extend(aftercheck_dirs_rmv(compare_result.dirs_rmv))

    # 3. 파일 복사 확인 
    SystemValues.backup_progress_msg = "파일 복사 확인 중"
    result = aftercheck_files_copy(
        compare_result.org_path, compare_result.tar_path, 
        compare_result.files_copy, fast_scan
    )
    files_copy.extend(result.files_copy)
    files_renew.extend(result.files_renew)

    # 4. 파일 갱신 확인
    SystemValues.backup_progress_msg = "파일 갱신 확인 중"
    result = aftercheck_files_renew(
        compare_result.org_path, compare_result.tar_path, 
        compare_result.files_renew, fast_scan
    )
    files_copy.extend(result.files_copy)
    files_renew.extend(result.files_renew)

    # 5. 폴더 복사 확인 (재귀적으로 내부 파일 및 폴더 검사 결과 병합)
    SystemValues.backup_progress_msg = "폴더 복사 확인 중"
    result = aftercheck_dirs_copy(
        compare_result.org_path, compare_result.tar_path, 
        compare_result.dirs_copy, fast_scan
    )
    dirs_copy.extend(result.dirs_copy)
    dirs_rmv.extend(result.dirs_rmv)
    files_copy.extend(result.files_copy)
    files_rmv.extend(result.files_rmv)
    files_renew.extend(result.files_renew)

    # 최종적으로 리스트 대입
    failed_result = CompareResult()
    failed_result.org_path = compare_result.org_path
    failed_result.tar_path = compare_result.tar_path
    failed_result.files_rmv = files_rmv
    failed_result.dirs_rmv = dirs_rmv
    failed_result.files_copy = files_copy
    failed_result.files_renew = files_renew
    failed_result.dirs_copy = dirs_copy

    return failed_result


def aftercheck_files_rmv(files: list):
    """ 
    절대경로 리스트 files의 파일들이 
    제대로 삭제되었는지 확인한다.
    """
    failed_files = []
    SystemValues.backup_progress_val = 0
    SystemValues.backup_progress_max = len(files)

    for src in files:
        SystemValues.backup_progress_path = src
        if os.path.exists(src): # 삭제한줄 알았던 파일이 존재하고,
            # exists만으로는 대소문자까지 일치하는지 확인할 수 없다.
            if os.path.basename(src) == os.path.basename(os.path.realpath(src)): # 대소문자까지 비교하여 완전 동일한 파일이면 
                failed_files.append(src) # 실패한 파일로 넣음
        SystemValues.backup_progress_val += 1

    return failed_files


def aftercheck_files_copy(org_path, tar_path, files: list, fast_scan=True):
    """ 
    org_path 내의 절대경로 리스트 files의 파일들이 
    tar_path로 제대로 복사되었는지 compare해본다.
    """
    failed = CompareResult()
    SystemValues.backup_progress_val = 0
    SystemValues.backup_progress_max = len(files)

    for src in files:
        cut = cut_path(src, get_depth(org_path))
        dst = os.path.join(tar_path, cut)
        SystemValues.backup_progress_path = src

        try: 
            if not cmp_filter(src, dst, fast_scan):
                # 파일이 있는데 일치하지 않을 때는 갱신해야함
                failed.files_renew.append(dst)
        except FileNotFoundError:
            # 파일이 없을 때는 복사해야함 
            failed.files_copy.append(src)
        SystemValues.backup_progress_val += 1

    return failed


def aftercheck_files_renew(org_path, tar_path, files: list, fast_scan=True):
    """ 
    tar_path 내의 절대경로 리스트 files의 파일들이 
    org_path로부터 제대로 갱신되었는지 compare해본다.
    """
    failed = CompareResult()
    SystemValues.backup_progress_val = 0
    SystemValues.backup_progress_max = len(files)

    for dst in files:
        cut = cut_path(dst, get_depth(tar_path))
        src = os.path.join(org_path, cut)
        SystemValues.backup_progress_path = cut

        try: 
            if not cmp_filter(src, dst, fast_scan):
                # 파일이 있는데 일치하지 않을 때는 갱신해야함
                failed.files_renew.append(dst)
        except FileNotFoundError:
            # 파일이 없을 때는 복사해야함 
            failed.files_copy.append(src)
        SystemValues.backup_progress_val += 1

    return failed


def aftercheck_dirs_rmv(dirs: list):
    """ 
    절대경로 리스트 dirs의 폴더들이 
    제대로 삭제되었는지 확인한다.
    """
    failed_dirs = [] 
    SystemValues.backup_progress_val = 0
    SystemValues.backup_progress_max = len(dirs)

    for src in dirs:
        SystemValues.backup_progress_path = src
        if os.path.exists(src): # 삭제한줄 알았던 폴더가 존재하고,
            # exists만으로는 대소문자까지 일치하는지 확인할 수 없다.
            if os.path.basename(src) == os.path.basename(os.path.realpath(src)): # 대소문자까지 비교하여 완전 동일한 폴더이면
                failed_dirs.append(src) # 실패한 폴더로 넣음
        SystemValues.backup_progress_val += 1

    return failed_dirs


def aftercheck_dirs_copy(org_path, tar_path, dirs: list, fast_scan=True) -> CompareResult:
    """ 
    org_path 내의 절대경로 리스트 dirs의 폴더들이 
    tar_path로 제대로 복사되었는지 compare해본다.
    """
    failed_result = CompareResult()
    SystemValues.backup_progress_val = 0
    SystemValues.backup_progress_max = len(dirs)
    
    for src in dirs:
        cut = cut_path(src, get_depth(org_path))
        dst = os.path.join(tar_path, cut)
        SystemValues.backup_progress_path = src
        
        if not os.path.exists(dst):
            failed_result.dirs_copy.append(src)
            continue

        # 다양한 결과가 나오게 됨
        _result = compare(src, dst, fast_scan=fast_scan)
        failed_result.dirs_copy.extend(_result.dirs_copy)
        failed_result.dirs_rmv.extend(_result.dirs_rmv)
        failed_result.files_copy.extend(_result.files_copy)
        failed_result.files_rmv.extend(_result.files_rmv)
        failed_result.files_renew.extend(_result.files_renew)
        SystemValues.backup_progress_val += 1

    return failed_result