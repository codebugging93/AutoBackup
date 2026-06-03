from threading import Thread
from time import sleep, time

from gui.components import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askyesno, showerror

from gui.updater import UiUpdater
from system.AppData import AppData
from system.SystemValues import SystemValues
from system.aftercheck import aftercheck
from system.compare import compare
from system.constants import APPNAME, SUISEI_BLUE
from system.backup import backup, boost_files


# --- 각 화면 전환 함수 ---
def show_home():
    # 테스트용 기본 경로 설정
    AppData.original_path = r"e:\test_a"
    AppData.target_path = r"e:\test_b"
    AppData.fast_scan = True 

    btn_Previous.pack_forget()
    btn_begin.config(state="normal", text="시작", command=show_select_folder)
    switch_frame(frame_center_home)
    update_sidebar(0)

def show_select_folder():
    btn_begin.config(text="다음", command=show_select_check_mode)
    btn_Previous.config(state="normal", command=show_home)
    btn_Previous.pack(side="left", fill="y")
    btn_begin_path_check()

    # 화면상에 선택된 경로 표시 
    label_org_path.config(text=AppData.original_path)
    label_tar_path.config(text=AppData.target_path)
    switch_frame(frame_center_select)
    update_sidebar(1)

def show_select_check_mode():
    btn_begin.config(state="normal", text="다음", command=show_compare)
    btn_Previous.config(state="normal", command=show_select_folder)

    switch_frame(frame_center_check)
    update_sidebar(1)

def show_compare():
    btn_begin.config(text="다음", state="disabled")
    btn_Previous.config(state="disabled")

    switch_frame(frame_center_progress)
    update_sidebar(2)
    Thread(target=run_compare, daemon=True).start()
    # 스레드가 끝나면 자동으로 show_result 호출

def show_compare_result():
    res = AppData.compare_result
    if res is None:
        showerror(APPNAME, "알 수 없는 오류가 발생하였습니다.")
        show_home()
        return 
        
    btn_begin.config(text="백업", state="normal", command=show_backup)
    btn_Previous.config(state="normal", command=btn_prev_compare_again)

    # 버튼 텍스트 업데이트 
    btn_result_delete.config(text=f"삭제할 파일({len(res.files_rmv)})",
                             command=lambda:update_result_listbox(res.files_rmv))
    btn_result_delete2.config(text=f"삭제할 폴더({len(res.dirs_rmv)})",
                             command=lambda:update_result_listbox(res.dirs_rmv))
    btn_result_copy.config(text=f"복사할 파일({len(res.files_copy)})",
                             command=lambda:update_result_listbox(res.files_copy))
    btn_result_copy2.config(text=f"복사할 폴더({len(res.dirs_copy)})",
                             command=lambda:update_result_listbox(res.dirs_copy))
    btn_result_refresh.config(text=f"변경할 파일({len(res.files_renew)})",
                             command=lambda:update_result_listbox(res.files_renew))
    
    if len(res.files_rmv) != 0:
        update_result_listbox(res.files_rmv)
    elif len(res.dirs_rmv) != 0:
        update_result_listbox(res.dirs_rmv)
    elif len(res.files_copy) != 0:
        update_result_listbox(res.files_copy)
    elif len(res.dirs_copy) != 0:
        update_result_listbox(res.dirs_copy) 
    elif len(res.files_renew) != 0:
        update_result_listbox(res.files_renew)
    else:
        update_result_listbox(res.files_rmv)


    switch_frame(frame_center_result)
    update_sidebar(3)
        

def show_backup():
    btn_begin.config(text="다음", state="disabled")
    btn_Previous.config(state="disabled")

    switch_frame(frame_center_progress)
    update_sidebar(4)
    Thread(target=run_backup, daemon=True).start()


def show_complete():
    btn_begin.config(text="처음으로", state="normal", command=show_home)
    # btn_boost.config(text="최적화", state="normal", command=show_boost)
    btn_Previous.pack_forget()
    switch_frame(fram_center_complete)
    update_sidebar(6)


def show_aftercheck_result():
    res = AppData.failed_result # 실패한것만 다시
    if res is None:
        showerror(APPNAME, "알 수 없는 오류가 발생하였습니다.")
        show_home()
        return 
        
    btn_begin.config(text="백업", state="normal", command=show_re_backup)
    btn_Previous.config(text="취소", state="normal", command=btn_prev_cancel_re_backup)

    # 버튼 텍스트 업데이트 
    btn_result_delete.config(text=f"삭제할 파일({len(res.files_rmv)})",
                             command=lambda:update_result_listbox(res.files_rmv))
    btn_result_delete2.config(text=f"삭제할 폴더({len(res.dirs_rmv)})",
                             command=lambda:update_result_listbox(res.dirs_rmv))
    btn_result_copy.config(text=f"복사할 파일({len(res.files_copy)})",
                             command=lambda:update_result_listbox(res.files_copy))
    btn_result_copy2.config(text=f"복사할 폴더({len(res.dirs_copy)})",
                             command=lambda:update_result_listbox(res.dirs_copy))
    btn_result_refresh.config(text=f"변경할 파일({len(res.files_renew)})",
                             command=lambda:update_result_listbox(res.files_renew))
    
    if len(res.files_rmv) != 0:
        update_result_listbox(res.files_rmv)
    elif len(res.dirs_rmv) != 0:
        update_result_listbox(res.dirs_rmv)
    elif len(res.files_copy) != 0:
        update_result_listbox(res.files_copy)
    elif len(res.dirs_copy) != 0:
        update_result_listbox(res.dirs_copy) 
    elif len(res.files_renew) != 0:
        update_result_listbox(res.files_renew)
    else:
        update_result_listbox(res.files_rmv)

    switch_frame(frame_center_result)
    update_sidebar(3)


