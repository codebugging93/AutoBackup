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
from pathlib import Path
from threading import Thread
from time import sleep, time

from PySide6.QtWidgets import QFileDialog, QMessageBox

from gui.components import *  # noqa: F401,F403  (root, frame_*, btn_*, label_* 등)
from gui.components import call_in_gui_thread
from gui.components import ICON_DIR, ICON_FILE, FILES_ITEM_KEY, add_backup_item, add_empty_item
from gui.updater import UiUpdater
from system.AppData import AppData, reset_appdata
from system.Trashbin import Trashbin
from system.SystemValues import SystemValues
from system.aftercheck import aftercheck
from system.backup import backup, boost
from system.compare import CompareResult, compare
from system.compare import get_dirs_similarity, get_files_similarity, get_optimized_percent
from system.constants import APPNAME
from system.path import PREFIX_MAX_PATH, get_drive_display_name, get_listdir_split, is_dest_in_src, norm_max_path

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


def _show_info(message: str):
    QMessageBox.information(root, APPNAME, message)


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
    btn_begin.clicked.connect(show_select_items)

    # 이전 버튼 기능 변경
    btn_Previous.setText("이전")
    btn_Previous.setEnabled(True)
    btn_Previous.clicked.disconnect()
    btn_Previous.clicked.connect(show_home)
    btn_Previous.show()

    switch_frame(frame_center_select)
    update_sidebar(1)


def show_select_items():
    """ 폴더 선택이 올바른지 확인한 뒤, 원본 폴더 바로 아래의 항목을 고르는 화면을 띄운다. """

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

    # 2. 목록 채우기
    try:
        fill_backup_items(label_org_path.text(), label_tar_path.text())
    except OSError:
        _show_error("폴더의 내용을 읽을 수 없습니다.\n폴더 권한이나 장치 연결 상태를 확인해주세요.")
        return

    # 3. 화면 전환
    btn_begin.setText("다음")
    btn_begin.setEnabled(True)
    btn_begin.clicked.disconnect()
    btn_begin.clicked.connect(show_compare)

    btn_Previous.setText("이전")
    btn_Previous.setEnabled(True)
    btn_Previous.clicked.disconnect()
    btn_Previous.clicked.connect(show_select_folder)

    check_fast_scan.setChecked(AppData.fast_scan) # 처음으로 돌아갔다 오면 기본값(빠른검사)으로 초기화되어 있음
    switch_frame(frame_center_items)
    update_sidebar(1)


def check_fast_scan_clicked(checked: bool):
    """ 빠른 검사 체크박스: 체크 = 빠른검사, 해제 = 정밀검사 """
    AppData.fast_scan = checked
    if not checked:
        _show_info("정밀검사를 진행합니다.\n파일을 바이트 단위로 정밀 검사하므로 시간이 오래 걸릴 수 있습니다.")


def _read_top_level(path: str):
    """
    path 바로 아래의 내용물을 읽어서 반환한다. (get_listdir_split 결과)
    드라이브 루트이면 탐색기에 안 보이는 숨김 항목과 AutoBackup_휴지통을 뺀다.
    """
    is_drive_root = Path(path).parent == Path(path) # 드라이브 루트는 부모가 자기 자신이다
    entries = get_listdir_split(path, skip_hidden=is_drive_root)
    if is_drive_root:
        entries.dirs.pop(APPNAME + "_휴지통", None)
    return entries


