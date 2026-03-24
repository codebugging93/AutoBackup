import tkinter as tk
import os
from gui.custom_widgets import *
from system.constants import APPNAME


######################################
# 위젯 정의
######################################


# program settings
root = tk.Tk()
frame_main = tk.Frame(root)

# frame_button
frame_button = tk.Frame(frame_main)
btn_newtask = tk.Button(frame_button)
btn_compare = tk.Button(frame_button)
btn_single = tk.Button(frame_button)
# btn_exfat = tk.Button(frame_button)
btn_macro = tk.Button(frame_button)
buttons = btn_newtask, btn_compare, btn_single, btn_macro

# frame_status
frame_status = tk.Frame(frame_main)
label_progress_main = tk.Label(frame_status)
label_progress_sub = tk.Label(frame_status)
"""frame_log = tk.Frame(frame_status)"""
entry_ans = tk.Entry(frame_status)
entries = entry_ans, 

# frame_log (frame_status 안에 있음)
frame_log = tk.Frame(frame_status)
text_log = tk.Text(frame_log)
scroll_log = VerticalScrollbar(frame_log, text_log)

# frame_right 갱신/복사/삭제할 파일
frame_right = tk.Frame(root) 
llbox_file_renew = LabelListboxWithFrame(frame_right, "갱신할 파일") 
llbox_file_rmv = LabelListboxWithFrame(frame_right, "삭제할 파일") 
llbox_file_copy = LabelListboxWithFrame(frame_right, "복사할 파일") 

# left에는 복사/삭제할 폴더
frame_left = tk.Frame(root) 
llbox_folder_rmv = LabelListboxWithFrame(frame_left, "삭제할 폴더") 
llbox_folder_copy = LabelListboxWithFrame(frame_left, "복사할 폴더")
llboxes = (
    llbox_file_renew,
    llbox_file_rmv,
    llbox_file_copy,
    llbox_folder_rmv,
    llbox_folder_copy,
)



######################################
# 위젯 모양 설정
######################################

# 공통으로 공유할 설정
_cnf_bg_black = dict(bg="black")
_cnf_highlight = dict(
    highlightbackground="white",
    highlightcolor="white", 
    highlightthickness=1,
)

# 공통 레이블 설정
if os.name == "nt":
    _size = 10
else:
    _size = 8
_cnf_label = dict(
    **_cnf_highlight,
    bg="black",
    fg="white",
    font=("monospace", _size)
)


# root 설정
root.title(APPNAME)
root.config(**_cnf_bg_black, **_cnf_highlight)
root.geometry("1280x600")

# frame_main 설정
frame_main.config(**_cnf_bg_black)

# frame_button 설정
if os.name == "nt":
    w, h = 13, 7
else:
    w, h = 8, 4
_cnf_btn = dict( 
    **_cnf_bg_black, 
    **_cnf_highlight,
    width=w,
    height=h,
    fg="white",
    font=("monospace", 9),
    )

frame_button.config(**_cnf_bg_black, **_cnf_highlight)
btn_newtask.config(text="새 작업", **_cnf_btn)
btn_compare.config(text="비교", **_cnf_btn)
btn_single.config(text="싱글 백업", **_cnf_btn)
btn_macro.config(text="매크로", **_cnf_btn)

# frame_status 설정
frame_status.config(**_cnf_bg_black, **_cnf_highlight)
label_progress_main.config(**_cnf_label, anchor="w")
label_progress_sub.config(**_cnf_label)
entry_ans.config(
    disabledbackground="black",
    disabledforeground="white",
    insertbackground="white",
    state="normal",
    **_cnf_label,
    )

# frame_log 
frame_log.config(**_cnf_bg_black, **_cnf_highlight)

if os.name == "nt":
    _size = 16
else:
    _size = 10 
text_log.config(
    highlightthickness=0,
    bg="black",
    fg="white",
    font=("monospace", _size),
    width=1,
    height=1,
    state="disabled",
    )

# 하단 프레임 리스트박스 설정
frame_right.config(**_cnf_bg_black)
frame_left.config(**_cnf_bg_black)
_iteration = (
    llbox_file_renew,
    llbox_file_rmv,
    llbox_file_copy,
    llbox_folder_rmv,
    llbox_folder_copy,
)
for i in _iteration:
    i.listbox.config(
        **_cnf_highlight,
        width=1,
        height=1,
        bg="black",
        fg="white",
        font=("monospace", 10),
    )
    i.label.config(**_cnf_label)
    i.frame.config(**_cnf_bg_black)


######################################
# 위젯 배치
######################################



frame_main.pack(side='top', fill='x')
    
# frame_button
frame_button.pack(side='left', anchor='n')
for i in buttons:
    i.pack()

# frame_status
frame_status.pack(side='right', fill='both', expand=True)
label_progress_main.pack(fill='x')
label_progress_sub.pack(fill='x')
entry_ans.pack(side="bottom", fill='x')

# frame_log
frame_log.pack(fill='both', expand=True)
scroll_log.pack(side='right', fill='y')
text_log.pack(side='left', fill='both', expand=True)

# left & right
frame_left.pack_propagate(False)
frame_right.pack_propagate(False)
frame_left.pack(side="left", fill="both", expand=True)
frame_right.pack(side="right", fill="both", expand=True)
llbox_folder_rmv.pack(fill="both", expand=True)
llbox_folder_copy.pack(fill="both", expand=True)
llbox_file_renew.pack(fill="both", expand=True)
llbox_file_rmv.pack(fill="both", expand=True)
llbox_file_copy.pack(fill="both", expand=True)

