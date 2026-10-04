"""
gui/functions.py(tkinter)를 PySide6로 번역한 버전입니다.

동작(화면 흐름, 조건 검사, 오류 처리)은 기존 tkinter 버전과 동일하게 맞췄고,
위젯 API 차이 때문에 필요한 부분만 PySide6 방식으로 바꿨습니다.

- Label['text'] / .config(text=...)      -> .text() / .setText(...)
- Button.config(state=...)               -> .setEnabled(...)
- pack()/pack_forget()                   -> show()/hide()
- switch_frame() (프레임 전부 숨기고 하나만 표시) -> QStackedWidget.setCurrentWidget()
- tkinter.messagebox                     -> QMessageBox
- tkinter.filedialog.askdirectory        -> QFileDialog.getExistingDirectory
- root.after(0, func)                    -> components_pyside6.call_in_gui_thread(func)
  (background thread에서 messagebox를 직접 띄우고 완료를 기다리던 부분은
   call_in_gui_thread_blocking으로 동일하게 "대기" 동작을 재현함)

버튼의 클릭 커맨드(tkinter의 .config(command=...))는 화면마다 계속 바뀝니다
(예: btn_begin은 화면에 따라 show_select_folder/show_compare/show_backup 등을 실행).
Qt의 clicked.connect()는 호출할 때마다 새 연결을 "추가"할 뿐 이전 연결을 대체하지 않으므로,
버튼이 실행할 함수를 바꿀 때는 매번 clicked.disconnect() 후 clicked.connect(새 함수)를 호출합니다.
"""

import os
from threading import Thread
from time import sleep, time

from PySide6.QtWidgets import QFileDialog, QMessageBox

from gui.components import *  # noqa: F401,F403  (root, frame_*, btn_*, label_* 등)
from gui.components import call_in_gui_thread, call_in_gui_thread_blocking
from gui.updater import UiUpdater
from system.AppData import AppData, reset_appdata
from system.Trashbin import Trashbin
from system.SystemValues import SystemValues
from system.aftercheck import aftercheck
from system.backup import backup, boost
from system.compare import compare
from system.constants import APPNAME
from system.path import PREFIX_MAX_PATH, is_dest_in_src

