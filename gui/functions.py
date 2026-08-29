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
from system.AppData import AppData
from system.SystemValues import SystemValues
from system.aftercheck import aftercheck
from system.backup import backup, boost
from system.compare import compare
from system.constants import APPNAME
from system.path import PREFIX_MAX_PATH, get_root_dirs_count, is_dest_in_src


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


def _fill_result_screen(res, on_backup_command, previous_text, previous_command, header_text):
    """ show_compare_result / show_aftercheck_result의 공통 로직 """
    btn_begin.setText("백업")
    btn_begin.setEnabled(True)
    btn_begin.clicked.disconnect()
    btn_begin.clicked.connect(on_backup_command)

    btn_Previous.setText(previous_text)
    btn_Previous.setEnabled(True)
    btn_Previous.clicked.disconnect()
    btn_Previous.clicked.connect(previous_command)

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
    _org = res.org_path.removeprefix(PREFIX_MAX_PATH)
    _tar = res.tar_path.removeprefix(PREFIX_MAX_PATH)
    lable_expl_result.setText(f"{header_text}\n원본 폴더 : {_org}\n대상 폴더 : {_tar}")


def show_compare_result():
    res = AppData.compare_result
    if res is None:
        _show_error("알 수 없는 오류가 발생하였습니다.")
        show_home()
        return

    _fill_result_screen(
        res,
        on_backup_command=show_backup,
        previous_text="이전",
        previous_command=btn_prev_compare_again,
        header_text="원본 폴더의 내용은 변경되지 않습니다.",
    )

    # 유저가 폴더를 잘못 선택할 가능성을 확인함

    # 화면 전환
    switch_frame(frame_center_result)
    update_sidebar(3)

    # 유저가 폴더를 잘못 선택함을 알림
    """
    dirs_same의 개수가 1개뿐인 경우 보통 원본/대상 폴더를 잘못 지정한 것이다.
    즉 이럴 경우 폴더 일치율을 0%라고 계산하고, 유저에게 표시할 수 있다. 
    그런데 양쪽에 폴더가 없었다면 똑같이 0%지만 상황이 조금 다르다.
    그럴땐 "하위 폴더 없음" 이라고 유저에게 표시하자.

    파일 일치율은 오로지 files_same을 기준으로 한다.

    기준은 10%로 하자. 
    또한 더블 클릭을 방지하기 위해서 백업 버튼을 누를때도 더블 체크를 시킨다.

    그럼 이제 어떻게 모집단을 구해야 하는지가 관건이다.
    가장 간단한 모델을 생각해보자.
    A 집합과 B 집합이 있다.
    A는 {a, b, c, d, e}로 이루어져 있고,
    B는 {b, c, d, e, f}로 이루어져 있다.
    즉 A->B로 백업할때 a는 복사하고 f는 삭제해야하는 상황이다.

    이럴 경우의 유사도를 측정해보자면, 우선 전체집합은 {a, b, c, d, e, f}로 크기가 6이다.
    그중 교집합이 {b, c, d, e}이고 크기가 4이다.
    따라서 유사도는 4/6이다.

    모든 파일 검사에서는 각 공통 디렉터리에 바로 속한 파일들의 집합을 비교하도록 되어있다.
    애초에 files_same을 알아내는 과정에서 자연스럽게 합집합도 구할 수 있다.
    
    """
    if get_root_dirs_count(res.org_path) != 0 and get_root_dirs_count(res.tar_path) != 0:
        if len(res.files_same) == 0 or len(res.dirs_same) == 1:
            _show_warning("원본/대상 폴더간에 공통점이 거의 없습니다.\n선택된 폴더가 올바른지 확인하세요.")


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

    label_complete.setText("검사한 시간 : {:.1f}초".format(SystemValues.compare_run_time))
    label_complete2.setText("백업한 시간 : {:.1f}초".format(SystemValues.backup_run_time))
    label_complete3.setText("최적화율 : {:.1f}%".format(int(SystemValues.optimized_percent * 10) / 10))

    btn_Previous.hide()
    switch_frame(frame_center_complete)
    update_sidebar(5)


def show_aftercheck_result():
    """
    show_compare_result와 거의 동일하나,
    AppData.compare_result가 AppData.failed_result로 바뀌어있다.
    """
    res = AppData.failed_result  # 실패한것만 다시
    if res is None:
        _show_error("알 수 없는 오류가 발생하였습니다.")
        show_home()
        return

    _fill_result_screen(
        res,
        on_backup_command=show_re_backup,
        previous_text="취소",
        previous_command=btn_prev_cancel_re_backup,
        header_text="백업에 실패한 파일이 발견되었습니다.",
    )

    switch_frame(frame_center_result)
    update_sidebar(3)


