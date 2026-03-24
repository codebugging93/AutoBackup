"""
제 2페이즈;검사후의 동작들을 수행한다.
대답, 백업 등의 작업을 실행할 수 있다.
"""
from threading import Thread

from implemented.main_datas import backup_data, configs
from system.constants import BACKUP_MODES, CMP_MODES

from gui.answer import answer_frame
from gui.widgets import entry_ans, text_log
from gui.messages import *
from gui.backup import backup_all, backup_file, backup_boost
from gui.handle_widgets import unlock_widget, unlock_buttons, lock_buttons, lock_ui, unlock_ui
from gui.level_3 import ready_aftercheck_answer


_able_commands = [] # 선택지 제외용 리스트


# 1차대답 준비
def ready_backup_answer(): 
    # 선택지 제외 과정
    _able_commands.clear()
    info_string = "입력창에 원하는 모드를 입력해주세요."
    if backup_data.is_able_to_backup_file():
        info_string += "\nfile: 파일만 백업"
        _able_commands.append("file") 
    if backup_data.is_able_to_backup_all():
        info_string += "\nall: 파일과 폴더 모두 백업"
        _able_commands.append("all")
    if backup_data.is_able_boost():
        info_string += "\nboost: 백업 최적화 (검사속도 향상)"
        _able_commands.append("boost")    
    
    # 출력
    text_log.print() # 행갈이
    if len(_able_commands) == 0:
        text_log.print("작업할 파일이 하나도 없습니다.")
        lock_ui()
        unlock_buttons()
        return None
    text_log.print(info_string)

    # 바인딩
    entry_ans.bind_cmd(answer_backup)
    unlock_ui()


# 1차 대답; 모드 결정
def answer_backup():
    answer_frame(_command_backup, _able_commands)


def _command_backup(ans):
    if ans == "file":
        configs.backup_mode = BACKUP_MODES.FILE
    elif ans == "all":
        configs.backup_mode = BACKUP_MODES.ALL
    elif ans == "boost":
        configs.backup_mode = BACKUP_MODES.BOOST
    else:
        raise ValueError("wrong backup mode: " + str(configs.backup_mode))

    ready_backup_re_answer(ans)


# 2차 대답 준비
def ready_backup_re_answer(ans): 
    text_log.print() # 행갈이
    text_log.print(ans + " 작업을 시작합니까?")
    text_log.print("(시작은 y, 다시 선택은 c 입력)")

    entry_ans.bind_cmd(answer_backup_re_answer)
    lock_ui()
    unlock_widget(entry_ans.entry)


def answer_backup_re_answer():
    _answers = ("y", "c")
    answer_frame(_command_backup_re_answer, _answers)


def _command_backup_re_answer(ans):
    # 정상
    if ans == "y": # 바로 아래의 execute로 넘어감
        lock_ui()
        Thread(target=execute).start()
    elif ans == "c": # 1차 질문으로 돌아감
        ready_backup_answer()


def execute():
    # 백업 실행
    text_log.print()
    if configs.backup_mode == BACKUP_MODES.ALL:
        backup_all(backup_data)
    elif configs.backup_mode == BACKUP_MODES.FILE:
        backup_file(backup_data)
    elif configs.backup_mode == BACKUP_MODES.BOOST:
        backup_boost(backup_data)
        ready_backup_answer()  # 1차 질문으로 돌아감
        return None
    else:
        raise Exception("wrong backup mode : " + configs.backup_mode)

    # level 3으로 이동
    ready_aftercheck_answer()

