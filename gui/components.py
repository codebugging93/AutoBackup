"""
gui/components.py(tkinter)를 PySide6로 번역한 버전입니다.

- 변수명은 기존 components.py / functions.py에서 쓰이는 이름과 최대한 동일하게 맞췄습니다.
  (나중에 functions.py를 PySide6용으로 옮길 때 이름 매핑이 쉽도록 하기 위함)
- 화면 구성(홈 -> 폴더선택 -> 검사모드 -> 진행 -> 결과 -> 완료)은 기존과 동일하게 유지했습니다.
- 색상만 화이트 + suisei_blue 계열로 새로 디자인했습니다.
  배경/여백은 화이트 계열, 버튼/아이콘/포인트 요소는 suisei_blue 계열을 사용합니다.
- switch_frame()에 해당하는 기능은 QStackedWidget(frame_main)의 setCurrentWidget으로 대체됩니다.
"""

import os
import sys
from threading import Event

from PySide6.QtCore import QObject, QSize, Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from system.constants import APPNAME, SUISEI_BLUE


# --- 색상 팔레트 (화이트 + suisei_blue) ---
COLOR_BG = "#F5F9FE"      # 사이드바/카드 등 은은한 배경
COLOR_BLUE = SUISEI_BLUE       # 포인트 컬러 (#75B7EA)
COLOR_BORDER = "#E3EAF3"
COLOR_TEXT = "#28303B"
COLOR_TEXT_SUB = "#8993A6"


def _icon(path: str, size: int) -> QPixmap:
    """ 이미지 경로를 정사각형으로 리사이즈한 QPixmap으로 반환. 파일이 없으면 빈 투명 이미지를 반환. """
    pix = QPixmap(path)
    if pix.isNull():
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        return pix
    return pix.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


# --- QApplication / 메인 윈도우 ---
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

root = QWidget()
root.setWindowTitle(APPNAME)
root.setFixedSize(900, 600)
root.move(220, 40)
if os.path.exists(r"image\logo.ico"):
    root.setWindowIcon(QIcon(r"image\logo.ico"))

root.setStyleSheet(f"""
QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
    font-family: "맑은 고딕", "Segoe UI";
    font-size: 13px;
}}
#LeftBar {{
    background-color: {COLOR_BG};
    border-right: 1px solid {COLOR_BORDER};
}}
#LeftBar QLabel {{
    background-color: transparent;
}}
#BottomBar {{
    background-color: {COLOR_BG};
    border-top: 1px solid {COLOR_BORDER};
}}
#PanelCard {{
    background-color: {COLOR_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
}}
#IconButton {{
    border: 2px solid {COLOR_BORDER};
    border-radius: 18px;
    background-color: {COLOR_BG};
    padding: 18px;
}}
#IconButton:hover {{
    border-color: {COLOR_BLUE};
}}
QPushButton {{
    background-color: {COLOR_BG};
    border: 1px solid {COLOR_BLUE};
    border-radius: 8px;
    color: {COLOR_BLUE};
    padding: 8px 18px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {COLOR_BG};
}}
QPushButton:disabled {{
    color: {COLOR_TEXT_SUB};
    border-color: {COLOR_BORDER};
}}
#PrimaryButton {{
    background-color: {COLOR_BLUE};
    border: none;
    color: white;
}}
#PrimaryButton:hover {{
    background-color: {COLOR_BLUE};
}}
#PrimaryButton:disabled {{
    background-color: {COLOR_BORDER};
    color: {COLOR_TEXT_SUB};
}}
QListWidget {{
    background-color: {COLOR_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
}}
QListWidget::item {{
    padding: 3px 6px;
}}
QListWidget::item:selected {{
    background-color: {COLOR_BLUE};
    color: white;
}}
QProgressBar {{
    background-color: {COLOR_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    height: 14px;
}}
QProgressBar::chunk {{
    background-color: {COLOR_BLUE};
    border-radius: 6px;
}}
#HeaderLabel {{
    font-size: 17px;
    font-weight: 700;
    color: {COLOR_TEXT};
}}
#SubLabel {{
    color: {COLOR_TEXT_SUB};
}}
#ArrowLabel {{
    color: {COLOR_BLUE};
    font-size: 22px;
    font-weight: 700;
}}
""")


