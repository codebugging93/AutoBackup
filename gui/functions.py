import math
import os
import shutil
from threading import Thread
from time import sleep, time

from gui.components import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askyesno, showerror, showwarning

from gui.updater import UiUpdater
from system.AppData import AppData
from system.SystemValues import SystemValues
from system.aftercheck import aftercheck
from system.compare import compare
from system.constants import APPNAME, SUISEI_BLUE
from system.backup import backup, boost
from system.path import PREFIX_MAX_PATH, get_root_dirs_count, is_dest_in_src


# --- 각 화면 전환 함수 ---
def show_home():
    # # 테스트용 기본 경로 설정
    # label_org_path.config(text=r"e:\test_a")
    # label_tar_path.config(text=r"e:\test_b")
    # AppData.fast_scan = True 

    btn_Previous.pack_forget()
    btn_begin.config(state="normal", text="시작", command=show_select_folder)
    btn_optimize.pack_forget()
    switch_frame(frame_center_home)
    update_sidebar(0)

def show_select_folder():
    btn_begin.config(text="다음", command=show_select_check_mode)
    btn_Previous.config(state="normal", command=show_home)
    btn_Previous.pack(side="left", fill="y")
    btn_begin_path_check()

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
    
    # 리스트박스 업데이트(내용이 존재하는거로)
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

    # 경로 표시
    _org = res.org_path.removeprefix(PREFIX_MAX_PATH)
    _tar = res.tar_path.removeprefix(PREFIX_MAX_PATH)
    lable_expl_result.config(text=f"원본 폴더의 내용은 변경되지 않습니다.\n원본 폴더 : {_org}\n대상 폴더 : {_tar}")

    # 유저가 폴더를 잘못 선택할 가능성을 확인함     
    bool1 = len(res.dirs_rmv) == get_root_dirs_count(res.tar_path) 
    bool2 = len(res.dirs_copy) == get_root_dirs_count(res.org_path) 

    # 화면 전환
    switch_frame(frame_center_result)
    update_sidebar(3)
    
    # 유저가 폴더를 잘못 선택함을 알림
    if bool1 or bool2:
        showwarning("경고", "폴더 구조가 매우 다릅니다.\n폴더를 제대로 선택하셨는지 확인하세요.")


def show_backup():
    if not askyesno(APPNAME, "백업을 시작합니까?"):
        return 

    btn_begin.config(text="다음", state="disabled")
    btn_Previous.config(state="disabled")

    switch_frame(frame_center_progress)
    update_sidebar(4)
    Thread(target=run_backup, daemon=True).start()


def show_complete():
    btn_begin.config(text="처음으로", state="normal", command=show_home)
    btn_optimize.config(text="최적화", state="normal", command=show_boost)
    btn_optimize.pack(side='right', fill='y')

    label_complete.config(text="검사한 시간 : {:.1f}초".format(SystemValues.compare_run_time))
    label_complete2.config(text="백업한 시간 : {:.1f}초".format(SystemValues.backup_run_time))
    label_complete3.config(text="최적화율 : {:.1f}%".format(int(SystemValues.optimized_percent * 10) / 10))

    btn_Previous.pack_forget()
    switch_frame(frame_center_complete)
    update_sidebar(5)


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
    btn_optimize.pack_forget()

    switch_frame(frame_center_progress)
    update_sidebar(4)
    Thread(target=run_boost, daemon=True).start()



# --- 화면 관리 함수 ---
def switch_frame(new_frame: Frame):
    """현재 관리 중인 프레임들을 모두 숨기고 지정된 프레임을 화면에 표시합니다."""
    for frame in frames:
        frame.pack_forget()
    new_frame.pack(expand=True, fill="both")

# 사이드바 이미지 배열 
_sidebar_images = [
    tk_step_home_img,
    tk_step_select_img,
    tk_step_progress_img,
    tk_step_result_img,
    tk_step_backup_img,
    tk_step_complete_img,
]

_sidebar_images_inverted = [
    tk_step_home_img_inverted,
    tk_step_select_img_inverted,
    tk_step_progress_img_inverted,
    tk_step_result_img_inverted,
    tk_step_backup_img_inverted,
    tk_step_complete_img_inverted,
]


def update_sidebar(index: int):
    """왼쪽 상태바의 레이블 색상을 현재 단계에 맞춰 업데이트합니다."""
    for i, label in enumerate(labels):
        if i == index:
            labels[i].config(image=_sidebar_images_inverted[i])
        else:
            labels[i].config(image=_sidebar_images[i])

def update_result_listbox(data_list: list[str]):
    """결과 리스트박스의 내용을 비우고 새로운 데이터(정렬됨)를 삽입합니다."""
    mid_result_list.delete(0, END)
    # 데이터가 set인 경우를 대비해 정렬된 리스트로 변환하여 삽입
    for item in sorted(list(data_list)):
        item = item.removeprefix(PREFIX_MAX_PATH)
        mid_result_list.insert(END, item)


