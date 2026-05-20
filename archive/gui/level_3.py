"""
제 3페이즈;백업한 후에, 대답 함수등을 관리한다.
# 대답, 후검사 수행, 후최적화 등
"""

from threading import Thread

from implemented.main_datas import backup_data, aftercheck_data

from gui.backup import backup_boost, backup_all
from gui.widgets import text_log, entry_ans
from gui.handle_widgets import lock_widget, unlock_widget, lock_buttons, unlock_buttons, lock_ui, unlock_ui
from gui.answer import answer_frame
from gui.messages import *
from gui.implemented_tasks import aftercheck, listbox_update


"""
aftercheck를 y/n할 때 상황: ui가 모두 열려있음
rebackup을 y/n할 때 상황: 엔트리만 열려있음
console를 y/n할 때 상황: ui가 모두 열려있음

예상도
aftercheck - rebackup - console

console에서 /recheck 실행 시 aftercheck로 돌아감
"""


# aftercheck 대답 준비
def ready_aftercheck_answer():
    text_log.print()
    text_log.print(msg_aftercheck_ans)
    entry_ans.bind_cmd(answer_aftercheck)
    unlock_ui()


# aftercheck 엔트리 바인딩 용도
def answer_aftercheck():
    _answers = ("y", "n")
    answer_frame(_command_aftercheck_answer, _answers)


def _command_aftercheck_answer(ans):
    if ans == "y": # aftercheck 실행
        lock_ui()
        Thread(target=aftercheck_run).start()
    elif ans == "n": # afterboost 준비
        ready_console_answer()


def aftercheck_run():
    """ 
    접미사 _run은 aftercheck 작업 후에 UI에 여러 정보를 표시하고
    다음 순서의 함수로 넘어가는 등의 표면적인 동작을 의미한다.
    """
    aftercheck()
    
    listbox_update(aftercheck_data)

    # 표시
    msg_list = []
    msg_list.append(("파일 복사", len(aftercheck_data.set_file_copy)))
    msg_list.append(("파일 삭제", len(aftercheck_data.set_file_rmv)))
    msg_list.append(("파일 갱신", len(aftercheck_data.set_file_renew)))
    msg_list.append(("폴더 복사", aftercheck_data.tree_copy.num))
    msg_list.append(("폴더 삭제", aftercheck_data.tree_rmv.num))

    need_re_backup = False # 재백업 여부를 결정함
    text_log.print() # 일단 실패 여부와 상관없이 행갈이
    for action, num in msg_list:
        if num != 0:
            text_log.print(f"{action} 실패 : {num}개")
            need_re_backup = True

    # 분기점
    if need_re_backup: 
        ready_re_backup_answer() # 재백업
    else: 
        text_log.print("재검사를 완료했으며, 이상은 없습니다.")
        ready_console_answer() # 콘솔로
    

# 재백업 준비 
def ready_re_backup_answer(): 
    text_log.print() # 실패 목록을 띄웠으므로 행갈이
    text_log.print(msg_rebackup_ans)
    
    entry_ans.bind_cmd(answer_re_backup)
    lock_ui()
    unlock_widget(entry_ans.entry)


def answer_re_backup():
    _answers = ("y", "n")
    answer_frame(_command_re_backup, _answers)
    

def _command_re_backup(ans): 
    if ans == "y": 
        lock_ui()
        Thread(target=re_backup).start() # 후백업 실행
    elif ans == "n": 
        ready_console_answer() # 콘솔로 


def re_backup(): 
    """ 재검사 후 잘못된 것들을 바로잡는 백업, 하지만 스킵도 가능하다. """
    backup_all(aftercheck_data, is_aftercheck=True)
    # 이 작업이 끝나면 바로 콘솔로 넘어간다.
    ready_console_answer()


# 명령어 준비
def ready_console_answer():
    text_log.print()
    text_log.print(msg_console)
    entry_ans.bind_cmd(answer_console)
    unlock_ui()

_RECHECK = "/recheck"
_BOOST = "/boost"
def answer_console():
    _answers = (_RECHECK, _BOOST)
    answer_frame(_command_console_answer, _answers)


def _command_console_answer(ans):
    if ans == _RECHECK:  # 후검사 실행
        _command_aftercheck_answer("y")
    elif ans == _BOOST: # 후최적화 실행
        lock_ui()
        Thread(target=afterboost).start()



def afterboost():
    backup_boost(backup_data)
    text_log.print()
    text_log.print(msg_boost_end) 

    ready_console_answer() # afterboost는 콘솔로 다시 돌아감