# --- 단계표시용 아이콘 (기존과 동일한 이미지 파일 재사용) ---
_STEP_ICON_SIZE = 70

# 현재 단계가 아닐시 사용하는 이미지 (흰색/무채색 배경)
tk_step_home_img = _icon(r"image\step-1.png", _STEP_ICON_SIZE)
tk_step_select_img = _icon(r"image\step-2.png", _STEP_ICON_SIZE)
tk_step_progress_img = _icon(r"image\step-3.png", _STEP_ICON_SIZE)
tk_step_result_img = _icon(r"image\step-4.png", _STEP_ICON_SIZE)
tk_step_backup_img = _icon(r"image\step-5.png", _STEP_ICON_SIZE)
tk_step_complete_img = _icon(r"image\step-6.png", _STEP_ICON_SIZE)

# _inverted 붙은거는 현재 단계에 사용하는 이미지 (블루 배경)
tk_step_home_img_inverted = _icon(r"image\step1.png", _STEP_ICON_SIZE)
tk_step_select_img_inverted = _icon(r"image\step2.png", _STEP_ICON_SIZE)
tk_step_progress_img_inverted = _icon(r"image\step3.png", _STEP_ICON_SIZE)
tk_step_result_img_inverted = _icon(r"image\step4.png", _STEP_ICON_SIZE)
tk_step_backup_img_inverted = _icon(r"image\step5.png", _STEP_ICON_SIZE)
tk_step_complete_img_inverted = _icon(r"image\step6.png", _STEP_ICON_SIZE)

# 폴더 선택 버튼용 아이콘
tk_btn_org_img = _icon(r"image\original_folder.png", 160)
tk_btn_tar_img = _icon(r"image\target_folder.png", 160)


# --- 전체 레이아웃 뼈대: [세로] 본문(가로: 좌측바 + 메인영역) / 하단바 ---
root_layout = QVBoxLayout(root)
root_layout.setContentsMargins(0, 0, 0, 0)
root_layout.setSpacing(0)

body_row = QHBoxLayout()
body_row.setContentsMargins(0, 0, 0, 0)
body_row.setSpacing(0)
root_layout.addLayout(body_row, 1)


# --- 왼쪽 단계 표시 바 ---
frame_LeftBar = QFrame()
frame_LeftBar.setObjectName("LeftBar")
frame_LeftBar.setFixedWidth(70)
body_row.addWidget(frame_LeftBar)

leftbar_layout = QVBoxLayout(frame_LeftBar)
# 오른쪽에 살짝 여백을 둬서 아이콘 라벨이 #LeftBar의 border-right 픽셀까지
# 침범해 가리지 않도록 한다.
leftbar_layout.setContentsMargins(0, 0, 2, 0)
leftbar_layout.setSpacing(0)

label_step_img = QLabel()
label_step_img.setPixmap(tk_step_home_img)
label_step_img2 = QLabel()
label_step_img2.setPixmap(tk_step_select_img)
label_step_img3 = QLabel()
label_step_img3.setPixmap(tk_step_progress_img)
label_step_img4 = QLabel()
label_step_img4.setPixmap(tk_step_result_img)
label_step_img5 = QLabel()
label_step_img5.setPixmap(tk_step_backup_img)
label_step_img6 = QLabel()
label_step_img6.setPixmap(tk_step_complete_img)

# 아이콘끼리는 간격 없이 딱 붙여서 쌓고, 남는 공간은 맨 아래로 몰아둔다.
for _lbl in (label_step_img, label_step_img2, label_step_img3,
             label_step_img4, label_step_img5, label_step_img6):
    _lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    leftbar_layout.addWidget(_lbl)

leftbar_layout.addStretch()


# --- 중앙 화면 메인 프레임 (frame_main): 화면 전환은 QStackedWidget으로 처리 ---
frame_main = QStackedWidget()
body_row.addWidget(frame_main, 1)