def _ask_yes_no(message: str) -> bool:
    reply = QMessageBox.question(
        root, APPNAME, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes


def _show_error(message: str):
    QMessageBox.critical(root, "오류", message)


def _show_warning(message: str):
    QMessageBox.warning(root, "경고", message)


# --- 각 화면 전환 함수 ---
def show_home():
    # 처음 화면으로 돌아올 때는 이전 작업의 흔적을 남기지 않는다.
    reset_appdata()
    Trashbin.remove_path = ""

    btn_Previous.hide()
    btn_optimize.hide()

    # 다음 버튼 기능 변경
    btn_begin.setText("시작")
    btn_begin.setEnabled(True)
    btn_begin.clicked.disconnect()
    btn_begin.clicked.connect(show_select_folder)

    switch_frame(frame_center_home)
    update_sidebar(0)


def show_select_folder():
    # 다음 버튼 기능 변경
    btn_begin.setText("다음")
    btn_begin.setEnabled(True)
    btn_begin.clicked.disconnect()
    btn_begin.clicked.connect(show_select_check_mode)

    # 이전 버튼 기능 변경
    btn_Previous.setText("이전")
    btn_Previous.setEnabled(True)
    btn_Previous.clicked.disconnect()
    btn_Previous.clicked.connect(show_home)
    btn_Previous.show()

    switch_frame(frame_center_select)
    update_sidebar(1)


def show_select_check_mode():
    # 1. 폴더 선택 제대로 되었는지 확인
    # 유저가 선택을 하지 않은 경우
    if len(label_org_path.text()) == 0 or len(label_tar_path.text()) == 0:
        _show_error("원본 폴더와 대상 폴더를 모두 선택해주세요.")
        return

    # 선택한 폴더가 실존하지 않는 경우(USB 연결 해제 등)
    if not os.path.isdir(label_org_path.text()) or not os.path.isdir(label_tar_path.text()):
        _show_error("선택한 폴더를 찾을 수 없습니다.\n장치 연결 상태 등을 확인해주세요.")
        return

    # 같은 폴더를 선택한 경우
    if label_org_path.text() == label_tar_path.text():
        _show_error("같은 폴더는 선택하실 수 없습니다.")
        return

    # 유저가 내부 폴더를 선택한 경우
    if is_dest_in_src(label_org_path.text(), label_tar_path.text()) or \
            is_dest_in_src(label_tar_path.text(), label_org_path.text()):
        _show_error("한 폴더가 다른쪽에 포함됩니다.\n폴더가 서로 포함되지 않도록 해주세요.")
        return

    # 2. 화면 전환
    btn_begin.setText("다음")
    btn_begin.setEnabled(True)
    btn_begin.clicked.disconnect()
    btn_begin.clicked.connect(show_compare)

    btn_Previous.setText("이전")
    btn_Previous.setEnabled(True)
    btn_Previous.clicked.disconnect()
    btn_Previous.clicked.connect(show_select_folder)

    switch_frame(frame_center_check)
    update_sidebar(1)


def show_compare():
    # 선택한 폴더가 실존하지 않는 경우(USB 연결 해제 등)
    if not os.path.isdir(label_org_path.text()) or not os.path.isdir(label_tar_path.text()):
        _show_error("선택한 폴더를 찾을 수 없습니다.\n장치 연결 상태 등을 확인해주세요.")
        return

    btn_begin.setText("다음")
    btn_begin.setEnabled(False)
    btn_Previous.setEnabled(False)

    switch_frame(frame_center_progress)
    update_sidebar(2)
    Thread(target=run_compare, daemon=True).start()
    # 스레드가 끝나면 자동으로 show_compare_result 호출


def show_compare_result():
    """ 검사 결과 화면을 띄운다. """

    res = AppData.compare_result
    if res is None:
        _show_error("알 수 없는 오류가 발생하였습니다.")
        show_home()
        return

    btn_begin.setText("백업")
    btn_begin.setEnabled(True)
    btn_begin.clicked.disconnect()
    btn_begin.clicked.connect(show_backup)

    btn_Previous.setText("이전")
    btn_Previous.setEnabled(True)
    btn_Previous.clicked.disconnect()
    btn_Previous.clicked.connect(btn_prev_compare_again)
    btn_Previous.show() # 완료 화면 등에서 숨겨진 채로 넘어와도 다시 보이게 한다

    # 버튼 텍스트 업데이트
    btn_result_delete.setText(f"삭제할 파일({len(res.files_rmv)})")
    btn_result_delete.clicked.disconnect()
    btn_result_delete.clicked.connect(lambda: update_result_listbox(res.files_rmv))

    btn_result_delete2.setText(f"삭제할 폴더({len(res.dirs_rmv)})")
    btn_result_delete2.clicked.disconnect()
    btn_result_delete2.clicked.connect(lambda: update_result_listbox(res.dirs_rmv))

    btn_result_copy.setText(f"복사할 파일({len(res.files_copy)})")
    btn_result_copy.clicked.disconnect()
    btn_result_copy.clicked.connect(lambda: update_result_listbox(res.files_copy))

    btn_result_copy2.setText(f"복사할 폴더({len(res.dirs_copy)})")
    btn_result_copy2.clicked.disconnect()
    btn_result_copy2.clicked.connect(lambda: update_result_listbox(res.dirs_copy))

    btn_result_refresh.setText(f"변경할 파일({len(res.files_renew)})")
    btn_result_refresh.clicked.disconnect()
    btn_result_refresh.clicked.connect(lambda: update_result_listbox(res.files_renew))

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
    label_org_path.setText(res.org_path.removeprefix(PREFIX_MAX_PATH))
    label_tar_path.setText(res.tar_path.removeprefix(PREFIX_MAX_PATH))
    # 결과 화면의 경로 카드도 같은 값으로 채운다.
    label_result_org.setText(label_org_path.text())
    label_result_tar.setText(label_tar_path.text())
    lable_expl_result.setText("원본 폴더의 내용은 변경되지 않습니다.")

    # 유사도 표시
    # 유사도가 음수이면 잴 대상 자체가 없었다는 뜻이다.
    if res.dirs_similarity < 0:
        label_dirs_similarity.setText("하위 폴더 없음")
    else:
        label_dirs_similarity.setText(f"{res.dirs_similarity:.1f}%")

    if res.files_similarity < 0:
        label_files_similarity.setText("파일 없음")
    else:
        label_files_similarity.setText(f"{res.files_similarity:.1f}%")

    # 화면 전환
    switch_frame(frame_center_result)
    update_sidebar(3)

    # 유저가 폴더를 잘못 선택함을 알림
    # 폴더 유사도와 파일 유사도 중 어느 하나라도 기준치보다 낮으면 경고한다.
    # 음수는 잴 대상이 없었다는 뜻이므로 판단에서 제외한다.
    
    SIMILARITY_WARNING_THRESHOLD = 30.0 # 폴더/파일 유사도가 이 값보다 낮으면 폴더를 잘못 고른 것으로 보고 경고한다.
    if 0 <= res.dirs_similarity < SIMILARITY_WARNING_THRESHOLD or 0 <= res.files_similarity < SIMILARITY_WARNING_THRESHOLD:
        _show_warning("원본/대상 폴더간에 공통점이 거의 없습니다.\n"
                      "선택된 폴더가 올바른지 확인하세요.")


def show_backup():
    if not _ask_yes_no("백업을 시작합니까?"):
        return

    btn_begin.setText("다음")
    btn_begin.setEnabled(False)
    btn_Previous.setEnabled(False)

    switch_frame(frame_center_progress)
    update_sidebar(4)
    Thread(target=run_backup, daemon=True).start()


def show_complete():
    btn_begin.setText("처음으로")
    btn_begin.setEnabled(True)
    btn_begin.clicked.disconnect()
    btn_begin.clicked.connect(show_home)

    btn_optimize.setText("최적화")
    btn_optimize.setEnabled(True)
    btn_optimize.clicked.disconnect()
    btn_optimize.clicked.connect(show_boost)
    btn_optimize.show()


    label_complete.setText("검사한 시간 : {:.1f}초".format(AppData.compare_run_time))
    label_complete2.setText("백업한 시간 : {:.1f}초".format(AppData.backup_run_time))
    label_complete3.setText("최적화율 : {:.1f}%".format(AppData.compare_result.optimized_percent))

    btn_Previous.hide()
    switch_frame(frame_center_complete)
    update_sidebar(5)

    if AppData.backup_success:
        pass # 백업 성공 메시지 띄움 
    else:
        # 백업 실패 메시지 띄움 
        pass
        _show_error("백업되지 않은 파일이 존재합니다. 다시 검사해주세요.")


def show_boost():
    btn_begin.setText("다음")
    btn_begin.setEnabled(False)
    btn_Previous.setEnabled(False)
    btn_optimize.hide()

    switch_frame(frame_center_progress)
    update_sidebar(4)
    Thread(target=run_boost, daemon=True).start()


# --- 화면 관리 함수 ---
def switch_frame(new_frame):
    """지정된 프레임을 화면에 표시합니다."""
    frame_main.setCurrentWidget(new_frame)


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
    """왼쪽 상태바의 아이콘을 현재 단계에 맞춰 업데이트합니다.
    진행 중인 단계는 배경을 SUISEI_BLUE로, 나머지는 사이드바 배경색과 통일합니다.
    (아이콘 이미지 자체의 배경색에 의존하지 않고 코드에서 직접 칠함)
    """
    for i, label in enumerate(labels):
        if i == index:
            label.setPixmap(_sidebar_images_inverted[i])
            label.setStyleSheet(f"background-color: {COLOR_BLUE};")
        else:
            label.setPixmap(_sidebar_images[i])
            label.setStyleSheet(f"background-color: {COLOR_BG};")

def update_result_listbox(data_list):
    """결과 리스트박스의 내용을 비우고 새로운 데이터(정렬됨)를 삽입합니다."""
    mid_result_list.clear()
    # 데이터가 set인 경우를 대비해 정렬된 리스트로 변환하여 삽입
    # addItem으로 하나씩 넣으면 항목이 많을 때 느리므로 addItems로 한 번에 넣는다.
    items = [item.removeprefix(PREFIX_MAX_PATH) for item in sorted(data_list)]
    mid_result_list.addItems(items)


# --- 이벤트 핸들러 ---
# 폴더 선택 화면
def btn_sel_org_clicked():
    while True:
        path = QFileDialog.getExistingDirectory(root, "원본 폴더 선택")
        # 취소
        if not path:
            return None

        # 같은 폴더 선택
        path = os.path.normpath(path)
        if path == label_tar_path.text():
            _show_error("같은 폴더는 선택하실 수 없습니다.")
            continue

        break

    label_org_path.setText(path)


def btn_sel_target_clicked():
    while True:
        path = QFileDialog.getExistingDirectory(root, "대상 폴더 선택")
        # 취소
        if not path:
            return None

        # 같은 폴더 선택
        path = os.path.normpath(path)
        if path == label_org_path.text():
            _show_error("같은 폴더는 선택하실 수 없습니다.")
            continue

        break

    label_tar_path.setText(path)


# 백업 모드 선택 화면
def btn_fast_sel_clicked():
    AppData.fast_scan = True


def btn_det_sel_clicked():
    AppData.fast_scan = False


def run_compare():
    """
    compare()를 돌려 AppData.compare_result를 갱신한다.
    """
    UiUpdater.start(UiUpdater.update_compare)
    SystemValues.compare_start_time = time()

    try:
        AppData.compare_result = compare(
            label_org_path.text(),
            label_tar_path.text(),
            AppData.fast_scan,
        )
    except Exception:
        cancel_task("검사 중 오류가 발생하였습니다.\nUSB 인식 상태 등을 확인해주세요.")
        return 

    AppData.compare_run_time = time() - SystemValues.compare_start_time
    UiUpdater.stop()
    sleep(0.5)

    call_in_gui_thread(show_compare_result)


def run_backup():
    # ---------- 백업 ----------
    UiUpdater.start(UiUpdater.update_backup)
    SystemValues.backup_start_time = time()

    try:
        backup(AppData.compare_result)
        failed = aftercheck(AppData.compare_result, AppData.fast_scan)
    except Exception:
        cancel_task("백업 중 오류가 발생하였습니다.\nUSB 인식 상태 등을 확인해주세요.")
        return

    AppData.backup_run_time = time() - SystemValues.backup_start_time
    UiUpdater.stop()
    sleep(0.5)

    remain = len(failed.dirs_copy) + len(failed.dirs_rmv) + len(failed.files_copy) + \
            len(failed.files_rmv) + len(failed.files_renew)

    if remain == 0: # 더 처리할 것이 없다 -> 백업 성공
        AppData.backup_success = True 
    else:
        AppData.backup_success = False
    call_in_gui_thread(show_complete) 


def cancel_task(message: str):
    """
    작업을 이어갈 수 없는 오류가 발생했을 때, 작업을 중단하고 처음 화면으로 돌아간다.
    검사/백업/최적화 어디에서 호출하든 동작이 같다.

    기다렸다가 재개하지 않고 무조건 중단하는 이유:
    - 원본 폴더는 절대 건드리지 않으므로 중단해도 데이터가 안전하다.
    - compare()가 매번 현재 상태를 처음부터 다시 계산하므로, 다시 실행하는 것이 곧 이어서 하기다.
      즉 재개해서 아낄 수 있는 것은 검사 시간뿐이다.
    - "장치를 다시 연결해주세요" 하고 기다리면 그 사이에 다른 장치가 꽂힐 수 있다.
      기다리지 않으면 그런 상황 자체가 생기지 않는다.
    """
    UiUpdater.stop()
    sleep(0.5)

    def handle_error():
        _show_error(message)

        # 오류로 중단한 경우에는 선택했던 경로까지 지운다.
        # 장치가 사라진 뒤 같은 드라이브 문자에 다른 장치가 붙을 수 있으므로,
        # 경로 문자열을 그대로 재사용하지 않고 사용자가 다시 고르게 한다.
        label_org_path.setText("")
        label_tar_path.setText("")

        show_home()

    call_in_gui_thread(handle_error)


def run_boost():
    try:
        UiUpdater.start(UiUpdater.update_backup)
        SystemValues.backup_progress_msg = "검사 속도 향상을 위한 최적화"

        SystemValues.backup_start_time = time()
        boost(AppData.compare_result)

        SystemValues.backup_progress_msg = "최적화 완료"
        UiUpdater.stop()
        sleep(0.5)

        call_in_gui_thread(show_complete)
    except Exception:
        # 최적화 중에도 장치가 바뀔 수 있으므로 다른 작업과 똑같이 중단하고 처음 화면으로 돌아간다.
        cancel_task("최적화 중 오류가 발생하였습니다.\nUSB 인식 상태 등을 확인해주세요.")


def btn_prev_compare_again():
    if not _ask_yes_no("백업을 취소하시겠습니까?"):
        return None

    show_home()


# 초기 UI 상태 업데이트
show_home()

btn_sel_org.clicked.connect(btn_sel_org_clicked)
btn_sel_target.clicked.connect(btn_sel_target_clicked)
btn_fast_sel.clicked.connect(btn_fast_sel_clicked)
btn_det_sel.clicked.connect(btn_det_sel_clicked)
