from enum import Enum


# 자동 경로 설정
APPNAME = "AutoBackup"
VERSION = "0.2"
SUISEI_BLUE = "#75B7EA"


class BACKUP_MODES(Enum):
    """ 백업 선택 모드 """
    FILE = 6000
    ALL = 6001
    BOOST = 6002


class CMP_MODES(Enum):
    """ 비교 선택 모드 """
    ALL = 7000
    TOP_ONLY = 7001


class CMP_STATS(Enum):
    """ 검사를 하고 난 후 original과 target을 비교한 결과 모음 """
    SAME = 10
    PARTIAL = 11
    NOTSAME = 12
    ROOT = 13