# --- 1번 홈 화면 ---
frame_center_home = QWidget()
_home_layout = QVBoxLayout(frame_center_home)
_home_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
_home_layout.setSpacing(10)

_home_title = QLabel(APPNAME)
_home_title.setObjectName("HeaderLabel")
_home_title.setStyleSheet(f"font-size: 30px; color: {COLOR_BLUE}; font-weight: 800;")
_home_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

_home_sub = QLabel("빠른 백업과 동기화를 위한 솔루션")
_home_sub.setStyleSheet(f"font-size: 18px;")
_home_sub.setObjectName("SubLabel")
_home_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

_home_layout.addWidget(_home_title)
_home_layout.addWidget(_home_sub)

frame_main.addWidget(frame_center_home)


# --- 2번 폴더선택 화면 ---
frame_center_select = QWidget()
_select_layout = QHBoxLayout(frame_center_select)
_select_layout.setContentsMargins(40, 30, 40, 30)
_select_layout.setSpacing(20)

# 원본폴더 선택
frame_org_part = QWidget()
_org_layout = QVBoxLayout(frame_org_part)
_org_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
_org_layout.setSpacing(14)

label_original = QLabel("원본폴더")
label_original.setObjectName("HeaderLabel")
label_original.setAlignment(Qt.AlignmentFlag.AlignCenter)

btn_sel_org = QPushButton()
btn_sel_org.setObjectName("IconButton")
btn_sel_org.setIcon(QIcon(tk_btn_org_img))
btn_sel_org.setIconSize(QSize(140, 140))
btn_sel_org.setFixedSize(190, 190)
btn_sel_org.setCursor(Qt.CursorShape.PointingHandCursor)

label_org_path = QLabel("")
label_org_path.setObjectName("SubLabel")
label_org_path.setWordWrap(True)
label_org_path.setAlignment(Qt.AlignmentFlag.AlignCenter)
label_org_path.setFixedWidth(260)

_org_layout.addWidget(label_original)
_org_layout.addWidget(btn_sel_org, alignment=Qt.AlignmentFlag.AlignHCenter)
_org_layout.addWidget(label_org_path)

_select_layout.addWidget(frame_org_part, 1)

# 중앙 화살표 위치
frame_mid_part = QLabel("→")
frame_mid_part.setObjectName("ArrowLabel")
frame_mid_part.setFixedWidth(36)
frame_mid_part.setAlignment(Qt.AlignmentFlag.AlignCenter)
_select_layout.addWidget(frame_mid_part)

# 대상폴더 선택
frame_tar_part = QWidget()
_tar_layout = QVBoxLayout(frame_tar_part)
_tar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
_tar_layout.setSpacing(14)

label_target = QLabel("대상폴더")
label_target.setObjectName("HeaderLabel")
label_target.setAlignment(Qt.AlignmentFlag.AlignCenter)

btn_sel_target = QPushButton()
btn_sel_target.setObjectName("IconButton")
btn_sel_target.setIcon(QIcon(tk_btn_tar_img))
btn_sel_target.setIconSize(QSize(140, 140))
btn_sel_target.setFixedSize(190, 190)
btn_sel_target.setCursor(Qt.CursorShape.PointingHandCursor)

label_tar_path = QLabel("")
label_tar_path.setObjectName("SubLabel")
label_tar_path.setWordWrap(True)
label_tar_path.setAlignment(Qt.AlignmentFlag.AlignCenter)
label_tar_path.setFixedWidth(260)

_tar_layout.addWidget(label_target)
_tar_layout.addWidget(btn_sel_target, alignment=Qt.AlignmentFlag.AlignHCenter)
_tar_layout.addWidget(label_tar_path)

_select_layout.addWidget(frame_tar_part, 1)

frame_main.addWidget(frame_center_select)


# --- 3번 검사선택 화면 ---
frame_center_check = QWidget()
_check_layout = QHBoxLayout(frame_center_check)
_check_layout.setContentsMargins(40, 40, 40, 40)
_check_layout.setSpacing(24)

