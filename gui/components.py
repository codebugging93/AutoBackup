"""
gui/components.py(tkinter)를 PySide6로 번역한 버전입니다.

- 변수명은 기존 components.py / functions.py에서 쓰이는 이름과 최대한 동일하게 맞췄습니다.
  (나중에 functions.py를 PySide6용으로 옮길 때 이름 매핑이 쉽도록 하기 위함)
- 화면 구성(홈 -> 폴더선택 -> 검사모드 -> 진행 -> 결과 -> 완료)은 기존과 동일하게 유지했습니다.
- 색상만 화이트 + suisei_blue 계열로 새로 디자인했습니다.
  배경/여백은 화이트 계열, 버튼/아이콘/포인트 요소는 suisei_blue 계열을 사용합니다.
- switch_frame()에 해당하는 기능은 QStackedWidget(frame_main)의 setCurrentWidget으로 대체됩니다.
"""

import math
import os
import sys
from threading import Event

from PySide6.QtCore import QObject, QRectF, QSize, Qt, QThread, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from system.constants import APPNAME, SUISEI_BLUE


# --- 색상 팔레트 (화이트 + suisei_blue) ---
COLOR_BG = "#F5F9FE"      # 사이드바/카드 등 은은한 배경
COLOR_BLUE = SUISEI_BLUE       # 포인트 컬러 (#75B7EA)
COLOR_BORDER = "#E3EAF3"
COLOR_TEXT = "#28303B"         # 기본 글자색(검은색 계열). 색을 따로 지정하지 않은 QLabel 등은 전부 이 색을 쓴다.
COLOR_TEXT_SUB = "#8993A6"     # 흐린 글자색(회색). 카드 제목, 안내 문구 등
COLOR_BLUE_PRESSED = QColor(COLOR_BLUE).darker(115).name()  # 파란 버튼을 누르고 있을 때 (포인트 컬러보다 15% 어둡게)
COLOR_BLUE_SOFT = "#DCEBF8"    # 흰 버튼을 누르고 있을 때 깔리는 옅은 파랑


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


def get_image(image_name:str):
    return os.path.join("image", image_name)


# --- QApplication / 메인 윈도우 ---
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