def fill_backup_items(org_path: str, tar_path: str):
    """
    원본/대상 폴더 바로 아래의 내용물을 집합으로 나눠서 범위 화면의 세 칸을 채운다.
    처음에는 모두 체크된 상태(= 동기화)로 둔다.

        복사할 항목: 원본에만 있음 / 삭제할 항목: 대상에만 있음 / 검사할 항목: 양쪽에 다 있음

    목록은 폴더만 보여준다. 두 폴더 바로 아래의 파일은 하나로 묶어서
    검사할 항목 맨 위에 한 줄로만 보여준다. (체크하면 복사/삭제/검사를 모두 한다)
    폴더를 읽지 못하면 OSError가 그대로 올라가며, 이때 기존 목록은 건드리지 않는다.
    """
    org = _read_top_level(org_path)
    tar = _read_top_level(tar_path)

    # 폴더: 이름 순서는 윈도우가 돌려준 순서 그대로 (복사/검사는 원본 쪽, 삭제는 대상 쪽 순서)
    copy_dirs = [name for name in org.dirs if name not in tar.dirs]
    delete_dirs = [name for name in tar.dirs if name not in org.dirs]
    check_dirs = [name for name in org.dirs if name in tar.dirs]

    # 파일: 개수만 센다
    # 루트 파일 검사(run_compare)와 같은 기준으로 센다.
    # 한쪽이라도 드라이브 루트이면 양쪽 모두 숨김 파일을 뺀다.
    org_files = org.files.keys()
    tar_files = tar.files.keys()
    org_is_drive = Path(org_path).parent == Path(org_path)
    tar_is_drive = Path(tar_path).parent == Path(tar_path)
    if org_is_drive or tar_is_drive:
        org_files = get_listdir_split(org_path, skip_hidden=True).files.keys()
        tar_files = get_listdir_split(tar_path, skip_hidden=True).files.keys()

    copy_files = len(org_files - tar_files)
    delete_files = len(tar_files - org_files)
    check_files = len(org_files & tar_files)

    # 파일이 하나라도 있으면 묶음 행의 문구를 만든다. (삭제가 숨지 않도록 개수를 함께 보여준다)
    files_text = ""
    if copy_files + delete_files + check_files > 0:
        files_text = f"두 폴더 바로 아래의 파일 (복사 {copy_files:,} · 삭제 {delete_files:,} · 검사 {check_files:,})"

    # 다 읽은 뒤에 화면을 바꾼다.
    label_copy_items.setText(f"복사할 항목 ({len(copy_dirs)}개)")
    _fill_one_list(list_copy_items, copy_dirs, "")

    label_delete_items.setText(f"삭제할 항목 ({len(delete_dirs)}개)")
    _fill_one_list(list_delete_items, delete_dirs, "")

    # 파일 묶음 행도 검사할 항목 하나로 센다.
    check_count = len(check_dirs)
    if files_text != "":
        check_count += 1
    label_check_items.setText(f"검사할 항목 ({check_count}개)")
    _fill_one_list(list_check_items, check_dirs, files_text)


def _fill_one_list(item_list, dir_names, files_text):
    """ 범위 화면의 목록 하나를 채운다. (파일 묶음 한 줄 -> 폴더들 -> 비어 있으면 "현재 없음")
        files_text가 빈 문자열이면 파일 묶음 행을 넣지 않는다. """
    item_list.clear()

    # 파일은 묶음 한 줄로
    if files_text != "":
        add_backup_item(item_list, ICON_FILE, files_text, FILES_ITEM_KEY)

    # 폴더
    for name in dir_names:
        add_backup_item(item_list, ICON_DIR, name, name)

    # 아무것도 없으면
    if item_list.count() == 0:
        add_empty_item(item_list)

    update_select_all(item_list)


