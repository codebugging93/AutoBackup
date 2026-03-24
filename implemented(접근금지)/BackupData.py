from system.DepthList import DepthList


class BackupData:
    """ 파일 리스트, 버튼 상태, 폴더 상태 등을 담는 클래스 """
    def __init__(self):
        self.cmp_state = None  # utils.constants.CMP_STATS가 할당될 것임
        self.set_file_renew = set()  # 갱신할 파일 리스트
        self.set_file_copy = set()  # 복사할 파일 리스트
        self.set_file_rmv = set()  # 삭제할 파일 리스트
        self.set_file_same = set()  # 완전동일한 파일 리스트
        self.tree_copy = DepthList()  # 생성할 폴더 트리
        self.tree_rmv = DepthList()  # 삭제할 폴더 트리
        self.tree_same = DepthList()  # 두 폴더 사이에서 상대경로가 같은 폴더 트리


    def reset(self):
        self.cmp_state = None
        self.set_file_renew.clear()
        self.set_file_copy.clear()
        self.set_file_rmv.clear()
        self.set_file_same.clear()
        self.tree_copy.clear()
        self.tree_rmv.clear()
        self.tree_same.clear()


    def is_able_to_backup_file(self):
        return not (len(self.set_file_copy) == len(self.set_file_rmv) == len(self.set_file_renew) == 0)


    def is_able_to_backup_all(self):
        """  파일 백업가능 또는 폴더 백업가능 """
        return self.is_able_to_backup_file() or not (self.tree_rmv.num == self.tree_copy.num == 0)


    def is_able_boost(self):
        return len(self.set_file_same) != 0
