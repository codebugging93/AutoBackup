import os

from system.constants import APPNAME
from galaxy.widgets import *

def decorate_layout():
    # configs 
    _cnf_bg_black = dict(bg="black")
    _cnf_highlight = dict(
        highlightbackground="white",
        highlightcolor="white", 
        highlightthickness=1,
    )

    # config for label
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

    _cnf_btn = dict(
        **_cnf_bg_black, 
        **_cnf_highlight,
        width=4,
        height=2,
        fg="white",
        font=("monospace", 9),
        )


    # root
    root.title(APPNAME)
    root.config(**_cnf_bg_black)
    root.geometry("1280x600")

    label_progress_main.config(**_cnf_label, anchor="w")
    label_progress_sub.config(**_cnf_label, anchor="w")

    # frame_log
    frame_log.config(**_cnf_bg_black, **_cnf_highlight)
    if os.name == "nt":
        _size = 16
    else:
        _size = 10 
    text_log.config(
        width=1,
        height=20,
        fg="white",
        bg="black",
        highlightthickness=0,
        state="disabled",
        font=("monospace", _size),
        )
    
    entry_ans_with_frame.frame.config(
        **_cnf_bg_black, 
        **_cnf_highlight,
        ) 
    entry_ans_with_frame.entry.config(
        disabledbackground="black",
        disabledforeground="white",
        insertbackground="white",
        fg="white",
        bg="black",
        font=("monospace", 10),
        state="disabled",
        bd=0,
        )

    btn_start.config(text="시작", **_cnf_btn)



def expand_layout():
    label_progress_main.pack(fill='x')
    label_progress_sub.pack(fill='x')
    frame_log.pack(fill='x')
    scroll_log.pack(side='right', fill='y')
    text_log.pack(fill='both', side="left", expand=True)
    entry_ans_with_frame.pack_custom(fill='x')
    btn_start.pack(expand=True)

    root.mainloop()

