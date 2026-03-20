from implemented.main_datas import configs
from TKgui.widgets import btn_exfat

def update_exfat_btn():
    isexFAT = configs.isexFAT
    if isexFAT:
        btn_exfat.config(text="exFAT 모드\nON") 
    else:
        btn_exfat.config(text="exFAT 모드")  # TODO 타겟 장치가 exFAT이면 자동으로 켜지는 기능 넣기     


def toggle_exfat_btn():
    configs.exfat(not configs.isexFAT)
    update_exfat_btn()