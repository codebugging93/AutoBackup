""" main_for_android에서는 이 모듈의 init 함수로 프로그램을 시작해야 한다. """

from threading import Thread
from galaxy.binding import bind_progress
from galaxy.execute import execute_task
from galaxy.layout import decorate_layout, expand_layout
from galaxy.widgets import btn_start


def init():
    bind_progress()
    btn_start.config(command=Thread(target=execute_task).start)

    decorate_layout()
    expand_layout()