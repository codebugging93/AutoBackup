class ConfigData:
    """ 
    프로그램 실행 중의 상태를 저장하는 클래스
    비교 모드 / 백업 모드 / exFAT 모드 
    휴지통 경로 등등
    """
    def __init__(self):
        self.backup_mode = None  # level_2에서 선택한 백업 모드 
        self.compare_mode = None # 초기에 선택한 비교 모드 
        self.isexFAT = False  # 선택한 디바이스를 exFAT으로 취급하고 다른 비교 알고리즘을 사용함
        

    
    def exfat(self, exfat_bool):
        self.isexFAT = exfat_bool


    def reset(self):
        self.backup_mode = None
        self.compare_mode = None 
        self.isexFAT = False