root = QWidget()
root.setWindowTitle(APPNAME)
root.setFixedSize(900, 600)
root.move(220, 40)
if os.path.exists(get_image("logo.ico")):
    root.setWindowIcon(QIcon(get_image("logo.ico")))

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
QPushButton:pressed {{
    background-color: {COLOR_BLUE_SOFT};
    padding: 9px 18px 7px 18px; /* 글자를 1px 아래로 내려 눌린 느낌을 준다 */
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
#PrimaryButton:pressed {{
    background-color: {COLOR_BLUE_PRESSED};
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
#DriveLabel {{
    color: {COLOR_BLUE};
    font-size: 14px;
    font-weight: 700;
}}
""")


# --- 단계표시용 아이콘 (기존과 동일한 이미지 파일 재사용) ---
_STEP_ICON_SIZE = 70

# 현재 단계가 아닐시 사용하는 이미지 (흰색/무채색 배경)
tk_step_home_img = _icon(get_image("step-1.png"), _STEP_ICON_SIZE)
tk_step_select_img = _icon(get_image("step-2.png"), _STEP_ICON_SIZE)
tk_step_progress_img = _icon(get_image("step-3.png"), _STEP_ICON_SIZE)
tk_step_result_img = _icon(get_image("step-4.png"), _STEP_ICON_SIZE)
tk_step_backup_img = _icon(get_image("step-5.png"), _STEP_ICON_SIZE)
tk_step_complete_img = _icon(get_image("step-6.png"), _STEP_ICON_SIZE)

# _inverted 붙은거는 현재 단계에 사용하는 이미지 (블루 배경)
tk_step_home_img_inverted = _icon(get_image("step1.png"), _STEP_ICON_SIZE)
tk_step_select_img_inverted = _icon(get_image("step2.png"), _STEP_ICON_SIZE)
tk_step_progress_img_inverted = _icon(get_image("step3.png"), _STEP_ICON_SIZE)
tk_step_result_img_inverted = _icon(get_image("step4.png"), _STEP_ICON_SIZE)
tk_step_backup_img_inverted = _icon(get_image("step5.png"), _STEP_ICON_SIZE)
tk_step_complete_img_inverted = _icon(get_image("step6.png"), _STEP_ICON_SIZE)

# 폴더 선택 버튼용 아이콘
tk_btn_org_img = _icon(get_image("original_folder.png"), 160)
tk_btn_tar_img = _icon(get_image("target_folder.png"), 160)


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
# 원본/대상 두 열의 [제목 - 아이콘 - 장치 - 경로]가 항상 같은 높이에 오도록 격자로 배치한다.
# 열마다 따로 세로 가운데 정렬을 하면, 경로가 길어 줄바꿈된 쪽만 위로 밀려 좌우가 어긋난다.
frame_center_select = QWidget()
_select_layout = QGridLayout(frame_center_select)
_select_layout.setContentsMargins(40, 30, 40, 30)
_select_layout.setHorizontalSpacing(20)
_select_layout.setVerticalSpacing(14)

# 열: 원본 / 화살표 / 대상
_SEL_COL_ORG = 0
_SEL_COL_ARROW = 1
_SEL_COL_TAR = 2
_select_layout.setColumnStretch(_SEL_COL_ORG, 1)
_select_layout.setColumnStretch(_SEL_COL_TAR, 1)

# 행: 0과 5는 여백. 내용(1~4행)이 세로 가운데에 오도록 위아래로 남는 공간을 나눠 가진다.
_SEL_ROW_TITLE = 1
_SEL_ROW_BUTTON = 2
_SEL_ROW_DRIVE = 3
_SEL_ROW_PATH = 4
_select_layout.setRowStretch(0, 1)
_select_layout.setRowStretch(5, 1)

# 원본폴더 선택
label_original = QLabel("원본폴더")
label_original.setObjectName("HeaderLabel")
label_original.setAlignment(Qt.AlignmentFlag.AlignCenter)

btn_sel_org = QPushButton()
btn_sel_org.setObjectName("IconButton")
btn_sel_org.setIcon(QIcon(tk_btn_org_img))
btn_sel_org.setIconSize(QSize(140, 140))
btn_sel_org.setFixedSize(190, 190)
btn_sel_org.setCursor(Qt.CursorShape.PointingHandCursor)

# 선택한 폴더가 어느 장치에 있는지 한 줄로 알려준다. ("USB(내 USB)" 등)
# 폴더를 고르기 전에도 자리를 차지하도록 높이를 고정해서 레이아웃이 흔들리지 않게 한다.
label_org_drive = QLabel("")
label_org_drive.setObjectName("DriveLabel")
label_org_drive.setAlignment(Qt.AlignmentFlag.AlignCenter)
label_org_drive.setFixedWidth(260)
label_org_drive.setFixedHeight(20)

label_org_path = QLabel("")
label_org_path.setObjectName("SubLabel")
label_org_path.setWordWrap(True)
label_org_path.setAlignment(Qt.AlignmentFlag.AlignCenter)
label_org_path.setFixedWidth(260)

# 경로는 위에서부터 채워야 한쪽만 길어져도 좌우 시작 높이가 같다.
_PATH_ALIGN = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop

_select_layout.addWidget(label_original, _SEL_ROW_TITLE, _SEL_COL_ORG, Qt.AlignmentFlag.AlignHCenter)
_select_layout.addWidget(btn_sel_org, _SEL_ROW_BUTTON, _SEL_COL_ORG, Qt.AlignmentFlag.AlignHCenter)
_select_layout.addWidget(label_org_drive, _SEL_ROW_DRIVE, _SEL_COL_ORG, Qt.AlignmentFlag.AlignHCenter)
_select_layout.addWidget(label_org_path, _SEL_ROW_PATH, _SEL_COL_ORG, _PATH_ALIGN)

# 중앙 화살표. 네 행에 걸쳐 놓고 그 안에서 세로 가운데에 둔다.
frame_mid_part = QLabel("→")
frame_mid_part.setObjectName("ArrowLabel")
frame_mid_part.setFixedWidth(36)
frame_mid_part.setAlignment(Qt.AlignmentFlag.AlignCenter)
_select_layout.addWidget(
    frame_mid_part,
    _SEL_ROW_TITLE, _SEL_COL_ARROW, # 시작 위치
    4, 1,                           # 4개 행에 걸침
    Qt.AlignmentFlag.AlignCenter,
)

# 대상폴더 선택
label_target = QLabel("대상폴더")
label_target.setObjectName("HeaderLabel")
label_target.setAlignment(Qt.AlignmentFlag.AlignCenter)

btn_sel_target = QPushButton()
btn_sel_target.setObjectName("IconButton")
btn_sel_target.setIcon(QIcon(tk_btn_tar_img))
btn_sel_target.setIconSize(QSize(140, 140))
btn_sel_target.setFixedSize(190, 190)
btn_sel_target.setCursor(Qt.CursorShape.PointingHandCursor)

label_tar_drive = QLabel("")
label_tar_drive.setObjectName("DriveLabel")
label_tar_drive.setAlignment(Qt.AlignmentFlag.AlignCenter)
label_tar_drive.setFixedWidth(260)
label_tar_drive.setFixedHeight(20)

label_tar_path = QLabel("")
label_tar_path.setObjectName("SubLabel")
label_tar_path.setWordWrap(True)
label_tar_path.setAlignment(Qt.AlignmentFlag.AlignCenter)
label_tar_path.setFixedWidth(260)

_select_layout.addWidget(label_target, _SEL_ROW_TITLE, _SEL_COL_TAR, Qt.AlignmentFlag.AlignHCenter)
_select_layout.addWidget(btn_sel_target, _SEL_ROW_BUTTON, _SEL_COL_TAR, Qt.AlignmentFlag.AlignHCenter)
_select_layout.addWidget(label_tar_drive, _SEL_ROW_DRIVE, _SEL_COL_TAR, Qt.AlignmentFlag.AlignHCenter)
_select_layout.addWidget(label_tar_path, _SEL_ROW_PATH, _SEL_COL_TAR, _PATH_ALIGN)

frame_main.addWidget(frame_center_select)


# --- 2-1번 백업 범위 선택 화면 ---
# 원본과 대상 폴더 바로 아래의 내용물을 집합으로 나눠서 보여주고, 무엇을 백업할지 고르게 한다.
#   1행 왼쪽: 복사할 항목 (원본에만 있음) / 1행 오른쪽: 삭제할 항목 (대상에만 있음)
#   2행     : 검사할 항목 (양쪽에 다 있음)
frame_center_items = QWidget()
_items_layout = QVBoxLayout(frame_center_items)
_items_layout.setContentsMargins(24, 16, 24, 16)
_items_layout.setSpacing(12)

label_items_title = QLabel("백업할 폴더를 선택해주세요")
label_items_title.setStyleSheet(f"font-size: 17px; color: {COLOR_TEXT}; font-weight: 700;")
_items_layout.addWidget(label_items_title)

# 세 목록이 함께 쓰는 스타일 (objectName이 같으므로 같은 문자열을 각 목록에 입힌다)
_BACKUP_LIST_STYLE = f"""
#BackupItems {{
    border: none;
    background-color: transparent;
}}
#BackupItems::item {{
    padding: 0px 4px;
    height: 26px; /* 윈도우 11 기본 스타일은 행을 터치용으로 높게(약 40px) 잡으므로 직접 지정한다 */
}}
/* 체크박스: 해제 = 흰 상자 + 회색 테두리, 체크 = 파란색으로 채움 */
#BackupItems::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {COLOR_TEXT_SUB};
    border-radius: 4px;
    background-color: white;
}}
#BackupItems::indicator:checked {{
    border-color: {COLOR_BLUE};
    background-color: {COLOR_BLUE};
    image: url({get_image("check.svg").replace(os.sep, "/")}); /* 흰색 체크 표시 */
}}
/* 스크롤바: 얇고 둥근 막대 */
#BackupItems QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px 0px 2px 0px;
}}
#BackupItems QScrollBar::handle:vertical {{
    background: {COLOR_BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
#BackupItems QScrollBar::handle:vertical:hover {{
    background: {COLOR_TEXT_SUB};
}}
#BackupItems QScrollBar::add-line:vertical, #BackupItems QScrollBar::sub-line:vertical {{
    height: 0px;
}}
#BackupItems QScrollBar::add-page:vertical, #BackupItems QScrollBar::sub-page:vertical {{
    background: transparent;
}}
"""


def _checkbox_style(object_name: str, font_size: int, color: str) -> str:
    """ 목록의 체크박스와 같은 모양의 QCheckBox 스타일. (일부만 체크된 상태는 옅은 파랑으로 채움) """
    return f"""
