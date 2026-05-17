from enum import Enum

from system.compare import CompareResult

class CheckMode(Enum):
    FAST = 0
    DEEP = 1

class AppData:
    original_path = None
    target_path = None
    check_mode = None
    compare_result: CompareResult | None = None

    