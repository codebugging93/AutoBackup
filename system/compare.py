import os

from system.SystemValues import SystemValues
from system.filecmp_modified import auto_set_filter, cmp_shallow, do_cmp
from system.path import ListdirSplitResult, get_listdir_split, norm_max_path


class CompareResult:
    """
    dirs_copy: 복사할 폴더가 포함된 절대경로 리스트
    dirs_rmv: 삭제할 폴더가 포함된 절대경로 리스트
    dirs_same: 공통된 디렉토리가 포함된 상대경로 리스트

    dirs_copy와 dirs_rmv에 들어있는 디렉토리는 서브디렉토리를 포함한 폴더이며,
    dirs_same은 서브디렉토리를 모두 따로따로 저장하여 길이가 길다.

    files_copy: 복사할 파일이 포함된 절대경로 리스트
    files_rmv: 삭제할 파일이 포함된 절대경로 리스트
    files_renew: 갱신할 파일이 포함된 절대경로 리스트
    files_same: 동일한 파일이 포함된 상대경로 리스트

    dirs_similarity: 폴더 이름 기준 유사도(백분율)
    files_similarity: 파일 이름 기준 유사도(백분율)

    두 유사도는 잴 대상이 아예 없으면 -1을 담는다.
    (양쪽 모두 하위 폴더가 없거나, 공통 폴더 안에 파일이 하나도 없는 경우)
    겹치는 것이 없어서 0%인 것과 셀 대상 자체가 없는 것은 다른 상황이므로 구분한다.

    dirs_intersection_set_count : 폴더 이름 기준 교집합의 크기
    dirs_universal_set_count    : 폴더 이름 기준 전체집합의 크기
    files_intersection_set_count: 파일 이름 기준 교집합의 크기
    files_universal_set_count   : 파일 이름 기준 전체집합의 크기

    위 네 값은 유사도를 계산할 때 쓴 값이다.
    여러 result의 유사도를 합칠 때는 백분율끼리 더할 수 없으므로 이 값들을 더해서 다시 계산한다.

    optimized_count: 최적화된 파일의 개수 (optimized_percent의 분자, 분모는 len(files_same))

    optimized_percent: 최적화된 파일의 비율(백분율)
    """

    def __init__(self):
        self.org_path = ""
        self.tar_path = ""
        self.cache = []

        self.dirs_copy = []
        self.dirs_rmv = []
        self.dirs_same = []
        self.dirs_similarity = -1.0 # -1은 잴 대상이 없다는 뜻
        self.files_similarity = -1.0

        self.dirs_intersection_set_count = 0
        self.dirs_universal_set_count = 0
        self.files_intersection_set_count = 0
        self.files_universal_set_count = 0

        self.files_copy = []
        self.files_rmv = []
        self.files_renew = []
        self.files_same = []

        self.optimized_percent = 0.0
        self.optimized_count = 0


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

        print("폴더 유사도 :", self.dirs_similarity)
        print("파일 유사도 :", self.files_similarity)
        print("최적화율 :", self.optimized_percent)


    def is_empty(self):
        return (
            len(self.dirs_copy) +
            len(self.dirs_rmv) +
            len(self.dirs_same) +
            len(self.files_copy) +
            len(self.files_rmv) +
            len(self.files_renew) +
            len(self.files_same)
        ) == 0
    



def compare(org_path, tar_path, fast_scan=True, root_only=False, skip_hidden=False):
    auto_set_filter(tar_path) # 검사 속도 향상

    # 260자 경로 제한 버그 해결
    org_path = norm_max_path(org_path)
    tar_path = norm_max_path(tar_path)

    # 비교할 폴더 계산, 파일 수 계산등의 전처리 작업
    pre_result = compare_preprocessing(org_path, tar_path, root_only, skip_hidden) # 이 result가 반환될 객체임
    # 공통 폴더 내에서 파일 비교
    result = compare_files(pre_result, fast_scan=fast_scan)    

    return result


