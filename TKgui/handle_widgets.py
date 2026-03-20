from TKgui.widgets import buttons, entries


def lock_ui():
    """ 모든 엔트리와 버튼을 잠금 """
    lock_entries()
    lock_buttons()


def unlock_ui():
    """ 모든 엔트리와 버튼을 잠금 해제 """
    unlock_entries()
    unlock_buttons()


def lock_buttons():
    for i in buttons:
        lock_widget(i)


def unlock_buttons():
    for i in buttons:
        unlock_widget(i)


def lock_entries():
    for i in entries:
        lock_widget(i)


def unlock_entries():
    for i in entries:
        unlock_widget(i)


def lock_widget(widget) -> None:
    widget.configure(state="disabled")


def unlock_widget(widget) -> None: 
    widget.configure(state="normal")