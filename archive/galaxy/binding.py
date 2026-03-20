"""
bind_progress를 import해서 꼭 위젯과 함수를 바인딩하자
"""


from implemented.main_datas import main_prog, sub_prog 
from galaxy.widgets import label_progress_main, label_progress_sub


def bind_progress():
    main_prog.bind_writing(_write_main, _clear_main)
    sub_prog.bind_writing(_write_sub, _clear_sub)
    

_write_main = lambda string: label_progress_main.config(text=string)
_clear_main = lambda: _write_main("")

_write_sub = lambda string: label_progress_sub.config(text=string)
_clear_sub = lambda: _write_sub("")

