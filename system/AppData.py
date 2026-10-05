from enum import Enum

from system.compare import CompareResult

class AppData:
    # original_path와 target_path는 260자 경로 제한 우회가 적용되어 있지 않으니
    # 경로 제한 문제를 피하려면 compare_results에 든 각 result의 org_path와 tar_path를 참조하세요.
    fast_scan = True
    compare_results: list[CompareResult] = [] # 폴더마다 compare한 결과들
    # compare_results를 모두 합친 종합 수치 (검사가 끝나면 run_compare에서 기록)
    dirs_similarity = -1.0 # -1은 잴 대상이 없다는 뜻
    files_similarity = -1.0
    optimized_percent = 0.0
    compare_run_time = 0.0
    backup_run_time = 0.0
    backup_success = False
    # failed_result = CompareResult()


def reset_appdata():
    AppData.fast_scan = True
    AppData.compare_results = []
    AppData.dirs_similarity = -1.0
    AppData.files_similarity = -1.0
    AppData.optimized_percent = 0.0
    AppData.compare_run_time = 0.0
    AppData.backup_run_time = 0.0
    AppData.backup_success = False
    # AppData.failed_result = CompareResult()