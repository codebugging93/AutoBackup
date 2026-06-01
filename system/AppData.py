from enum import Enum

from system.compare import CompareResult

class AppData:
    original_path = None
    target_path = None
    fast_scan = True
    compare_result: CompareResult | None = None
    failed_result: CompareResult | None = None

    
def reset_appdata():
    AppData.original_path = None
    AppData.target_path = None
    AppData.fast_scan = True
    AppData.compare_result = None
    AppData.failed_result = None