def show_re_backup():
    btn_begin.config(text="다음", state="disabled")
    btn_Previous.config(state="disabled")

    switch_frame(frame_center_progress)
    update_sidebar(4)
    Thread(target=run_re_backup, daemon=True).start()


def show_boost():
    btn_begin.config(text="다음", state="disabled")
    btn_Previous.config(state="disabled")

    switch_frame(frame_center_progress)
    update_sidebar(4)
    Thread(target=run_boost, daemon=True).start()



# --- 화면 관리 함수 ---
def switch_frame(new_frame: Frame):
    """현재 관리 중인 프레임들을 모두 숨기고 지정된 프레임을 화면에 표시합니다."""
    for frame in frames:
        frame.pack_forget()
    new_frame.pack(expand=True, fill="both")

def update_sidebar(index: int):
    """왼쪽 상태바의 레이블 색상을 현재 단계에 맞춰 업데이트합니다."""
    for i, label in enumerate(labels):
        if i == index:
            label.config(bg=SUISEI_BLUE)
        else:
            label.config(bg="white")

def update_result_listbox(data_list):
    """결과 리스트박스의 내용을 비우고 새로운 데이터(정렬됨)를 삽입합니다."""
    mid_result_list.delete(0, END)
    # 데이터가 set인 경우를 대비해 정렬된 리스트로 변환하여 삽입
    for item in sorted(list(data_list)):
        mid_result_list.insert(END, item)


# --- 이벤트 핸들러 ---
# 폴더 선택 화면 
def btn_sel_org_clicked():
    path = askdirectory(title="원본 폴더 선택")
    if not path: 
        return None
    
    if path == AppData.target_path:
        showerror("오류", "같은 폴더는 선택하실 수 없습니다.")
        return None
    
    AppData.original_path = path 
    label_org_path.config(text=path)

    btn_begin_path_check()


def btn_sel_target_clicked():
    path = askdirectory(title="대상 폴더 선택")
    if not path: 
        return None

    if path == AppData.original_path:
        showerror("오류", "같은 폴더는 선택하실 수 없습니다.")
        return None 
    
    AppData.target_path = path 
    label_tar_path.config(text=path)

    btn_begin_path_check()


def btn_begin_path_check():
    if AppData.original_path is not None and AppData.target_path is not None \
        and AppData.original_path != AppData.target_path:
        btn_begin.config(state="normal")
    else:
        btn_begin.config(state="disabled")
    

# 백업 모드 선택 화면 
def btn_fast_sel_clicked():
    AppData.fast_scan = True

def btn_det_sel_clicked():
    AppData.fast_scan = False


def run_compare():
    UiUpdater.start(UiUpdater.update_compare)
    SystemValues.compare_start_time = time()

    AppData.compare_result = compare(
        AppData.original_path,
        AppData.target_path,
        AppData.fast_scan
        )
    
    SystemValues.compare_run_time = time() - SystemValues.compare_start_time
    sleep(0.5)
    UiUpdater.stop()

    root.after(0, show_compare_result)


def run_backup():
    # 진행중에 바뀌는 메시지는 backup(), aftercheck(), boost_files() 안에 존재한다.

    SystemValues.backup_start_time = time()
    UiUpdater.start(UiUpdater.update_backup)

    backup(AppData.compare_result)
    SystemValues.backup_progress_msg = "백업 완료"
    sleep(0.5)

    AppData.failed_result = aftercheck(AppData.compare_result, AppData.fast_scan)
    SystemValues.backup_progress_msg = "재검사 완료"
    sleep(0.5)

    SystemValues.backup_run_time = time() - SystemValues.backup_start_time
    UiUpdater.stop()

    # 백업이 제대로 완료되지 않았다면
    if not AppData.failed_result.is_empty():
        root.after(0, show_aftercheck_result)
    else:
        root.after(0, show_complete)


def run_re_backup():
    # run_backup의 파생형

    SystemValues.backup_start_time = time()
    UiUpdater.start(UiUpdater.update_backup)

    backup(AppData.failed_result)
    SystemValues.backup_progress_msg = "백업 완료"
    sleep(0.5)

    AppData.failed_result = aftercheck(AppData.failed_result, AppData.fast_scan)
    SystemValues.backup_progress_msg = "재검사 완료"
    sleep(0.5)

    SystemValues.backup_run_time += time() - SystemValues.backup_start_time
    UiUpdater.stop()

    # 백업이 제대로 완료되지 않았다면
    if not AppData.failed_result.is_empty():
        root.after(0, show_aftercheck_result)
    else:
        root.after(0, show_complete)


def run_boost():
    SystemValues.backup_start_time = time()
    UiUpdater.start(UiUpdater.update_backup)

    boost_files(AppData.original_path, AppData.target_path, 
                AppData.compare_result.files_same)
    SystemValues.backup_progress_msg = "최적화 완료"
    sleep(0.5)

    UiUpdater.stop()
    root.after(0, show_complete)

    
def btn_prev_compare_again():
    if not askyesno(title=APPNAME, message="백업을 취소하시겠습니까?"):
        return None 
    
    show_home()


def btn_prev_cancel_re_backup():
    if not askyesno(title=APPNAME, message="모든 작업을 취소하시겠습니까?"):
        return None 
    
    show_home()









    







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
show_home()

btn_sel_org.config(command=btn_sel_org_clicked)
btn_sel_target.config(command=btn_sel_target_clicked)
btn_fast_sel.config(command=btn_fast_sel_clicked)
btn_det_sel.config(command=btn_det_sel_clicked)