"""
가장 광범위하게 쓰이는 데이터들을 담은 모듈

포함한 내용은 다음과 같다.
data: BackupData
aftercheck_data: BackupData
configs: ConfigData
original, target: Folder
main_prog, sub_prog: Progress
"""


from system.Classes.BackupData import BackupData
from system.Classes.ConfigData import ConfigData
from system.Classes.Folder import Folder
from system.Classes.Progress import Progress


backup_data = BackupData()
aftercheck_data = BackupData()
configs = ConfigData()
original = Folder("원본")
target = Folder("대상")

main_prog = Progress()
sub_prog = Progress()


def reset_datas():
    """
    data, original, target 객체 초기화
    configs는 초기화되지 않음
    """
    backup_data.reset()
    aftercheck_data.reset()
    original.reset()
    target.reset()