def compare_preprocessing(org_path, tar_path, root_only=False, skip_hidden=False):
    """
    폴더 비교를 끝내고, 이어질 파일 비교(compare_files)에 필요한 준비까지 마친
    CompareResult를 반환한다.

    org_path는 백업하려는 원본 폴더, tar_path는 덮어씌울 대상 폴더이며 둘 다 절대경로다.

    root_only=True이면 루트 바로 아래의 파일만 다룬다.
        루트의 폴더는 없는 것으로 취급하므로 분류되지도, 내려가지도, 유사도에 세지도 않는다.
        따라서 dirs_copy / dirs_rmv는 비어 있고, dirs_same은 [""]이며, dirs_similarity는 -1이다.

    skip_hidden=True이면 숨김 속성이 붙은 항목을 없는 것으로 취급한다. (get_listdir_split 참고)

    양쪽에 모두 존재하는 폴더만 너비 우선으로 따라 내려가면서, 폴더마다 아래 네 가지를 한다.

    1. 폴더 분류
        dirs_copy: 원본에만 있는 폴더 (절대경로)
        dirs_rmv : 대상에만 있는 폴더 (절대경로)
        dirs_same: 양쪽에 다 있는 폴더 (상대경로, 첫 원소는 루트를 뜻하는 "")

        한쪽에만 있는 폴더는 통째로 복사/삭제할 대상이라 그 안으로는 내려가지 않는다.
        따라서 그 안의 파일은 캐시에도, 유사도 계산에도 들어가지 않는다.
        dirs_same은 너비 우선 탐색의 결과이므로 depth 오름차순으로 정렬되어 있다.

    2. 유사도 계산 (이름 기준 자카드, 백분율)
        dirs_similarity : 폴더 이름 기준
        files_similarity: 파일 이름 기준

        이름이 같으면 내용이 달라도 양쪽에 대응하는 것이 있다는 뜻이므로 교집합으로 센다.
        잴 대상이 아예 없으면 0%가 아니라 -1을 담는다.
        (겹치는 것이 없어서 0%인 것과, 셀 대상 자체가 없는 것은 다른 상황이기 때문이다.)

    3. 진행률 준비
        compare_files가 실제로 비교하게 될 파일 수를
        SystemValues.bottom_progress_max에 더해둔다. (진행 화면의 아랫줄)

    4. 캐시 (result.cache)
        (공통 폴더의 상대경로, 원본 목록, 대상 목록, 공통 파일 이름)을 폴더마다 담아둔다.
        compare_files가 이것을 그대로 이어받으므로 같은 폴더를 두 번 스캔하지 않아도 된다.

    파일의 내용 비교는 여기서 하지 않는다.
    반환된 결과의 files_copy / files_rmv / files_renew / files_same은 비어 있으며,
    이어서 실행하는 compare_files가 채운다.
    """
    # 리턴값 
    return_copy = []
    return_rmv = []
    return_same = [""] # 루트 폴더를 의미하는 공백 경로를 넣었다.
                # '.'이 아니라 공백인 이유는, os.path.join(org_path, i)를 실행하기 위해서이다.
    return_cache = [] 

    # 각종 측정값
    dirs_universal_set_count = 0
    dirs_intersection_set_count = 0
    files_universal_set_count = 0
    files_intersection_set_count = 0

    next_scan = [""] # 검사해야할 폴더이며, 루트 폴더를 의미하는 ""를 추가하였음
    while len(next_scan) > 0:  # 같은 폴더 산출
        same_folder = next_scan.pop(0) # org_path와 tar_path에 동시에 들어있는 폴더의 상대경로        
        org_dir = os.path.join(org_path, same_folder) # 절대경로 
        tar_dir = os.path.join(tar_path, same_folder) # 절대경로

        try:
            org_entries = get_listdir_split(org_dir, skip_hidden)
            tar_entries = get_listdir_split(tar_dir, skip_hidden)
        except PermissionError:
            # 사용자가 선택한 폴더 자체가 문제인 경우 에러를 띄워 검사를 중단시킴
            if same_folder == "":
                raise 

            # 교집합과 전체집합에서 각각 1씩 뺌
            return_same.remove(same_folder) 
            dirs_intersection_set_count -= 1
            dirs_universal_set_count -= 1 
            continue

        org_dirs = org_entries.dirs.keys()
        tar_dirs = tar_entries.dirs.keys()
        if root_only: # 루트의 파일만 다루므로 폴더는 없는 것으로 취급한다
            org_dirs = set()
            tar_dirs = set()
        common_name_dirs = org_dirs & tar_dirs # key끼리 교집합 가능함

        # 복사할 폴더
        for i in (org_dirs - common_name_dirs):
            p = os.path.join(org_dir, i) # 복사할것은 org쪽 저장장치에 있음
            return_copy.append(p) # 절대경로 

        # 삭제할 폴더
        for i in (tar_dirs - common_name_dirs):
            p = os.path.join(tar_dir, i) # 삭제할것은 tar쪽 저장장치에 있음
            return_rmv.append(p) # 절대경로 

        # 공통의 폴더
        for i in common_name_dirs:
            p = os.path.join(same_folder, i)
            return_same.append(p) # 상대경로
            next_scan.append(p) # 다음 검사할 항목으로 추진

        # 파일 개수 측정
        org_files = org_entries.files.keys()
        tar_files = tar_entries.files.keys()
        common_name_files = org_files & tar_files # key끼리 교집합 가능함
        # key의 집합이므로 이 key를 가지고 org_files나 tar_files쪽을 조회할 수 있음
        
        # 유사도 측정
        dirs_intersection_set_count += len(common_name_dirs)
        dirs_universal_set_count += len(org_dirs) + len(tar_dirs) - len(common_name_dirs)
        files_intersection_set_count += len(common_name_files)
        files_universal_set_count += len(org_files) + len(tar_files) - len(common_name_files)

        # 진행률 반영
        SystemValues.bottom_progress_max += len(common_name_files) # 공통 이름의 파일을 가지고 compare_files에서 작업함 
        return_cache.append((same_folder, org_entries, tar_entries, common_name_files))

    # 결과물 제작
    result = CompareResult()
    result.org_path = org_path
    result.tar_path = tar_path
    result.cache = return_cache

    result.dirs_copy = return_copy
    result.dirs_rmv = return_rmv 
    result.dirs_same = return_same

    # 유사도 계산에 쓰는 집합 크기도 함께 기록한다.
    result.dirs_intersection_set_count = dirs_intersection_set_count
    result.dirs_universal_set_count = dirs_universal_set_count
    result.files_intersection_set_count = files_intersection_set_count
    result.files_universal_set_count = files_universal_set_count

    # 폴더 유사도 계산
    if dirs_universal_set_count != 0:
        result.dirs_similarity = dirs_intersection_set_count / dirs_universal_set_count * 100
    else:
        result.dirs_similarity = -1.0 # 양쪽 모두 하위 폴더가 없음

    # 파일 유사도 계산
    if files_universal_set_count != 0:
        result.files_similarity = files_intersection_set_count / files_universal_set_count * 100
    else:
        result.files_similarity = -1.0 # 공통 폴더 안에 파일이 하나도 없음

    return result


