from enum import Enum

from system.compare import CompareResult

class AppData:
    # original_path와 target_path는 260자 경로 제한 우회가 적용되어 있지 않으니 
    # 경로 제한 문제를 피하려면 compare_result의 org_path와 tar_path를 참조하세요.
    fast_scan = True
    compare_result = CompareResult()
    compare_run_time = 0.0
    backup_run_time = 0.0
    backup_success = False
    # failed_result = CompareResult()

    
def reset_appdata():
    AppData.fast_scan = True
    AppData.compare_result = CompareResult()
    AppData.compare_run_time = 0.0
    AppData.backup_run_time = 0.0
    AppData.backup_success = False
    # AppData.failed_result = CompareResult()