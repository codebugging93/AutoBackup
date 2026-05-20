from gui.widgets import entry_ans, text_log
from gui.messages import msg_wrong_ans


def answer_frame(cmd, correct_answers):
    """
    대답받고 실행하는 프레임
    """
    ans = entry_ans.entry.get()
    entry_ans.clear()

    # 대답 걸러내기
    ans = ans.strip()
    if ans == "":
        return None
    elif ans not in correct_answers:
        text_log.print(msg_wrong_ans) 
        return None

    # 처리
    cmd(ans)



    
def answer_frame_base(cmd):
    """
    대답받고 실행하는 프레임
    """
    ans = entry_ans.entry.get()
    entry_ans.clear()

    # 처리
    cmd(ans)

"""
대답함수의 본보기
문장을 출력하는 함수가 실행되기 직전에 \n을 추가하는 것이 제일 좋다.

# 재검사 대답 받을 준비 
def ready_aftercheck_answer(): # D
    text_log.write(msg_aftercheck_ans)
    entry_ans.bind_cmd(answer_aftercheck)
    ui_unlock()


# 재검사 대답
def answer_aftercheck(): # D
    answer_frame(command_aftercheck_answer)


def command_aftercheck_answer(ans):
    ans = ans.strip()

    if ans == "y": # 재검사 실행
        text_log.write()
        ui_lock()
        Thread(target=aftercheck).start()

    elif ans == "n": # 후최적화
        text_log.write()
        ready_afterboost_answer()

    elif ans != "":
        text_log.write(msg_wrong_ans)
"""