def compare_one_file(org_entry: os.DirEntry, tar_entry: os.DirEntry, fast_scan=True) -> bool:
    """
    이름이 같은 파일 하나를 비교해서, 내용이 같으면 True를 반환한다.

        1. cmp_shallow로 크기와 수정시간만 보고 빠르게 판정을 시도한다.
        2. 그것으로 결론이 나지 않으면(None) do_cmp로 내용을 직접 비교한다.
    정밀검사(fast_scan=False)일 때는 1단계를 건너뛰고 반드시 내용을 비교한다.

    빠른 검사가 가능한 파일(크기와 수정시간이 같고, 실제로도 같은 파일)이면
    SystemValues.optimized_count를 1 올린다. (정밀검사에서도 최적화율을 재기 위해)
    """
    org_stat = org_entry.stat(follow_symlinks=False)
    tar_stat = tar_entry.stat(follow_symlinks=False)

    # 1단계: 크기와 수정시간만으로 빠르게 판정을 시도한다.
    is_same = None
    if fast_scan:
        is_same = cmp_shallow(org_stat, tar_stat)
        if is_same:
            SystemValues.optimized_count += 1 # 빠른 반환이 가능한 파일(최적화 된 파일)을 셈

    # 2단계: 결론이 나지 않았으면 내용을 직접 비교한다.
    if is_same is None:
        is_same = do_cmp(org_entry.path, tar_entry.path)
        if is_same and cmp_shallow(org_stat, tar_stat):
            SystemValues.optimized_count += 1 # 빠른 반환이 가능한 파일(최적화 된 파일)을 셈

    return is_same