def show_compare():
    # 백업할 항목을 하나도 고르지 않은 경우
    if not is_any_backup_item_checked():
        _show_error("백업할 항목을 하나 이상 선택해주세요.")
        return

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

    dirs_similarity = AppData.dirs_similarity
    files_similarity = AppData.files_similarity

    btn_begin.setText("백업")
    btn_begin.setEnabled(True)
    btn_begin.clicked.disconnect()
    btn_begin.clicked.connect(show_backup)

    btn_Previous.setText("이전")
    btn_Previous.setEnabled(True)
    btn_Previous.clicked.disconnect()
    btn_Previous.clicked.connect(btn_prev_compare_again)
    btn_Previous.show() # 완료 화면 등에서 숨겨진 채로 넘어와도 다시 보이게 한다

    # 변경 사항 카드 업데이트
    update_changes_card({
        "삭제할 파일": len(res.files_rmv),
        "삭제할 폴더": len(res.dirs_rmv),
        "복사할 파일": len(res.files_copy),
        "복사할 폴더": len(res.dirs_copy),
        "변경할 파일": len(res.files_renew),
    })

    # 경로 표시
    label_org_path.setText(res.org_path.removeprefix(PREFIX_MAX_PATH))
    label_tar_path.setText(res.tar_path.removeprefix(PREFIX_MAX_PATH))
    # 결과 화면의 경로 카드도 같은 값으로 채운다.
    label_result_org.setText(label_org_path.text())
    label_result_tar.setText(label_tar_path.text())

    # 유사도 표시
    # 유사도가 음수이면 차트 대신 "폴더 없음"/"파일 없음"이 표시된다.
    pie_dirs_similarity.set_similarity(dirs_similarity)
    pie_files_similarity.set_similarity(files_similarity)

    # 화면 전환
    result_tabs.setCurrentIndex(0) # 항상 개요 탭부터 보여준다
    switch_frame(frame_center_result)
    update_sidebar(3)

    # 유저가 폴더를 잘못 선택함을 알림
    # 폴더 유사도와 파일 유사도 중 어느 하나라도 기준치보다 낮으면 경고한다.
    # 음수는 잴 대상이 없었다는 뜻이므로 판단에서 제외한다.
    
    SIMILARITY_WARNING_THRESHOLD = 30.0 # 폴더/파일 유사도가 이 값보다 낮으면 폴더를 잘못 고른 것으로 보고 경고한다.
    if 0 <= dirs_similarity < SIMILARITY_WARNING_THRESHOLD or 0 <= files_similarity < SIMILARITY_WARNING_THRESHOLD:
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


    update_complete_screen(
        AppData.backup_success,
        AppData.compare_run_time,
        AppData.backup_run_time,
        AppData.optimized_percent,
    )

    btn_Previous.hide()
    switch_frame(frame_center_complete)
    update_sidebar(5)

    if not AppData.backup_success:
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
    label_org_drive.setText(get_drive_display_name(path)) # 예) "로컬 디스크 (C:)"


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
    label_tar_drive.setText(get_drive_display_name(path))


