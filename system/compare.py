import os
from time import time

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

    optimized_count: files_same 중에서 빠른 검사만으로 판별된(최적화된) 파일 수
    optimized_percent: 최적화된 파일의 비율(백분율)

    최적화율을 SystemValues에 바로 쓰지 않고 이 결과 객체에 담는 이유는,
    aftercheck()가 내부적으로 compare()를 여러 번 호출하기 때문이다.
    전역에 바로 기록하면 그 중첩 호출들이 전체 검사 결과를 덮어써 버린다.
    따라서 기록은 호출하는 쪽(상위 레벨)에서 담당한다.
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

        self.files_copy = []
        self.files_rmv = []
        self.files_renew = []
        self.files_same = []

        self.optimized_percent = 0.0


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
    



def compare(org_path, tar_path, fast_scan=True):
    SystemValues.compare_progress_val = 0
    SystemValues.compare_progress_max = 0
    SystemValues.compare_progress_path = ""
    
    auto_set_filter(tar_path) # 검사 속도 향상

    # 260자 경로 제한 버그 해결
    org_path = norm_max_path(org_path)
    tar_path = norm_max_path(tar_path)

    # 비교할 폴더 계산, 파일 수 계산등의 전처리 작업
    result = compare_preprocessing(org_path, tar_path) # 이 result가 반환될 객체임
    # 공통 폴더 내에서 파일 비교
    returns = compare_files(result, fast_scan=fast_scan)    
    result.files_copy = returns[0]
    result.files_rmv = returns[1]
    result.files_renew = returns[2]
    result.files_same = returns[3]

    # 최적화율 계산
    if len(result.files_same) != 0:
        result.optimized_percent = SystemValues.optimized_count / len(result.files_same) * 100
    else:
        result.optimized_percent = 0

    return result


def compare_preprocessing(org_path, tar_path):
    """
    폴더 비교를 끝내고, 이어질 파일 비교(compare_files)에 필요한 준비까지 마친
    CompareResult를 반환한다.

    org_path는 백업하려는 원본 폴더, tar_path는 덮어씌울 대상 폴더이며 둘 다 절대경로다.

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
        SystemValues.compare_progress_max에 채워둔다.

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
    SystemValues.compare_progress_max = 0 # 작업할 파일 개수 측정
    dirs_universal_set_count = 0
    dirs_intersection_set_count = 0
    files_universal_set_count = 0
    files_intersection_set_count = 0

    next_scan = [""] # 검사해야할 폴더이며, 루트 폴더를 의미하는 ""를 추가하였음
    while len(next_scan) > 0:  # 같은 폴더 산출
        same_folder = next_scan.pop(0) # org_path와 tar_path에 동시에 들어있는 폴더의 상대경로
        org_dir = os.path.join(org_path, same_folder) # 절대경로 
        tar_dir = os.path.join(tar_path, same_folder) # 절대경로

        org_entries = get_listdir_split(org_dir) 
        tar_entries = get_listdir_split(tar_dir) 
        org_dirs = org_entries.dirs.keys()
        tar_dirs = tar_entries.dirs.keys()
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
        SystemValues.compare_progress_max += len(common_name_files) # 공통 이름의 파일을 가지고 compare_files에서 작업함 
        return_cache.append((same_folder, org_entries, tar_entries, common_name_files))

    # 결과물 제작
    result = CompareResult()
    result.org_path = org_path
    result.tar_path = tar_path
    result.cache = return_cache

    result.dirs_copy = return_copy
    result.dirs_rmv = return_rmv 
    result.dirs_same = return_same

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


def compare_files(preprocessing_result:CompareResult, fast_scan=True):
    """
    compare_preprocessing()가 만들어둔 캐시를 이어받아, 공통 폴더 안의 파일을 비교한다.

    캐시에는 폴더를 훑을 때 얻은 DirEntry가 그대로 들어있다.
    엔트리는 크기와 수정시간을 이미 들고 있고 전체 경로(entry.path)도 알고 있으므로,
    파일마다 os.stat을 다시 부르거나 경로를 os.path.join으로 다시 만들 필요가 없다.

    파일 하나를 판정하는 순서는 다음과 같다.
        1. cmp_shallow로 크기와 수정시간만 보고 빠르게 판정을 시도한다.
        2. 그것으로 결론이 나지 않으면(None) do_cmp로 내용을 직접 비교한다.
    정밀검사(fast_scan=False)일 때는 수정시간이 같아도 믿지 않고,
    크기만 확인한 뒤 반드시 내용을 비교한다.

    반환값은 (복사할 파일, 삭제할 파일, 갱신할 파일, 동일한 파일) 순서이며,
    동일한 파일만 상대경로이고 나머지 셋은 절대경로이다.

    최적화된 파일의 개수를 측정하여 SystemValues.optimized_count에 저장한다.
    (cmp_shallow가 빠르게 True를 반환할 때마다 그 안에서 1씩 올라간다.
     따라서 정밀검사에서는 최적화율이 잡히지 않는다.)
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
            SystemValues.compare_progress_path = rel_file

            # common_names는 공통된 파일의 이름을 갖고있고, 
            # fname 자체가 org_entries와 tar_entries를 조회할수 있는 key이다.
            org_entry = org_entries.files[fname]
            tar_entry = tar_entries.files[fname]
            org_stat = org_entry.stat(follow_symlinks=False)
            tar_stat = tar_entry.stat(follow_symlinks=False)

            # 1단계: 크기와 수정시간만으로 빠르게 판정을 시도한다.
            is_same = None
            if fast_scan:
                is_same = cmp_shallow(org_stat, tar_stat)
                if is_same:
                    SystemValues.optimized_count += 1 # 빠른 반환이 가능한 파일(최적화 된 파일)을 셈

            # 2단계: 결론이 나지 않았으면 내용을 직접 비교한다.
            if is_same == None:
                is_same = do_cmp(org_entry.path, tar_entry.path)

            if is_same: # 내용이 동일하면 같은 파일
                return_same.append(rel_file) # 상대 경로로 저장
            else: # 내용이 다르다면 갱신할 파일
                return_renew.append(tar_entry.path) # 갱신될 파일의 절대 경로로 저장

            SystemValues.compare_progress_val += 1
            #진행이 될떄 값이 1씩 추가됨

        # 복사할 파일을 추출함 
        org_files = org_entries.files
        for fname in (org_files.keys() - common_names):
            return_copy.append(org_files[fname].path) # 복사할 파일은 원본에 존재함

        # 삭제할 파일을 추출함
        tar_files = tar_entries.files
        for fname in (tar_files.keys() - common_names):
            return_rmv.append(tar_files[fname].path) # 삭제할 파일은 타겟에 존재함

    return return_copy, return_rmv, return_renew, return_same
