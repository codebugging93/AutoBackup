from gui.components import *



current_index = 0

def update_ui():
    global current_index
    # 인덱스가 범위를 벗어나지 않도록 강제 제한
    current_index = max(0, min(current_index, len(frames) - 1))

    for frame in frames:
        frame.pack_forget()
    frames[current_index].pack(expand=True, fill="both")

    # 이전 버튼 상태 제어
    if current_index == 0:
        btn_Previous.config(state="disabled")
    else:
        btn_Previous.config(state="normal")

    # 다음,시작 버튼 상태 및 텍스트 제어
    if current_index == len(frames) - 1:
        btn_begin.config(state="disabled", text="완료")
    else:
        btn_begin.config(state="normal", text="다음" if current_index > 0 else "시작")

    for i, label in enumerate(labels):
        if i < current_index:
            pass 
        elif i == current_index:
            label.config(bg="white")
        else:
            label.config(bg="white")

def handle_6_1_frame_navigation():
    # 검사 결과 연동 변수 (테스트용)
    이상이_있음 = True

    if 이상이_있음:
        return frames.index(frame_center_result)
    else:
        return frames.index(fram_center_optimize)

def move_next():
    global current_index
    
    if current_index == frames.index(frame_center_recheck):
        current_index = handle_6_1_frame_navigation()
    elif current_index == len(frames) - 1:
        current_index = 4
    elif current_index < len(frames) - 1:
        current_index += 1

    update_ui()

def move_prev():
    global current_index
    if current_index > 0:
        current_index -= 1
        update_ui()    



def show_second_result_frame(frame_type):
    # 6-2 프레임 숨기기
    frame_mid_del_result.pack_forget()
    frame_bot_del_result.pack_forget()
    
    frame_mid_copy_result.pack_forget()
    frame_bot_copy_result.pack_forget()
    
    frame_mid_renew_result.pack_forget()
    frame_bot_renew_result.pack_forget()

    if frame_type == "delete":
        frame_mid_del_result.pack(side="top", pady="5")
        frame_bot_del_result.pack(side="top", pady="5")
    elif frame_type == "copy":
        frame_mid_copy_result.pack(side="top", pady="5")
        frame_bot_copy_result.pack(side="top", pady="5")
    elif frame_type == "renew":
        frame_mid_renew_result.pack(side="top", pady="5")
        frame_bot_renew_result.pack(side="top", pady="5")

# 초기 UI 상태 업데이트
update_ui()
show_second_result_frame("delete")






btn_result_delete.config(command=lambda: show_second_result_frame("delete"))

btn_result_copy.config(command=lambda: show_second_result_frame("copy")) 

btn_result_refresh.config(command=lambda: show_second_result_frame("renew"))

btn_begin.config(command=move_next)
btn_Previous.config(command=move_prev)