def compare_files(preprocessing_result:CompareResult, fast_scan=True):
    """
    compare_preprocessing()가 만들어둔 캐시를 이어받아, 공통 폴더 안의 파일을 비교한다.

    캐시에는 폴더를 훑을 때 얻은 DirEntry가 그대로 들어있다.
    엔트리는 크기와 수정시간을 이미 들고 있고 전체 경로(entry.path)도 알고 있으므로,
    파일마다 os.stat을 다시 부르거나 경로를 os.path.join으로 다시 만들 필요가 없다.

    파일 하나의 판정은 compare_one_file에 맡긴다.

    반환값은 (복사할 파일, 삭제할 파일, 갱신할 파일, 동일한 파일)이 포함된 result이며,
    동일한 파일만 상대경로이고 나머지 셋은 절대경로이다.

    최적화된 파일의 개수를 측정하여 SystemValues.optimized_count에 저장한다.
    """
    SystemValues.optimized_count = 0 # 최적화율 측정

    return_copy, return_renew, return_rmv, return_same = [], [], [], []

    for values in preprocessing_result.cache:
        # values의 rel_path는 오름차순으로 길이가 길어진다고 가정한다.
        rel_path = values[0] # org_path와 tar_path에 동시에 들어있는 폴더의 상대경로
        org_entries: ListdirSplitResult = values[1]
        tar_entries: ListdirSplitResult = values[2]

        common_names = values[3] # 동일 이름의 집합

        # 이름이 동일하면서 내용까지 동일한지 검사함
        for fname in common_names:
            rel_file = os.path.join(rel_path, fname) # 상대 경로
            SystemValues.bottom_progress_path = rel_file

            # common_names는 공통된 파일의 이름을 갖고있고, 
            # fname 자체가 org_entries와 tar_entries를 조회할수 있는 key이다.
            org_entry = org_entries.files[fname]
            tar_entry = tar_entries.files[fname]
            is_same = compare_one_file(org_entry, tar_entry, fast_scan)

            if is_same: # 내용이 동일하면 같은 파일
                return_same.append(rel_file) # 상대 경로로 저장
            else: # 내용이 다르다면 갱신할 파일
                return_renew.append(tar_entry.path) # 갱신될 파일의 절대 경로로 저장

            SystemValues.bottom_progress_val += 1
            #진행이 될떄 값이 1씩 추가됨

        # 복사할 파일을 추출함 
        org_files = org_entries.files
        for fname in (org_files.keys() - common_names):
            return_copy.append(org_files[fname].path) # 복사할 파일은 원본에 존재함

        # 삭제할 파일을 추출함
        tar_files = tar_entries.files
        for fname in (tar_files.keys() - common_names):
            return_rmv.append(tar_files[fname].path) # 삭제할 파일은 타겟에 존재함

    # 결과 정리
    result = preprocessing_result
    result.files_copy = return_copy
    result.files_rmv = return_rmv
    result.files_renew = return_renew
    result.files_same = return_same
    result.optimized_count = SystemValues.optimized_count # 여러 result의 최적화율을 합칠 때 쓴다

    # 최적화율 계산
    if len(result.files_same) != 0:
        result.optimized_percent = SystemValues.optimized_count / len(result.files_same) * 100
    else:
        result.optimized_percent = 0

    return result


def get_files_similarity(results: list[CompareResult]) -> float:
    """
    여러 result의 교집합/전체집합 크기를 모두 더해서 파일 이름 기준 종합 유사도(백분율)를 계산한다.
    셀 파일이 하나도 없으면 -1을 반환한다.
    """
    intersection = 0
    universal = 0
    for result in results:
        intersection += result.files_intersection_set_count
        universal += result.files_universal_set_count

    if universal == 0:
        return -1.0
    return intersection / universal * 100


def get_dirs_similarity(results: list[CompareResult]) -> float:
    """
    여러 result의 교집합/전체집합 크기를 모두 더해서 폴더 이름 기준 종합 유사도(백분율)를 계산한다.
    셀 폴더가 하나도 없으면 -1을 반환한다.
    """
    intersection = 0
    universal = 0
    for result in results:
        intersection += result.dirs_intersection_set_count
        universal += result.dirs_universal_set_count

    if universal == 0:
        return -1.0
    return intersection / universal * 100


def get_optimized_percent(results: list[CompareResult]) -> float:
    """
    여러 result의 최적화된 파일 수와 동일한 파일 수를 모두 더해서 종합 최적화율(백분율)을 계산한다.
    동일한 파일이 하나도 없으면 0을 반환한다. (compare_files와 같은 규칙)
    """
    optimized = 0
    same = 0
    for result in results:
        optimized += result.optimized_count
        same += len(result.files_same)

    if same == 0:
        return 0.0
    return optimized / same * 100


def merge_results(org_path, tar_path, results: list[CompareResult]) -> CompareResult:
    """
    여러 result의 복사/삭제/갱신 목록(절대경로)을 org_path/tar_path 기준의 result 하나로 합친다.
    results의 모든 경로는 org_path/tar_path 안에 있어야 한다.
    same 목록은 상대경로라서 합치지 않는다.
    """
    merged = CompareResult()
    # compare와 똑같이 260자 경로 제한 접두사를 붙여, 목록의 경로들과 깊이를 맞춘다
    merged.org_path = norm_max_path(org_path)
    merged.tar_path = norm_max_path(tar_path)
    for result in results:
        merged.dirs_copy.extend(result.dirs_copy)
        merged.dirs_rmv.extend(result.dirs_rmv)
        merged.files_copy.extend(result.files_copy)
        merged.files_rmv.extend(result.files_rmv)
        merged.files_renew.extend(result.files_renew)
    return merged