# --- 이벤트 핸들러 ---
# 폴더 선택 화면 
def btn_sel_org_clicked():
    while True:
        path = askdirectory(title="원본 폴더 선택")
        # 취소
        if not path: 
            return None
        
        # 같은 폴더 선택
        path = os.path.normpath(path)
        if path == label_tar_path['text']:
            showerror("오류", "같은 폴더는 선택하실 수 없습니다.")
            continue 

        break 

    label_org_path.config(text=path)
    btn_begin_path_check()


def btn_sel_target_clicked():
    while True:
        path = askdirectory(title="대상 폴더 선택")
        # 취소
        if not path: 
            return None
        
        # 같은 폴더 선택
        path = os.path.normpath(path)
        if path == label_org_path['text']:
            showerror("오류", "같은 폴더는 선택하실 수 없습니다.")
            continue 

        break 
    
    label_tar_path.config(text=path)
    btn_begin_path_check()


def btn_begin_path_check():
    # 유저가 선택을 하지 않은 경우: 잠금
    if len(label_org_path['text']) == 0 or len(label_tar_path['text']) == 0:
        btn_begin.config(state="disabled")
        return 
    
    # 유저가 같은 폴더를 선택한 경우: 잠금
    if label_org_path['text'] == label_tar_path['text']:
        btn_begin.config(state="disabled")
        return 
    
    # 유저가 내부 폴더를 선택한 경우: 잠금
    if is_dest_in_src(label_org_path['text'], label_tar_path['text']) or \
        is_dest_in_src(label_tar_path['text'], label_org_path['text']):
        btn_begin.config(state="disabled")
        showerror("오류", "한쪽을 포함하는 폴더는 백업할 수 없습니다.\n다른 폴더를 선택해주세요.")
        return 

    btn_begin.config(state="normal")
    

# 백업 모드 선택 화면 
def btn_fast_sel_clicked():
    AppData.fast_scan = True

def btn_det_sel_clicked():
    AppData.fast_scan = False


def run_compare():
    UiUpdater.start(UiUpdater.update_compare)

    SystemValues.compare_start_time = time()
    AppData.compare_result = compare(
        label_org_path['text'],
        label_tar_path['text'],
        AppData.fast_scan
        )
    SystemValues.compare_run_time = time() - SystemValues.compare_start_time

    UiUpdater.stop()
    sleep(0.5)

    root.after(0, show_compare_result)


def run_backup():
    # 진행중에 바뀌는 메시지는 backup(), aftercheck(), boost_files() 안에 존재한다.
    UiUpdater.start(UiUpdater.update_backup)

    SystemValues.backup_start_time = time()
    backup(AppData.compare_result)
    AppData.failed_result = aftercheck(AppData.compare_result, AppData.fast_scan)
    SystemValues.backup_run_time = time() - SystemValues.backup_start_time

    SystemValues.backup_progress_msg = "백업 완료"
    UiUpdater.stop()
    sleep(0.5)

    # 백업이 제대로 완료되지 않았다면
    if not AppData.failed_result.is_empty():
        root.after(0, show_aftercheck_result)
    else:
        root.after(0, show_complete)


def run_re_backup():
    # run_backup의 파생형
    UiUpdater.start(UiUpdater.update_backup)

    SystemValues.backup_start_time = time()
    backup(AppData.failed_result)
    AppData.failed_result = aftercheck(AppData.failed_result, AppData.fast_scan)
    SystemValues.backup_run_time += time() - SystemValues.backup_start_time
    
    SystemValues.backup_progress_msg = "백업 완료"
    UiUpdater.stop()
    sleep(0.5)

    # 백업이 제대로 완료되지 않았다면
    if not AppData.failed_result.is_empty():
        root.after(0, show_aftercheck_result)
    else:
        root.after(0, show_complete)


def run_boost():
    UiUpdater.start(UiUpdater.update_backup)
    SystemValues.backup_progress_msg = "검사 속도 향상을 위한 최적화"

    SystemValues.backup_start_time = time()
    boost(AppData.compare_result)

    SystemValues.backup_progress_msg = "최적화 완료"
    UiUpdater.stop()
    sleep(0.5)

    root.after(0, show_complete)

    
def btn_prev_compare_again():
    if not askyesno(title=APPNAME, message="백업을 취소하시겠습니까?"):
        return None 
    
    show_home()


def btn_prev_cancel_re_backup():
    if not askyesno(title=APPNAME, message="모든 작업을 취소하시겠습니까?"):
        return None 
    
    show_home()


# 초기 UI 상태 업데이트
show_home()

btn_sel_org.config(command=btn_sel_org_clicked)
btn_sel_target.config(command=btn_sel_target_clicked)
btn_fast_sel.config(command=btn_fast_sel_clicked)
btn_det_sel.config(command=btn_det_sel_clicked)