# 좌측 빠른검사 프레임
frame_fast_check = QWidget()
frame_fast_check.setObjectName("PanelCard")
_fast_layout = QVBoxLayout(frame_fast_check)
_fast_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
_fast_layout.setContentsMargins(20, 30, 20, 30)
_fast_layout.setSpacing(10)

label_fast_check = QLabel("빠른검사")
label_fast_check.setObjectName("HeaderLabel")
label_fast_check.setAlignment(Qt.AlignmentFlag.AlignCenter)

label_fast_expl = QLabel("파일의 메타데이터를 기반으로\n빠른 검사를 진행합니다.")
label_fast_expl.setObjectName("SubLabel")
label_fast_expl.setAlignment(Qt.AlignmentFlag.AlignCenter)

btn_fast_sel = QPushButton("선택")
btn_fast_sel.setObjectName("PrimaryButton")
btn_fast_sel.setFixedWidth(130)

_fast_layout.addWidget(label_fast_check)
_fast_layout.addWidget(label_fast_expl)
_fast_layout.addSpacing(10)
_fast_layout.addWidget(btn_fast_sel, alignment=Qt.AlignmentFlag.AlignHCenter)

_check_layout.addWidget(frame_fast_check, 1)

# 우측 정밀검사 프레임
fram_detail = QWidget()
fram_detail.setObjectName("PanelCard")
_detail_layout = QVBoxLayout(fram_detail)
_detail_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
_detail_layout.setContentsMargins(20, 30, 20, 30)
_detail_layout.setSpacing(10)

label_det_check = QLabel("정밀검사")
label_det_check.setObjectName("HeaderLabel")
label_det_check.setAlignment(Qt.AlignmentFlag.AlignCenter)

label_det_expl = QLabel("파일을 바이트 단위로 정밀 검사합니다.\n시간이 오래 걸릴 수 있습니다.")
label_det_expl.setObjectName("SubLabel")
label_det_expl.setAlignment(Qt.AlignmentFlag.AlignCenter)

btn_det_sel = QPushButton("선택")
btn_det_sel.setObjectName("PrimaryButton")
btn_det_sel.setFixedWidth(130)

_detail_layout.addWidget(label_det_check)
_detail_layout.addWidget(label_det_expl)
_detail_layout.addSpacing(10)
_detail_layout.addWidget(btn_det_sel, alignment=Qt.AlignmentFlag.AlignHCenter)

_check_layout.addWidget(fram_detail, 1)

frame_main.addWidget(frame_center_check)


# --- 4번 프로그레스바 화면 ---
frame_center_progress = QWidget()
_progress_layout = QVBoxLayout(frame_center_progress)
_progress_layout.setContentsMargins(24, 24, 24, 24)
_progress_layout.setSpacing(18)

# 상단(검사/백업) 진행 영역
frame_top_progress = QWidget()
_top_progress_layout = QVBoxLayout(frame_top_progress)
_top_progress_layout.setContentsMargins(0, 0, 0, 0)
_top_progress_layout.setSpacing(6)

frame_top_progress_label = QWidget()
_top_progress_label_layout = QHBoxLayout(frame_top_progress_label)
_top_progress_label_layout.setContentsMargins(0, 0, 0, 0)

label_top_progress = QLabel("파일 검사 중 0/0 (0.0%)")
label_top_progress2 = QLabel("00:00:00")
label_top_progress2.setObjectName("SubLabel")

_top_progress_label_layout.addWidget(label_top_progress)
_top_progress_label_layout.addStretch()
_top_progress_label_layout.addWidget(label_top_progress2)

top_progressbar = QProgressBar()
top_progressbar.setRange(0, 100)
top_progressbar.setTextVisible(False)

label_top_progress3 = QLabel("")
label_top_progress3.setObjectName("SubLabel")
label_top_progress3.setWordWrap(True)

_top_progress_layout.addWidget(frame_top_progress_label)
_top_progress_layout.addWidget(top_progressbar)
_top_progress_layout.addWidget(label_top_progress3)