#{object_name} {{
    font-size: {font_size}px;
    color: {color};
    spacing: 8px;
}}
#{object_name}::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {COLOR_TEXT_SUB};
    border-radius: 4px;
    background-color: white;
}}
#{object_name}::indicator:checked {{
    border-color: {COLOR_BLUE};
    background-color: {COLOR_BLUE};
    image: url({get_image("check.svg").replace(os.sep, "/")});
}}
#{object_name}::indicator:indeterminate {{
    border-color: {COLOR_BLUE};
    background-color: {COLOR_BLUE_SOFT};
}}
#{object_name}::indicator:disabled {{
    border-color: {COLOR_BORDER};
    background-color: {COLOR_BG};
}}
#{object_name}:disabled {{
    color: {COLOR_BORDER};
}}
"""


_select_all_boxes = {}  # 목록 -> 그 칸의 "전체 선택" 체크박스


def _checkable_items(item_list: QListWidget) -> list:
    """ 목록에서 체크박스가 있는 행만 돌려준다. ("현재 없음" 행 제외) """
    items = []
    for i in range(item_list.count()):
        item = item_list.item(i)
        if item.data(Qt.ItemDataRole.CheckStateRole) is not None:
            items.append(item)
    return items


def update_select_all(item_list: QListWidget):
    """ 목록의 체크 상태에 맞춰 "전체 선택" 체크박스를 맞춘다. (전부 = 체크 / 일부 = 중간 / 없음 = 해제) """
    box = _select_all_boxes[item_list]
    items = _checkable_items(item_list)
    checked = 0
    for item in items:
        if item.checkState() == Qt.CheckState.Checked:
            checked += 1

    box.setEnabled(len(items) > 0) # 고를 것이 없는 칸("현재 없음")에서는 누를 수 없게 한다
    if len(items) > 0 and checked == len(items):
        box.setCheckState(Qt.CheckState.Checked)
    elif checked == 0:
        box.setCheckState(Qt.CheckState.Unchecked)
    else:
        box.setCheckState(Qt.CheckState.PartiallyChecked)


def _select_all_clicked(item_list: QListWidget):
    """ "전체 선택"을 누르면: 전부 체크되어 있으면 전부 해제, 아니면 전부 체크 """
    items = _checkable_items(item_list)
    all_checked = True
    for item in items:
        if item.checkState() != Qt.CheckState.Checked:
            all_checked = False

    new_state = Qt.CheckState.Unchecked if all_checked else Qt.CheckState.Checked
    for item in items:
        item.setCheckState(new_state)
    update_select_all(item_list)


def toggle_backup_item(item: QListWidgetItem):
    """ 행을 클릭하면 체크 상태를 뒤집는다. 체크박스가 없는 행("현재 없음")은 무시한다. """
    if item.data(Qt.ItemDataRole.CheckStateRole) is None:
        return
    if item.checkState() == Qt.CheckState.Checked:
        item.setCheckState(Qt.CheckState.Unchecked)
    else:
        item.setCheckState(Qt.CheckState.Checked)
    update_select_all(item.listWidget())


def _make_scope_section():
    """ 범위 화면의 칸 하나(제목 + 전체 선택 + 체크박스 목록)를 만든다. 카드, 제목 라벨, 목록을 함께 반환한다. """
    card = QFrame()
    card.setObjectName("PanelCard")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 10, 14, 8)
    layout.setSpacing(4)

    title = QLabel("")
    title.setStyleSheet(f"font-size: 14px; color: {COLOR_TEXT}; font-weight: 700;")

    select_all = QCheckBox()
    select_all.setObjectName("SelectAllCheck")
    select_all.setToolTip("전체 선택")
    select_all.setTristate(True) # 일부만 체크된 상태를 보여주기 위함 (누를 때는 전체 체크/해제만 함)
    select_all.setCursor(Qt.CursorShape.PointingHandCursor)
    # 글자가 없으므로 글자용 간격(spacing)은 없앤다
    select_all.setStyleSheet(_checkbox_style("SelectAllCheck", 12, COLOR_TEXT_SUB) + "#SelectAllCheck { spacing: 0px; }")

    header = QHBoxLayout()
    header.setContentsMargins(7, 0, 0, 0) # 아래 목록의 체크박스와 세로줄을 맞춤
    header.setSpacing(8)
    header.addWidget(select_all) # 제목 왼쪽에 둔다
    header.addWidget(title)
    header.addStretch()

    item_list = QListWidget()
    item_list.setObjectName("BackupItems")
    # 행을 "선택"하는 기능은 쓰지 않는다. 클릭하면 체크만 바뀐다.
    item_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
    item_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    item_list.setIconSize(QSize(16, 16))
    item_list.setStyleSheet(_BACKUP_LIST_STYLE)
    item_list.itemClicked.connect(toggle_backup_item)

    _select_all_boxes[item_list] = select_all
    select_all.clicked.connect(lambda _checked=False, l=item_list: _select_all_clicked(l))

    layout.addLayout(header)
    layout.addWidget(item_list, 1)
    return card, title, item_list


card_copy_items, label_copy_items, list_copy_items = _make_scope_section()
card_delete_items, label_delete_items, list_delete_items = _make_scope_section()
card_check_items, label_check_items, list_check_items = _make_scope_section()

# 격자: 1행과 2행은 50:50, 1행의 두 칸도 50:50
frame_scope_grid = QWidget()
_scope_grid_layout = QGridLayout(frame_scope_grid)
_scope_grid_layout.setContentsMargins(0, 0, 0, 0)
_scope_grid_layout.setHorizontalSpacing(12)
_scope_grid_layout.setVerticalSpacing(12)
_scope_grid_layout.setRowStretch(0, 1)
_scope_grid_layout.setRowStretch(1, 1)
_scope_grid_layout.setColumnStretch(0, 1)
_scope_grid_layout.setColumnStretch(1, 1)

_scope_grid_layout.addWidget(card_copy_items, 0, 0)
_scope_grid_layout.addWidget(card_delete_items, 0, 1)
_scope_grid_layout.addWidget(card_check_items, 1, 0, 1, 2)  # 2행은 두 칸에 걸침

_items_layout.addWidget(frame_scope_grid, 1)

# 검사 방식: 체크 = 빠른검사, 해제 = 정밀검사 (AppData.fast_scan과 연결은 functions.py에서)
check_fast_scan = QCheckBox("빠른 검사")
check_fast_scan.setObjectName("FastScanCheck")
check_fast_scan.setChecked(True)
check_fast_scan.setCursor(Qt.CursorShape.PointingHandCursor)
check_fast_scan.setStyleSheet(_checkbox_style("FastScanCheck", 13, COLOR_TEXT))
_items_layout.addWidget(check_fast_scan, alignment=Qt.AlignmentFlag.AlignRight) # 다음 버튼이 있는 오른쪽에 둔다

frame_main.addWidget(frame_center_items)

ICON_DIR = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
ICON_FILE = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
FILES_ITEM_KEY = None


def add_backup_item(item_list: QListWidget, icon, text, key):
    """ 목록에 체크된 행 하나를 추가한다. key는 폴더 이름이고, 파일 개수 행은 FILES_ITEM_KEY다. """
    item = QListWidgetItem(icon, text)
    item.setData(Qt.ItemDataRole.UserRole, key)
    # ItemIsUserCheckable을 빼서 체크박스를 직접 눌러도 Qt가 따로 토글하지 않게 한다.
    # 체크는 행 클릭(toggle_backup_item) 한 곳에서만 바뀌므로 두 번 토글되는 일이 없다.
    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    item.setCheckState(Qt.CheckState.Checked)
    item_list.addItem(item)


def add_empty_item(item_list: QListWidget):
    """ 칸에 아무것도 없을 때 "현재 없음"을 표시한다. 체크박스가 없어 선택 결과에 들어가지 않는다. """
    item = QListWidgetItem("현재 없음")
    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
    item.setForeground(QColor(COLOR_TEXT_SUB))
    item_list.addItem(item)


def get_checked_backup_items(item_list: QListWidget) -> list:
    """ 목록에서 체크된 폴더의 이름 목록을 반환한다. (파일 개수 행은 포함하지 않음) """
    names = []
    for i in range(item_list.count()):
        item = item_list.item(i)
        key = item.data(Qt.ItemDataRole.UserRole)
        if key is not FILES_ITEM_KEY and item.checkState() == Qt.CheckState.Checked:
            names.append(key)
    return names


def is_backup_files_checked(item_list: QListWidget) -> bool:
    """ 목록의 파일 개수 행이 체크되어 있는지 반환한다. 파일이 없어서 행이 없으면 False. """
    for i in range(item_list.count()):
        item = item_list.item(i)
        if item.data(Qt.ItemDataRole.CheckStateRole) is None:
            continue  # "현재 없음" 행
        if item.data(Qt.ItemDataRole.UserRole) is FILES_ITEM_KEY:
            return item.checkState() == Qt.CheckState.Checked
    return False


def is_any_backup_item_checked() -> bool:
    """ 범위 화면의 세 목록 중 체크된 항목이 하나라도 있는지 반환한다. """
    for item_list in (list_copy_items, list_delete_items, list_check_items):
        for i in range(item_list.count()):
            if item_list.item(i).checkState() == Qt.CheckState.Checked:
                return True
    return False


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
frame_bottom_progress.hide()  # SystemValues.bottom_progress_visible이 True일 때만 표시 (gui/updater.py가 처리)

_progress_layout.addStretch()

frame_main.addWidget(frame_center_progress)


# --- 5번 검사결과표시 화면 ---
# 크롬 탭처럼 생긴 탭 두 개로 구성한다.
#   1) 백업 개요: 경로 / 변경 사항 / 유사도 등 한눈에 볼 정보
#   2) 제외 항목 선택: 백업에서 뺄 파일/폴더를 고르는 화면 (아직 빈 탭)
frame_center_result = QWidget()
_result_layout = QVBoxLayout(frame_center_result)
_result_layout.setContentsMargins(20, 14, 20, 14)
_result_layout.setSpacing(0)
# 경로 카드 높이: 14px 글자 기준 4줄 + 제목 + 여백
_PATH_CARD_HEIGHT = 104

result_tabs = QTabWidget()
result_tabs.setDocumentMode(False)
result_tabs.tabBar().setExpanding(False)
result_tabs.tabBar().setDrawBase(False)
# 선택된 탭은 아래 본문(pane)과 같은 색으로 이어 붙이고, 나머지 탭은 한 톤 어둡게 해서
# 크롬 탭처럼 "앞에 나와 있는 탭"이 구분되게 한다.
result_tabs.setStyleSheet(f"""
QTabWidget::pane {{
    background-color: {COLOR_BG};
    border: 1px solid {COLOR_BORDER};
    top: -1px;
}}
QTabBar::tab {{
    background-color: {COLOR_BORDER};
    color: {COLOR_TEXT_SUB};
    border: 1px solid {COLOR_BORDER};
    border-bottom: none;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    padding: 7px 22px;
    margin-right: 2px;
    min-width: 110px;
}}
QTabBar::tab:selected {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
    font-weight: 700;
    border-top: 2px solid {COLOR_BLUE};
}}
QTabBar::tab:!selected:hover {{
    color: {COLOR_TEXT};
}}
""")
_result_layout.addWidget(result_tabs)


def _make_result_card(title: str, wrap=False, min_height=0):
    """
    검사 결과 화면에 들어갈 카드 한 장을 만든다.
    카드 프레임과, 값을 채워 넣을 라벨을 함께 반환한다.

    wrap: 값이 길면 여러 줄로 접는다. (경로 카드용)
    min_height: 카드의 최소 높이. 경로 카드는 여러 줄이 들어갈 자리를 미리 잡아둔다.
    """
    card = QFrame()
    card.setObjectName("PanelCard")
    if min_height:
        card.setMinimumHeight(min_height)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 10, 14, 10)
    layout.setSpacing(2)

    title_label = QLabel(title)
    title_label.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SUB};")

    value_label = _PathLabel("-") if wrap else QLabel("-")
    value_label.setStyleSheet(f"font-size: 14px; color: {COLOR_TEXT}; font-weight: 600;")
    value_label.setWordWrap(wrap)
    value_label.setAlignment(Qt.AlignmentFlag.AlignTop)

    layout.addWidget(title_label)
    layout.addWidget(value_label, 1)
    return card, value_label


class _PathLabel(QLabel):
    """
    경로 표시용 라벨.
    Qt의 줄바꿈은 공백에서만 일어나서, 공백 없는 긴 경로는 카드 폭을 밀어내 버린다.
    화면에 보일 때만 경로 구분자 뒤에 폭 없는 공백(U+200B)을 넣어 그 자리에서 줄이 바뀌게 하고,
    text()는 원래 경로를 그대로 돌려준다.
    """

    def __init__(self, text=""):
        super().__init__()
        self._raw = ""
        # 내용 길이 때문에 카드 폭이 늘어나지 않게 한다. (폭은 레이아웃이 정함)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setText(text)

    def setText(self, text):
        self._raw = text
        super().setText(text.replace("\\", "\\\u200b").replace("/", "/\u200b"))

    def text(self):
        return self._raw


class SimilarityPie(QWidget):
    """
    유사도(0~100)를 원형(Pie) 차트로 그려주는 위젯.
    값이 음수이면 잴 대상이 없었다는 뜻이므로, 차트 대신 empty_text("파일 없음" 등)를 표시한다.
    """

    _TEXT_HEIGHT = 26  # 차트 아래 퍼센트 글자가 들어갈 높이

    def __init__(self, empty_text: str):
        super().__init__()
        self._empty_text = empty_text
        self._value = -1.0
        self.setMinimumSize(110, 110)

    def set_similarity(self, value: float):
        self._value = value
        self.update()  # 다시 그리기 예약

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._value < 0:
            painter.setPen(QColor(COLOR_TEXT_SUB))
            font = painter.font()
            font.setPixelSize(15)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._empty_text)
            return

        # 위젯 크기에 맞춰 가장 큰 정사각형 영역에 원을 그리고, 그 아래에 퍼센트를 쓴다.
        side = min(self.width(), self.height() - self._TEXT_HEIGHT) - 8
        x = (self.width() - side) / 2
        y = 4
        circle = QRectF(x, y, side, side)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(COLOR_BORDER))
        painter.drawEllipse(circle)

        # Qt의 각도는 1/16도 단위, 3시 방향이 0도이고 반시계가 +방향이다.
        # 12시 방향(90도)에서 시작해 시계 방향(-)으로 채운다.
        value = min(self._value, 100.0)
        painter.setBrush(QColor(COLOR_BLUE))
        if value >= 100.0:
            painter.drawEllipse(circle)
        elif value > 0:
            # 100% 미만인데 원이 꽉 차 보이면 100%로 오해하므로, 최소 1도의 빈틈은 남긴다.
            span = min(value / 100 * 360, 359) * 16
            painter.drawPie(circle, 90 * 16, int(-span))

        painter.setPen(QColor(COLOR_TEXT))
        font = painter.font()
        font.setPixelSize(16)
        font.setBold(True)
        painter.setFont(font)
        text_rect = QRectF(0, y + side, self.width(), self._TEXT_HEIGHT + 4)
        # 반올림하면 99.996%가 100.00%로 보여 "전부 일치"로 오해할 수 있으므로 소수점 둘째 자리에서 버린다.
        # (1e-9는 99.99가 99.98999...로 저장된 경우 99.98로 잘리는 것을 막기 위한 보정값)
        shown = math.floor(self._value * 100 + 1e-9) / 100
        if self._value < 100 and shown >= 100: # 보정값 때문에 100이 되는 경우까지 막는다
            shown = 99.99
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, f"{shown:.2f}%")


def _make_pie_column(name: str, empty_text: str):
    """ 유사도 카드 안에 들어갈 한 칸(이름 + 원형 차트)을 만든다. 칸 위젯과 차트 위젯을 함께 반환한다. """
    column = QWidget()
    layout = QVBoxLayout(column)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(4)

    name_label = QLabel(name)
    name_label.setStyleSheet(f"font-size: 14px; color: {COLOR_TEXT}; font-weight: 600;")
    name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    pie = SimilarityPie(empty_text)

    layout.addWidget(name_label)
    layout.addWidget(pie, 1)
    return column, pie


# --- 5-1. 백업 개요 탭 ---
frame_result_overview = QWidget()
_overview_layout = QVBoxLayout(frame_result_overview)
_overview_layout.setContentsMargins(16, 16, 16, 12)
_overview_layout.setSpacing(12)

# 원본 / 대상 경로 카드
frame_result_paths = QWidget()
_result_paths_layout = QHBoxLayout(frame_result_paths)
_result_paths_layout.setContentsMargins(0, 0, 0, 0)
_result_paths_layout.setSpacing(14)

# 경로는 생략 없이 전부 보여줘야 하므로 여러 줄이 들어갈 자리를 잡아둔다.
card_org_path, label_result_org = _make_result_card("원본 경로", wrap=True, min_height=_PATH_CARD_HEIGHT)
card_tar_path, label_result_tar = _make_result_card("대상 경로", wrap=True, min_height=_PATH_CARD_HEIGHT)
_result_paths_layout.addWidget(card_org_path, 1)
_result_paths_layout.addWidget(card_tar_path, 1)

_overview_layout.addWidget(frame_result_paths)

# 변경 사항 / 유사도(파일, 폴더) 카드
frame_result_cards = QWidget()
_result_cards_layout = QHBoxLayout(frame_result_cards)
_result_cards_layout.setContentsMargins(0, 0, 0, 0)
_result_cards_layout.setSpacing(14)

card_changes = QFrame()
card_changes.setObjectName("PanelCard")
_changes_layout = QVBoxLayout(card_changes)
_changes_layout.setContentsMargins(14, 10, 14, 10)
_changes_layout.setSpacing(8)

_changes_title = QLabel("변경 사항")
_changes_title.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SUB};")
_changes_layout.addWidget(_changes_title)

# 변경 사항 줄(라벨)들은 결과에 따라 개수가 달라지므로 이 안에 매번 새로 채운다.
frame_changes_list = QWidget()
_changes_list_layout = QVBoxLayout(frame_changes_list)
_changes_list_layout.setContentsMargins(0, 4, 0, 0)
_changes_list_layout.setSpacing(8)
_changes_layout.addWidget(frame_changes_list)
_changes_layout.addStretch()

# 파일 유사도와 폴더 유사도는 한 카드 안에 차트 두 개를 나란히 놓는다.
card_similarity = QFrame()
card_similarity.setObjectName("PanelCard")
_similarity_layout = QVBoxLayout(card_similarity)
_similarity_layout.setContentsMargins(14, 10, 14, 10)
_similarity_layout.setSpacing(6)

_similarity_title = QLabel("유사도")
_similarity_title.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SUB};")
_similarity_layout.addWidget(_similarity_title)

_pies_row = QHBoxLayout()
_pies_row.setSpacing(10)
_files_pie_column, pie_files_similarity = _make_pie_column("파일", "파일 없음")
_dirs_pie_column, pie_dirs_similarity = _make_pie_column("폴더", "폴더 없음")
_pies_row.addWidget(_files_pie_column, 1)
_pies_row.addWidget(_dirs_pie_column, 1)
_similarity_layout.addLayout(_pies_row, 1)

# 윗줄(원본/대상 경로)과 같은 1:1 비율로 나눠서 위아래 카드의 세로선이 맞도록 한다.
_result_cards_layout.addWidget(card_changes, 1)
_result_cards_layout.addWidget(card_similarity, 1)

_overview_layout.addWidget(frame_result_cards, 1)

# 하단 안내 문구 (2줄): 무엇을 하는지(흐린 글씨) / 무엇을 확인해야 하는지(기본 글씨)
label_result_expl = QLabel("원본 폴더에서 대상 경로에 백업합니다.")
label_result_expl.setStyleSheet(f"color: {COLOR_TEXT_SUB};")
label_result_expl.setWordWrap(True)

label_result_confirm = QLabel("경로와 변경사항을 확인하세요.")
label_result_confirm.setStyleSheet(f"color: {COLOR_TEXT}; font-weight: 700;")
label_result_confirm.setWordWrap(True)

_overview_layout.addWidget(label_result_expl)
_overview_layout.addWidget(label_result_confirm)

result_tabs.addTab(frame_result_overview, "백업 개요")


def update_changes_card(changes: dict):
    """
    변경 사항 카드를 채운다.
    changes: {"삭제할 파일": n, "복사할 폴더": m, ...} 형태. 개수가 0인 항목은 표시하지 않고,
    표시할 항목이 하나도 없으면 "변경 사항 없음"을 띄운다.
    """
    # 이전 검사 결과로 만든 라벨을 모두 지운다.
    while _changes_list_layout.count():
        item = _changes_list_layout.takeAt(0)
        if item.widget() is not None:
            item.widget().deleteLater()

    shown = [(name, count) for name, count in changes.items() if count > 0]
    if not shown:
        empty = QLabel("변경 사항 없음")
        empty.setStyleSheet(f"font-size: 14px; color: {COLOR_TEXT}; font-weight: 600;")
        _changes_list_layout.addWidget(empty)
        return

    for name, count in shown:
        row = QLabel(f"<span style='color:{COLOR_BLUE};'>●</span>&nbsp;&nbsp;{name}: <b>{count:,}개</b>")
        row.setStyleSheet(f"font-size: 14px; color: {COLOR_TEXT};")
        _changes_list_layout.addWidget(row)


# --- 5-2. 제외 항목 선택 탭 (추후 구현) ---
frame_result_exclude = QWidget()
result_tabs.addTab(frame_result_exclude, "제외할 파일/폴더 선택")

frame_main.addWidget(frame_center_result)

# 미리보기용 더미 데이터 (시각 확인용)
label_result_org.setText(r"C:\Users\user\Documents")
label_result_tar.setText(r"E:\Backup\Documents")
update_changes_card({"삭제할 파일": 3, "복사할 파일": 120, "복사할 폴더": 4})
pie_files_similarity.set_similarity(99.0)
pie_dirs_similarity.set_similarity(100.0)


# --- 6번 백업완료 화면 ---
# [제목 / 설명] - [검사 시간, 백업 시간 카드 | 최적화율 카드] - [최적화 안내 문구]
COLOR_FAIL = "#E5737A"  # 백업 실패 시 제목 색

frame_center_complete = QWidget()
_complete_layout = QVBoxLayout(frame_center_complete)
_complete_layout.setContentsMargins(36, 28, 36, 24)
_complete_layout.setSpacing(12)

label_complete_title = QLabel("백업이 완료되었습니다!")
label_complete_title.setStyleSheet(f"font-size: 24px; color: {COLOR_BLUE}; font-weight: 800;")


_complete_layout.addWidget(label_complete_title)
# 글씨와 카드 사이 위/아래 여백: 남는 세로 공간을 여백 20 : 카드 60 : 여백 20으로 나눈다.
_complete_layout.addStretch(20)

frame_complete_cards = QWidget()
_complete_cards_layout = QGridLayout(frame_complete_cards)
_complete_cards_layout.setContentsMargins(0, 0, 0, 0)
_complete_cards_layout.setHorizontalSpacing(14)
_complete_cards_layout.setVerticalSpacing(12)
_complete_cards_layout.setColumnStretch(0, 1)
_complete_cards_layout.setColumnStretch(1, 1)

# 왼쪽: 검사 시간 / 백업 시간 카드를 위아래로 쌓는다. 숫자가 주인공이므로 값을 크게 쓴다.
card_compare_time, label_complete = _make_result_card("검사 시간")
card_backup_time, label_complete2 = _make_result_card("백업 시간")
for _lbl in (label_complete, label_complete2):
    _lbl.setStyleSheet(f"font-size: 26px; color: {COLOR_TEXT}; font-weight: 700;")
    _lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

# 오른쪽: 최적화율 카드. 최적화율도 유사도와 같은 0~100 백분율이라 같은 원형 차트를 쓴다.
card_optimized = QFrame()
card_optimized.setObjectName("PanelCard")
_optimized_layout = QVBoxLayout(card_optimized)
_optimized_layout.setContentsMargins(14, 10, 14, 10)
_optimized_layout.setSpacing(6)

_optimized_title = QLabel("최적화율")
_optimized_title.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_SUB};")
pie_optimized = SimilarityPie("검사한 파일 없음")

_optimized_layout.addWidget(_optimized_title)
_optimized_layout.addWidget(pie_optimized, 1)

_complete_cards_layout.addWidget(card_compare_time, 0, 0)
_complete_cards_layout.addWidget(card_backup_time, 1, 0)
_complete_cards_layout.addWidget(card_optimized, 0, 1, 2, 1)  # 두 행에 걸침

_complete_layout.addWidget(frame_complete_cards, 60)
_complete_layout.addStretch(20)

label_complete3 = QLabel("최적화를 하면 다음 검사 시간을 단축시킬 수 있습니다.")
label_complete3.setWordWrap(True)
label_complete3.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter) # 화면 오른쪽에 붙임
_complete_layout.addWidget(label_complete3)

frame_main.addWidget(frame_center_complete)


def _format_seconds(seconds: float) -> str:
    """ 3.2 -> "3.2초", 75.0 -> "1분 15초" """
    if seconds < 60:
        return f"{seconds:.1f}초"
    minutes, sec = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}분 {sec}초"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}시간 {minutes}분"


def update_complete_screen(success: bool, compare_run_time: float, backup_run_time: float,
                           optimized_percent: float):
    """ 백업 완료 화면을 채운다. 백업에 실패한 파일이 있으면 제목을 실패용으로 바꾼다. """
    if success:
        label_complete_title.setText("백업이 완료되었습니다!")
        label_complete_title.setStyleSheet(f"font-size: 24px; color: {COLOR_BLUE}; font-weight: 800;")
    else:
        label_complete_title.setText("백업에 문제가 있습니다")
        label_complete_title.setStyleSheet(f"font-size: 24px; color: {COLOR_FAIL}; font-weight: 800;")

    label_complete.setText(_format_seconds(compare_run_time))
    label_complete2.setText(_format_seconds(backup_run_time))
    pie_optimized.set_similarity(optimized_percent)

    if optimized_percent >= 100:
        label_complete3.setText("모든 파일이 최적화되어 있습니다.")
    else:
        label_complete3.setText("최적화를 하면 다음 검사 시간을 단축시킬 수 있습니다.")


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
    frame_center_home, frame_center_select, frame_center_items,
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
