from gui.handle_widgets import lock_widget, unlock_widget
from gui.messages import msg_wrong_ans
from galaxy.widgets import text_log, entry_ans_with_frame
from implemented.main_datas import configs 
from utils.constants import BACKUP_MODES
from time import sleep


"""
def _ask_yes_no():
    outputer = widgets.text_log.write
    
    entry_ans = widgets.entry_ans
    def send_answer():
        v = entry_ans.get()
        if len(v) != 0:
            entry_list.append(v)
            entry_ans.clear()
    entry_ans.bind_cmd(send_answer)
    
    # 엔트리에 "y"가 입력될때까지 기다림
    outputer("y or n")
    entry_ans.unlock()
    correct = 'y', 'n'
    while True:
        # y, n인 경우 해야 하는 것 
        # 공백 출력, 엔트리 잠그기, 리턴하기, 엔트리 리스트 비우기
        sleep(1 / 60)
        if len(entry_list) == 0:
            continue
        
        i = entry_list[0]
        entry_list.clear()
        if i not in correct:
            outputer("잘못 입력하셨습니다.")
            continue
        
        outputer()
        entry_ans.lock()
        if i == "y":
            return True
        elif i == "n":
            return False
        else:
            raise Exception("y or n 오타")
            """
def answer_frame(correct_answers_iterable):
    """correct_answers_iterable 내의 올바른 대답을 유도함"""

    outputer = text_log.print
    correct_answers = correct_answers_iterable
    answers: list[str] = []

    def send_answer():
        v = entry_ans_with_frame.entry.get()
        answers.append(v)
        entry_ans_with_frame.clear()

    entry_ans_with_frame.bind_cmd(send_answer)
    unlock_widget(entry_ans_with_frame.entry)
    while True:
        sleep(1 / 60)
        if len(answers) == 0:
            continue 
        
        ans = answers[0]
        answers.clear() # 이중 입력 방지 정책   
        ans = ans.strip()   

        if ans == "":
            continue
        elif ans not in correct_answers:
            outputer(msg_wrong_ans) 
            continue

        return ans


def get_answer_for_backup():
    outputer = text_log.print
    outputer("\n백업을 시작하시겠습니까? (y/n)")

    ans = answer_frame(tuple("y", "n"))
    if ans == "y":
        return True 
    elif ans == "n":
        return False 
    else:
        outputer("잘못된 ans 값 제공됨:", ans)
        outputer("프로그램을 중단합니다.")
        raise ValueError(ans)
    
# 아래 함수는 위 함수의 복제판임

def get_answer_for_boost():
    outputer = text_log.print
    outputer("\n최적화을 시작하시겠습니까? (y/n)")

    ans = answer_frame(tuple("y", "n"))
    if ans == "y":
        return True 
    elif ans == "n":
        return False 
    else:
        outputer("잘못된 ans 값 제공됨:", ans)
        outputer("프로그램을 중단합니다.")
        raise ValueError(ans)
    
