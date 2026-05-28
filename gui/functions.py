from threading import Thread

from gui.components import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror

from gui.updater import UiUpdater
from system.AppData import AppData
from system.compare import compare
from system.constants import SUISEI_BLUE



current_index = 0 # 프레임 번호

def update_ui():
    global current_index
    # 인덱스가 범위를 벗어나지 않도록 강제 제한
    current_index = max(0, min(current_index, len(frames) - 1))

    # 왼쪽 상태바 레이블 배경색 변경
    for i, label in enumerate(labels):
        if i < current_index:
            pass 
        elif i == current_index:
            label.config(bg=SUISEI_BLUE)
        else:
            label.config(bg="white")

    # 프레임 교체 
    for frame in frames:
        frame.pack_forget()
    frames[current_index].pack(expand=True, fill="both")

    # 각 화면 제어 
    if current_index == 0:
        btn_Previous.pack_forget()
        btn_begin.config(state="normal", text="시작")
    
    elif current_index == 1:
        AppData.original_path = r"e:\test_a"
        AppData.target_path = r"e:\test_b"
        AppData.fast_scan = True 

        btn_begin_path_check()
        btn_begin.config(text="다음")
        btn_Previous.pack(side="left", fill="y")
        btn_Previous.config(state="normal")

    elif current_index == 2:
        btn_begin_backup_mode_check()

    elif current_index == 3:
        btn_begin.config(state="disabled")
        btn_Previous.config(state="disabled")
        Thread(target=run_compare, daemon=True).start()

    elif current_index == 4:
        btn_begin.config(state="normal")
        btn_Previous.config(state="disabled")



    elif current_index == len(frames) - 1:
        btn_begin.config(state="normal", text="완료")


def btn_begin_clicked():
    global current_index
    current_index += 1
    update_ui()
    

def btn_prev_clicked():
    global current_index
    current_index -= 1
    update_ui()    


# 폴더 선택 화면 
def btn_sel_org_clicked():
    path = askdirectory(title="원본 폴더 선택")
    if not path: 
        return None
    
    if path == AppData.target_path:
        showerror("오류", "같은 폴더는 선택하실 수 없습니다.")
        return None
    
    AppData.original_path = path 

    btn_begin_path_check()


def btn_sel_target_clicked():
    path = askdirectory(title="대상 폴더 선택")
    if not path: 
        return None

    if path == AppData.original_path:
        showerror("오류", "같은 폴더는 선택하실 수 없습니다.")
        return None 
    
    AppData.target_path = path 

    btn_begin_path_check()


def btn_begin_path_check():
    if AppData.original_path is not None and AppData.target_path is not None \
        and AppData.original_path != AppData.target_path:
        btn_begin.config(state="normal")
    else:
        btn_begin.config(state="disabled")
    

def btn_begin_backup_mode_check():
    if AppData.fast_scan != None:
        btn_begin.config(state="normal")
    else:
        btn_begin.config(state="disabled")


# 백업 모드 선택 화면 
def btn_fast_sel_clicked():
    AppData.fast_scan = True
    btn_begin_backup_mode_check()

def btn_det_sel_clicked():
    AppData.fast_scan = False
    btn_begin_backup_mode_check()


def run_compare():
    UiUpdater.start(UiUpdater.update_compare)

    compare(
        AppData.original_path,
        AppData.target_path,
        AppData.fast_scan
        )
    
    UiUpdater.stop()

    btn_begin_clicked()

    
    

    







"""def show_second_result_frame(frame_type):
    # 6-2 프레임 숨기기
    frame_mid_del_result.pack_forget()
    frame_bot_del_result.pack_forget()
    
    frame_mid_copy_result.pack_forget()
    frame_bot_copy_result.pack_forget()
    
    frame_mid_renew_result.pack_forget()
    frame_bot_renew_result.pack_forget()

    if frame_type == "delete":
        frame_mid_del_result.pack(side="top", pady="5")
        frame_bot_del_result.pack(side="top", pady="5")
    elif frame_type == "copy":
        frame_mid_copy_result.pack(side="top", pady="5")
        frame_bot_copy_result.pack(side="top", pady="5")
    elif frame_type == "renew":
        frame_mid_renew_result.pack(side="top", pady="5")
        frame_bot_renew_result.pack(side="top", pady="5")
"""


# 초기 UI 상태 업데이트
update_ui()
# show_second_result_frame("delete")


btn_sel_org.config(command=btn_sel_org_clicked)
btn_sel_target.config(command=btn_sel_target_clicked)
btn_fast_sel.config(command=btn_fast_sel_clicked)
btn_det_sel.config(command=btn_det_sel_clicked)
btn_begin.config(command=btn_begin_clicked)
btn_Previous.config(command=btn_prev_clicked)


# btn_result_delete.config(command=lambda: show_second_result_frame("delete"))
# btn_result_copy.config(command=lambda: show_second_result_frame("copy")) 
# btn_result_refresh.config(command=lambda: show_second_result_frame("renew"))