def show_re_backup():
    btn_begin.setText("다음")
    btn_begin.setEnabled(False)
    btn_Previous.setEnabled(False)

    switch_frame(frame_center_progress)
    update_sidebar(4)
    Thread(target=run_re_backup, daemon=True).start()


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
    for item in sorted(list(data_list)):
        item = item.removeprefix(PREFIX_MAX_PATH)
        mid_result_list.addItem(item)


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
    try:
        UiUpdater.start(UiUpdater.update_compare)

        SystemValues.compare_start_time = time()
        AppData.compare_result = compare(
            label_org_path.text(),
            label_tar_path.text(),
            AppData.fast_scan,
        )
        SystemValues.compare_run_time = time() - SystemValues.compare_start_time

        # 최적화율 기록은 상위 레벨인 여기서 담당한다.
        # (compare가 직접 기록하면 aftercheck 안의 중첩 compare가 이 값을 덮어써 버린다.)
        SystemValues.optimized_percent = AppData.compare_result.optimized_percent

        UiUpdater.stop()
        sleep(0.5)

        call_in_gui_thread(show_compare_result)
    except Exception:
        UiUpdater.stop()
        sleep(0.5)

        def handle_error():
            _show_error("검사 중 오류가 발생하였습니다.\nUSB 인식 상태 등을 확인해주세요.")
            show_select_folder()

        call_in_gui_thread(handle_error)


def run_backup():
    # 진행중에 바뀌는 메시지는 backup(), aftercheck(), boost() 안에 존재한다.

    # 권한 문제인 파일은 backup() 안에서 알아서 건너뛴다.
    # 여기까지 올라온 오류는 USB 분리, 용량 부족처럼 작업을 이어갈 수 없는 상황이다.
    # 원본 폴더는 절대 건드리지 않으므로, 그냥 백업을 취소하고 처음 화면으로 돌아가면 된다.
    # 다시 실행하면 compare()가 남은 차이만 다시 계산하므로 이어서 하는 것과 같다.
    UiUpdater.start(UiUpdater.update_backup)

    SystemValues.backup_start_time = time()
    try:
        # 1. 백업 루틴
        backup(AppData.compare_result)
        SystemValues.backup_progress_msg = "백업 완료"

        # 2. 재검사 루틴
        AppData.failed_result = aftercheck(AppData.compare_result, AppData.fast_scan)
        SystemValues.backup_progress_msg = "재검사 완료"
    except Exception:
        cancel_backup()
        return
    finally:
        SystemValues.backup_run_time = time() - SystemValues.backup_start_time

    UiUpdater.stop()
    sleep(0.5)

    # 백업이 제대로 완료되지 않았다면
    if not AppData.failed_result.is_empty():
        call_in_gui_thread(show_aftercheck_result)
    else:
        call_in_gui_thread(show_complete)


def cancel_backup():
    """
    백업을 이어갈 수 없는 오류가 발생했을 때, 작업을 취소하고 처음 화면으로 돌아간다.

    이 상태에서는 재검사(aftercheck)를 돌리면 안 된다.
    장치가 사라진 상태에서 재검사를 하면 모든 파일이 백업에 실패한 것으로 잘못 판정되고,
    삭제한 파일은 반대로 잘 지워진 것으로 오판하기 때문이다.
    """
    UiUpdater.stop()
    sleep(0.5)

    def handle_error():
        _show_error("백업이 중단되었습니다.\n"
                    "USB 인식 상태 등을 확인한 뒤 다시 시도해주세요.\n"
                    "원본 폴더는 변경되지 않았습니다.")
        show_home()

    call_in_gui_thread(handle_error)


def run_re_backup():
    # run_backup의 파생형
    UiUpdater.start(UiUpdater.update_backup)

    SystemValues.backup_start_time = time()
    try:
        backup(AppData.failed_result)
        AppData.failed_result = aftercheck(AppData.failed_result, AppData.fast_scan)
    except Exception:
        # run_backup과 동일하게, 이어갈 수 없는 오류면 취소하고 처음 화면으로 돌아간다.
        cancel_backup()
        return
    finally:
        SystemValues.backup_run_time += time() - SystemValues.backup_start_time

    SystemValues.backup_progress_msg = "백업 완료"
    UiUpdater.stop()
    sleep(0.5)

    # 백업이 제대로 완료되지 않았다면
    if not AppData.failed_result.is_empty():
        call_in_gui_thread(show_aftercheck_result)
    else:
        call_in_gui_thread(show_complete)


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
        UiUpdater.stop()
        sleep(0.5)

        def handle_error():
            _show_error("최적화 중 오류가 발생하였습니다.\nUSB 인식 상태 등을 확인해주세요.")
            show_complete()

        call_in_gui_thread(handle_error)


def btn_prev_compare_again():
    if not _ask_yes_no("백업을 취소하시겠습니까?"):
        return None

    show_home()


def btn_prev_cancel_re_backup():
    if not _ask_yes_no("모든 작업을 취소하시겠습니까?"):
        return None

    show_home()


# 초기 UI 상태 업데이트
show_home()

btn_sel_org.clicked.connect(btn_sel_org_clicked)
btn_sel_target.clicked.connect(btn_sel_target_clicked)
btn_fast_sel.clicked.connect(btn_fast_sel_clicked)
btn_det_sel.clicked.connect(btn_det_sel_clicked)