_progress_layout.addWidget(frame_top_progress)

# 하단(파일 복사) 진행 영역 - 백업 중에만 표시됨(기존 tkinter도 초기엔 숨김)
frame_bottom_progress = QWidget()
_bottom_progress_layout = QVBoxLayout(frame_bottom_progress)
_bottom_progress_layout.setContentsMargins(0, 0, 0, 0)
_bottom_progress_layout.setSpacing(6)

frame_bottom_progress_label = QWidget()
_bottom_progress_label_layout = QHBoxLayout(frame_bottom_progress_label)
_bottom_progress_label_layout.setContentsMargins(0, 0, 0, 0)

label_bottom_progress = QLabel("파일 복사 중 0/0 (0.0%)")
_bottom_progress_label_layout.addWidget(label_bottom_progress)
_bottom_progress_label_layout.addStretch()

bottom_progressbar = QProgressBar()
bottom_progressbar.setRange(0, 100)
bottom_progressbar.setTextVisible(False)

label_bottom_progress3 = QLabel("")
label_bottom_progress3.setObjectName("SubLabel")
label_bottom_progress3.setWordWrap(True)

_bottom_progress_layout.addWidget(frame_bottom_progress_label)
_bottom_progress_layout.addWidget(bottom_progressbar)
_bottom_progress_layout.addWidget(label_bottom_progress3)

_progress_layout.addWidget(frame_bottom_progress)
frame_bottom_progress.hide()  # SystemValues.copy_working이 True일 때만 표시(추후 updater 이식 시 연결)

_progress_layout.addStretch()

frame_main.addWidget(frame_center_progress)


# --- 5번 검사결과표시 화면 ---
frame_center_result = QWidget()
_result_layout = QGridLayout(frame_center_result)
_result_layout.setContentsMargins(24, 20, 24, 20)
_result_layout.setRowStretch(0, 1)
_result_layout.setRowStretch(1, 2)

# 상단 구성 요소들을 묶을 프레임 (비율 1 영역)
frame_result_header = QWidget()
_result_header_layout = QVBoxLayout(frame_result_header)
_result_header_layout.setContentsMargins(0, 0, 0, 0)

lable_expl_result = QLabel("다음 파일들을 백업합니다")
lable_expl_result.setObjectName("HeaderLabel")
_result_header_layout.addWidget(lable_expl_result)

_result_layout.addWidget(frame_result_header, 0, 0)

# 버튼배열 + 하단 리스트
frame_mid_result = QWidget()
_mid_result_layout = QVBoxLayout(frame_mid_result)
_mid_result_layout.setContentsMargins(0, 0, 0, 0)
_mid_result_layout.setSpacing(10)

frame_btn_result = QWidget()
_btn_result_layout = QHBoxLayout(frame_btn_result)
_btn_result_layout.setContentsMargins(0, 0, 0, 0)
_btn_result_layout.setSpacing(8)

btn_result_delete = QPushButton("삭제할 파일(n)")
btn_result_delete2 = QPushButton("삭제할 폴더(n)")
btn_result_copy = QPushButton("복사할 파일(n)")
btn_result_copy2 = QPushButton("복사할 폴더(n)")
btn_result_refresh = QPushButton("갱신할 파일(n)")

for _btn in (btn_result_delete, btn_result_delete2, btn_result_copy,
             btn_result_copy2, btn_result_refresh):
    _btn.clicked.connect(lambda:None)
    _btn_result_layout.addWidget(_btn)
_btn_result_layout.addStretch()

_mid_result_layout.addWidget(frame_btn_result)

mid_result_list = QListWidget()
mid_result_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
# 스크롤바는 QListWidget에 기본 내장되어 있음(Scrollbar 위젯을 따로 만들 필요 없음)
mid_result_scroll = mid_result_list.verticalScrollBar()
_mid_result_layout.addWidget(mid_result_list, 1)

_result_layout.addWidget(frame_mid_result, 1, 0)