def run_compare():
    """
    compare()를 돌려 AppData.compare_results를 갱신한다.
    """

    # 범위 화면에서 고른 항목
    copy_dirs = get_checked_backup_items(list_copy_items)       # 복사할 폴더 이름들
    delete_dirs = get_checked_backup_items(list_delete_items)   # 삭제할 폴더 이름들
    check_dirs = get_checked_backup_items(list_check_items)     # 검사할 폴더 이름들
    root_files = is_backup_files_checked(list_check_items)      # 루트 파일 묶음 행 체크 여부

    # 진행 화면은 두 줄이다.
    # 윗줄: 몇 번째 폴더를 검사 중인지 
    SystemValues.progress_start_time = time()
    SystemValues.top_progress_msg = "폴더 검사 중"
    SystemValues.top_progress_val = 0
    SystemValues.top_progress_max = len(check_dirs)
    if root_files: # 루트 폴더도 검사할거면 1 추가
        SystemValues.top_progress_max += 1
    SystemValues.top_progress_path = ""

    # 아랫줄: 지금 검사 중인 폴더 안의 파일 진행률 (compare가 채운다)
    SystemValues.bottom_progress_msg = "파일 검사 중"
    SystemValues.bottom_progress_visible = True
    SystemValues.bottom_progress_val = 0
    SystemValues.bottom_progress_max = 0
    SystemValues.bottom_progress_path = ""

    UiUpdater.start()

    compare_results = [] # 폴더마다 compare한 결과를 모아둔다

    try:
        # 1. 루트에 대한 result를 먼저 만든다.
        # 루트 파일을 체크했으면 루트만 compare하고, 아니면 빈 result에서 시작한다.
        if root_files:
            SystemValues.top_progress_path = label_org_path.text() # 루트 파일 검사 중

            # 원본이나 대상 중 하나라도 드라이브 루트이면 숨김 파일(pagefile.sys 등)을 뺀다.
            # 드라이브 루트는 부모가 자기 자신이다. (_read_top_level과 같은 기준)
            org_is_drive = Path(label_org_path.text()).parent == Path(label_org_path.text())
            tar_is_drive = Path(label_tar_path.text()).parent == Path(label_tar_path.text())
            skip_hidden = org_is_drive or tar_is_drive

            root_result = compare(
                label_org_path.text(),
                label_tar_path.text(),
                AppData.fast_scan,
                root_only=True,
                skip_hidden=skip_hidden,
            )
            SystemValues.top_progress_val += 1
        else:
            root_result = CompareResult()
            # compare가 만든 result와 경로 형식을 맞춘다. (260자 경로 제한 우회)
            root_result.org_path = norm_max_path(label_org_path.text())
            root_result.tar_path = norm_max_path(label_tar_path.text())

        # 사용자가 고른 폴더를 compare와 같은 규칙의 절대경로로 합친다.
        for name in copy_dirs: # 복사할 것은 원본 쪽에 있다.
            root_result.dirs_copy.append(os.path.join(root_result.org_path, name))

        for name in delete_dirs: # 삭제할 것은 대상 쪽에 있다.
            root_result.dirs_rmv.append(os.path.join(root_result.tar_path, name))

        # 루트의 폴더들도 폴더 집합 크기에 센다. (root_only compare는 루트의 폴더를 세지 않으므로)
        # 복사/삭제할 폴더는 한쪽에만 있고, 검사할 폴더는 양쪽에 다 있다.
        root_result.dirs_universal_set_count += len(copy_dirs) + len(delete_dirs) + len(check_dirs)
        root_result.dirs_intersection_set_count += len(check_dirs)

        compare_results.append(root_result) # 0번은 루트 result

        # 2. 검사할 폴더마다 원본/대상의 같은 이름 폴더끼리 compare한다.
        for name in check_dirs:
            SystemValues.top_progress_path = name

            # 하단 진행률 초기화 
            SystemValues.bottom_progress_val = 0
            SystemValues.bottom_progress_max = 0
            SystemValues.bottom_progress_path = ""

            org_dir = os.path.join(label_org_path.text(), name)
            tar_dir = os.path.join(label_tar_path.text(), name)

            result = compare(org_dir, tar_dir, AppData.fast_scan)
            compare_results.append(result)
            SystemValues.top_progress_val += 1

        AppData.compare_results = compare_results

        # 3. 모든 result를 합친 종합 수치를 기록한다.
        AppData.dirs_similarity = get_dirs_similarity(compare_results)
        AppData.files_similarity = get_files_similarity(compare_results)
        AppData.optimized_percent = get_optimized_percent(compare_results)

    except Exception:
        cancel_task("검사 중 오류가 발생하였습니다.\nUSB 인식 상태 등을 확인해주세요.")
        return 

    AppData.compare_run_time = time() - SystemValues.progress_start_time
    UiUpdater.stop()
    sleep(0.5)
    SystemValues.bottom_progress_visible = False

    call_in_gui_thread(show_compare_result)


def run_backup():
    # ---------- 백업 ----------
    UiUpdater.start(UiUpdater.update_backup)
    SystemValues.progress_start_time = time()

    try:
        backup(AppData.compare_result)
        failed = aftercheck(AppData.compare_result, AppData.fast_scan)
    except Exception:
        cancel_task("백업 중 오류가 발생하였습니다.\nUSB 인식 상태 등을 확인해주세요.")
        return

    AppData.backup_run_time = time() - SystemValues.progress_start_time
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
        label_org_drive.setText("")
        label_tar_drive.setText("")

        show_home()

    call_in_gui_thread(handle_error)


def run_boost():
    try:
        UiUpdater.start(UiUpdater.update_backup)
        SystemValues.top_progress_msg = "검사 속도 향상을 위한 최적화"

        SystemValues.progress_start_time = time()
        boost(AppData.compare_result)

        SystemValues.top_progress_msg = "최적화 완료"
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
# toggled가 아니라 clicked에 연결: 사용자가 직접 눌렀을 때만 반응하고,
# 화면을 열 때 setChecked로 상태를 맞추는 것으로는 안내창이 뜨지 않는다.
check_fast_scan.clicked.connect(check_fast_scan_clicked)