frame_main.addWidget(frame_center_result)

# 미리보기용 더미 데이터 (원본 components.py와 동일하게 시각 확인용으로 채워둠)
for _i in range(50):
    mid_result_list.addItem(f"삭제 중앙 {_i + 1}")


# --- 6번 백업완료 화면 ---
frame_center_complete = QWidget()
_complete_layout = QVBoxLayout(frame_center_complete)
_complete_layout.setContentsMargins(30, 36, 30, 30)
_complete_layout.setSpacing(14)
_complete_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

label_complete = QLabel("검사한 시간 : n초")
label_complete2 = QLabel("백업한 시간 : n초")
label_complete3 = QLabel("최적화율 : n%")
for _lbl in (label_complete, label_complete2, label_complete3):
    _lbl.setStyleSheet(f"font-size: 15px; color: {COLOR_TEXT};")
    _complete_layout.addWidget(_lbl)

frame_main.addWidget(frame_center_complete)


# --- 하단 바 ---
frame_bottombar = QFrame()
frame_bottombar.setObjectName("BottomBar")
frame_bottombar.setFixedHeight(60)
root_layout.addWidget(frame_bottombar)

_bottombar_layout = QHBoxLayout(frame_bottombar)
_bottombar_layout.setContentsMargins(20, 10, 20, 10)

btn_Previous = QPushButton("이전")
btn_Previous.setFixedWidth(120)
btn_Previous.clicked.connect(lambda:None)


# 완료단계에서만 표시(기존과 동일하게 기본은 숨김 상태)
btn_optimize = QPushButton("최적화")
btn_optimize.setObjectName("PrimaryButton")
btn_optimize.setFixedWidth(120)
btn_optimize.hide()
btn_optimize.clicked.connect(lambda:None)

btn_begin = QPushButton("시작")
btn_begin.setObjectName("PrimaryButton")
btn_begin.setFixedWidth(120)
btn_begin.clicked.connect(lambda:None)

_bottombar_layout.addWidget(btn_Previous)
_bottombar_layout.addStretch()
_bottombar_layout.addWidget(btn_optimize)
_bottombar_layout.addWidget(btn_begin)


# --- 프레임 변경 배열 (기존 components.py의 frames / labels와 동일한 용도) ---
frames = [
    frame_center_home, frame_center_select, frame_center_check,
    frame_center_progress, frame_center_result, frame_center_complete,
]

labels = [label_step_img, label_step_img2, label_step_img3,
          label_step_img4, label_step_img5, label_step_img6]

current_index = 0

frame_main.setCurrentWidget(frame_center_home)


# --- 스레드 간 안전한 GUI 호출 헬퍼 (tkinter의 root.after(0, func)에 대응) ---
class _GuiInvoker(QObject):
    _invoke = Signal(object)

    def __init__(self):
        super().__init__()
        self._invoke.connect(self._run, Qt.ConnectionType.QueuedConnection)

    def _run(self, fn):
        fn()


_gui_invoker = _GuiInvoker()


def call_in_gui_thread(fn):
    """ 다른 스레드에서 fn을 GUI 스레드에 예약 실행시킵니다. (비동기, 결과를 기다리지 않음) """
    _gui_invoker._invoke.emit(fn)


def call_in_gui_thread_blocking(fn):
    """
    다른 스레드에서 fn을 GUI 스레드에서 실행시키고 완료될 때까지 호출한 스레드를 대기시킵니다.
    (백그라운드 스레드가 오류 메시지창을 띄우고, 사용자가 닫을 때까지 다음 코드를 진행하지 않는
    기존 tkinter 동작을 안전하게 재현하기 위함)
    """
    if QThread.currentThread() is app.thread():
        return fn()

    done = Event()
    result = {}

    def _wrapper():
        try:
            result["value"] = fn()
        finally:
            done.set()

    call_in_gui_thread(_wrapper)
    done.wait()
    return result.get("value")


# --- 단독 실행 시 디자인 미리보기 ---
if __name__ == "__main__":
    root.show()
    sys.exit(app.exec())
