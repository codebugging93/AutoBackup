from tkinter import*
from tkinter import ttk 
from PIL import Image, ImageTk

root = Tk() 
root.title("Home_Layout")
root.geometry("900x600+220+40") #가로1060, 세로 700 x값 220, y값 40

#사용할 이미지 모음
# 1. 원본 이미지 로드 (PIL Image)
raw_Logo = Image.open(r"image\main_home.jpg")
raw_original_folder = Image.open(r"image\folder_origin (1).png")
raw_target_folder = Image.open(r"히오스 사이즈 300 250.png")
raw_btn_home = Image.open(r"image\btn_home_new.jpg")
raw_btn_search = Image.open(r"image\btn_search.png")

# 2. 이미지 리사이즈 (PIL Image resized)
res_Logo = raw_Logo.resize((900, 600), Image.LANCZOS)
res_origin_folder = raw_original_folder.resize((250, 250), Image.LANCZOS)
res_backup_folder = raw_target_folder.resize((250, 250), Image.LANCZOS)
res_btn_home = raw_btn_home.resize((70, 70), Image.LANCZOS)
res_btn_search = raw_btn_search.resize((70, 70), Image.LANCZOS)

# 3. 실질적으로 사용하는 GUI 이미지 변환 (ImageTk.PhotoImage)
tk_logo = ImageTk.PhotoImage(res_Logo)
tk_origin_folder = ImageTk.PhotoImage(res_origin_folder)
tk_backup_folder = ImageTk.PhotoImage(res_backup_folder)
tk_Img_btn_home = ImageTk.PhotoImage(res_btn_home)
tk_Img_btn_search = ImageTk.PhotoImage(res_btn_search)

#왼쪽바와 중앙 화면을 포함하는 프레임
frame_top = Frame(root, bg="white")
frame_top.pack(side = "top",fill="both", expand="true")
frame_top.pack_propagate(0) 
#왼쪽 기능 바
fram_LeftBar = Frame(frame_top, relief="solid",  width="2c", bg="white")
fram_LeftBar.pack(side = "left",fill="both")
fram_LeftBar.pack_propagate(0)
label_step1 = Label(fram_LeftBar, image=tk_Img_btn_home)
label_step1.pack(pady="1", padx="0.2c")
label_step2 = Label(fram_LeftBar, image=tk_Img_btn_search)
label_step2.pack()
label_step3 = Label(fram_LeftBar, text= "단계3", height="3")
label_step3.pack()
label_step3 = Label(fram_LeftBar, text= "단계4", height="3")
label_step3.pack()

#중앙 화면 -> 앞으로 계속 불러올 화면
#중앙 화면 이미지 리사이즈

#1번 홈 화면


fram_center_first = Frame(frame_top, bg="black", relief="solid") #중앙 화면 프레임대신 레이블로 로고 넣기
label_1 = Label(fram_center_first,image=tk_logo, bd="0")

label_1.pack(expand=True)

fram_center_first.pack(fill="both", expand = True)


#2번 폴더선택
#원본폴더 선택

fram_center_second = Frame(frame_top, relief="solid", bd="1", bg="white")


fram_leftpart = Frame(fram_center_second, relief="solid", bd=1) 
fram_leftpart.pack(side="left", fill="both", expand = True)

label_original = Label(fram_leftpart, text="원본폴더")
label_original.pack(pady= (80,10))
btn_sel_original = Button(fram_leftpart, text="백업폴더",image=tk_origin_folder)
btn_sel_original.pack()
label_original = Label(fram_leftpart, text="")


#중앙 화살표 위치
fram_centerpart = Frame(fram_center_second, width="0.5c", relief="solid", bd=1, bg="white") 
fram_centerpart.pack(side = "left", fill="both", expand = "false")
fram_centerpart.pack_propagate(0)

#백업폴더 선택
fram_rightpart = Frame(fram_center_second, relief="solid", bd=1, bg="white") 
fram_rightpart.pack(side="left", fill="both", expand = "true")

label_target = Label(fram_rightpart, text="백업폴더")
label_target.pack(pady= (80,10))

btn_sel_backup = Button(fram_rightpart, text="백업폴더", image=tk_backup_folder)
btn_sel_backup.pack()
#ui구성후 프레임 구성하는 선 지우기 relief값 bd값 삭제
#-------------------------------------------------------------------------------2번콘티

#3번 검사선택

fram_center_third = Frame(frame_top, relief="solid", bd="1")

#좌측 빠른검사 프레임
fram_left = Frame(fram_center_third, relief="solid", bd="1")
fram_left.pack(side = "left", fill="both", expand="true")
fram_left.pack_propagate(0) 


label_fast = Label(fram_left, text="빠른검사")
label_fast.pack(pady=(30, 10))

label_sim_expl = Label(fram_left, text="파일의 메타데이터를 기반으로\n빠른 검사를 진행합니다.")
label_sim_expl.pack()

btn_fast_sel = Button(fram_left, text="선택")
btn_fast_sel.pack()

#우측 정밀검사 프레임
fram_right = Frame(fram_center_third,  relief="solid", bd="1")
fram_right.pack(side = "right",  fill="both", expand="true")
fram_right.pack_propagate(0) 

label_fast = Label(fram_right, text="정밀검사")
label_fast.pack(pady=(30, 10))

label_det_expl = Label(fram_right, text="파일을 바이트 단위로 정밀 검사합니다.\n시간이 오래 걸릴수 있습니다.")
label_det_expl.pack()

btn_detail_sel = Button(fram_right, text="선택")
btn_detail_sel.pack()

#4번 프로그레스바
fram_center_fourth = Frame(frame_top, relief="solid", bd="1")

fram_top_contain = Frame(fram_center_fourth, relief="solid")
fram_top_contain.pack(fill="x",)

label_top_progress1 = Label(fram_top_contain, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_top_progress1.pack(side="left")

label_top_progress2 = Label(fram_top_contain, text = "이곳엔 진행시간 00 : 00 표시")
label_top_progress2.pack(side="right")

top_progressbar = ttk.Progressbar(fram_center_fourth, maximum = 100, mode = "indeterminate" )
top_progressbar.pack(fill="x", padx="5")

label_top_progress3 = Label(fram_center_fourth, text = "이곳엔 파일의 경로를 표시")
label_top_progress3.pack(side="top", anchor="w")



fram_bottom_contain = Frame(fram_center_fourth, relief="solid")
fram_bottom_contain.pack(fill="x",)

label_bottom_progress1 = Label(fram_bottom_contain, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_bottom_progress1.pack(side="left")

label_bottom_progress2 = Label(fram_bottom_contain, text = "이곳엔 진행시간 00 : 00 표시")
label_bottom_progress2.pack(side="right")

bottom_progressbar = ttk.Progressbar(fram_center_fourth, maximum = 100, mode = "indeterminate" )
bottom_progressbar.pack(fill="x", padx="5")

label_bottom_progress3 = Label(fram_center_fourth, text = "이곳엔 파일의 경로를 표시")
label_bottom_progress3.pack(side="top", anchor="w")

#progressbar.setvar(value="50")


# progressbar.start(5)





#5번 검사결과표시

#5번 메인프레임 
fram_center_fifth = Frame(frame_top, relief="solid", bd="1")
#fram_center_fifth.pack(fill="both")



#5번 탑 프레임(삭제,복사,갱신 버튼)


#5번 중앙 프레임

#5번 삭제 프레임
fram_del_middle_result = Frame(fram_center_fifth, relief="solid", bd="1")

#5번 중앙 리스트박스
del_middle_scrollbar = Scrollbar(fram_del_middle_result)
del_middle_scrollbar.pack(side="right", fill="y")

del_middle_result_list = Listbox(fram_del_middle_result, selectmode="single", height = 10, width="50", yscrollcommand=del_middle_scrollbar.set)
del_middle_result_list.pack(side="left", fill="x", pady="5")

del_middle_scrollbar.config(command=del_middle_result_list.yview)

#5번 하단 프레임
fram_del_bottom_result = Frame(fram_center_fifth, relief="solid", bd="1")
del_bottom_scrollbar = Scrollbar(fram_del_bottom_result)
del_bottom_scrollbar.pack(side="right", fill="y")

del_bottom_result_list = Listbox(fram_del_bottom_result, selectmode="single", width="50", height = 10, yscrollcommand=del_bottom_scrollbar.set)
del_bottom_result_list.pack(side="left", fill="x")

del_bottom_scrollbar.config(command=del_bottom_result_list.yview)

for i in range(50):
    del_middle_result_list.insert(END, f"test500000000 {i+1}")

for i in range(50):
    del_bottom_result_list.insert(END, f"test511111111 {i+1}")


#5번 복사 프레임
fram_copy_middle_result = Frame(fram_center_fifth, relief="solid", bd="1")


#5번 중앙 리스트박스
err_label = Label(fram_center_fifth, text="내용 아직 미정")
err_label.pack()


# 5  탑 프레임(삭제,복사,갱신 버튼)
fram_second_top_result = Frame(fram_center_fifth, relief="solid", bd="1")
fram_second_top_result.pack(side="top", pady="15")

second_btn_delete = Button(fram_second_top_result, command=lambda: show_second_result_frame("delete"), text="삭제")
second_btn_delete.pack(side="left")
second_btn_copy = Button(fram_second_top_result, command=lambda: show_second_result_frame("copy"), text="복사")
second_btn_copy.pack(side="left")
second_btn_refresh = Button(fram_second_top_result, command=lambda: show_second_result_frame("renew"), text="갱신")
second_btn_refresh.pack(side="left")

# 5 삭제 프레임 
fram_62_del_middle_result = Frame(fram_center_fifth, relief="solid", bd="1")
Label(fram_62_del_middle_result, text="삭제할 파일").pack()
del_62_mid_scroll = Scrollbar(fram_62_del_middle_result)
del_62_mid_scroll.pack(side="right", fill="y")
del_62_mid_list = Listbox(fram_62_del_middle_result, selectmode="single", height=10, width="50", yscrollcommand=del_62_mid_scroll.set)
del_62_mid_list.pack(side="left", fill="x", pady="5")
del_62_mid_scroll.config(command=del_62_mid_list.yview)

fram_62_del_bottom_result = Frame(fram_center_fifth, relief="solid", bd="1")
Label(fram_62_del_bottom_result, text="삭제 관련 하단 목록").pack()
del_62_bot_scroll = Scrollbar(fram_62_del_bottom_result)
del_62_bot_scroll.pack(side="right", fill="y")
del_62_bot_list = Listbox(fram_62_del_bottom_result, selectmode="single", width="50", height=10, yscrollcommand=del_62_bot_scroll.set)
del_62_bot_list.pack(side="left", fill="x")
del_62_bot_scroll.config(command=del_62_bot_list.yview)

# 5 복사 프레임 
fram_62_copy_middle_result = Frame(fram_center_fifth, relief="solid", bd="1")
Label(fram_62_copy_middle_result, text="복사할 파일").pack()
copy_62_mid_scroll = Scrollbar(fram_62_copy_middle_result)
copy_62_mid_scroll.pack(side="right", fill="y")
copy_62_mid_list = Listbox(fram_62_copy_middle_result, selectmode="single", height=10, width="50", yscrollcommand=copy_62_mid_scroll.set)
copy_62_mid_list.pack(side="left", fill="x", pady="5")
copy_62_mid_scroll.config(command=copy_62_mid_list.yview)

fram_62_copy_bottom_result = Frame(fram_center_fifth, relief="solid", bd="1")
Label(fram_62_copy_bottom_result, text="복사 관련 하단 목록").pack()
copy_62_bot_scroll = Scrollbar(fram_62_copy_bottom_result)
copy_62_bot_scroll.pack(side="right", fill="y")
copy_62_bot_list = Listbox(fram_62_copy_bottom_result, selectmode="single", width="50", height=10, yscrollcommand=copy_62_bot_scroll.set)
copy_62_bot_list.pack(side="left", fill="x")
copy_62_bot_scroll.config(command=copy_62_bot_list.yview)

# 5 갱신 프레임 
fram_62_renew_middle_result = Frame(fram_center_fifth, relief="solid", bd="1")
Label(fram_62_renew_middle_result, text="갱신할 파일").pack()
renew_62_mid_scroll = Scrollbar(fram_62_renew_middle_result)
renew_62_mid_scroll.pack(side="right", fill="y")
renew_62_mid_list = Listbox(fram_62_renew_middle_result, selectmode="single", height=10, width="50", yscrollcommand=renew_62_mid_scroll.set)
renew_62_mid_list.pack(side="left", fill="x", pady="5")
renew_62_mid_scroll.config(command=renew_62_mid_list.yview)

fram_62_renew_bottom_result = Frame(fram_center_fifth, relief="solid", bd="1")
Label(fram_62_renew_bottom_result, text="갱신 관련 하단 목록").pack()
renew_62_bot_scroll = Scrollbar(fram_62_renew_bottom_result)
renew_62_bot_scroll.pack(side="right", fill="y")
renew_62_bot_list = Listbox(fram_62_renew_bottom_result, selectmode="single", width="50", height=10, yscrollcommand=renew_62_bot_scroll.set)
renew_62_bot_list.pack(side="left", fill="x")
renew_62_bot_scroll.config(command=renew_62_bot_list.yview)

# 5 리스트박스 데이터
for i in range(50):
    del_62_mid_list.insert(END, f"6-2 삭제 중앙 {i+1}")
    del_62_bot_list.insert(END, f"6-2 삭제 하단 {i+1}")
    copy_62_mid_list.insert(END, f"6-2 복사 중앙 {i+1}")
    copy_62_bot_list.insert(END, f"6-2 복사 하단 {i+1}")
    renew_62_mid_list.insert(END, f"6-2 갱신 중앙 {i+1}")
    renew_62_bot_list.insert(END, f"6-2 갱신 하단 {i+1}")



# 백업확인알림창

#6번 백업화면&프로그레스바
fram_center_sixth = Frame(frame_top, relief="solid", bd="1")

fram_main_contain = Frame(fram_center_sixth, relief="solid")
fram_main_contain.pack(fill="x",)

label_main = Label(fram_main_contain, text = "백업이 진행됩니다")
label_main.pack()

label_main_progress1 = Label(fram_main_contain, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_main_progress1.pack(side="left")

label_main_progress2 = Label(fram_main_contain, text = "이곳엔 진행시간 00 : 00 표시")
label_main_progress2.pack(side="right")

main_progressbar = ttk.Progressbar(fram_center_sixth, maximum = 100, mode = "indeterminate" )
main_progressbar.pack(fill="x", padx="5")

label_main_progress3 = Label(fram_center_sixth, text = "이곳엔 파일의 경로를 표시")
label_main_progress3.pack(side="top", anchor="w")


#6-1 이후 바로 재검사 실시

fram_center_sixth_first = Frame(frame_top, relief="solid", bd="1")

fram_second_main_contain = Frame(fram_center_sixth_first, relief="solid")
fram_second_main_contain.pack(fill="x",)

label_main_second = Label(fram_second_main_contain, text = "재검사 중입니다")
label_main_second.pack()

label_main_second_progress1 = Label(fram_second_main_contain, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_main_second_progress1.pack(side="left")

label_main_second_progress2 = Label(fram_second_main_contain, text = "이곳엔 진행시간 00 : 00 표시")
label_main_second_progress2.pack(side="right")

main_second_progressbar = ttk.Progressbar(fram_center_sixth_first, maximum = 100, mode = "indeterminate" )
main_second_progressbar.pack(fill="x", padx="5")

label_main_second_progress3 = Label(fram_center_sixth_first, text = "이곳엔 파일의 경로를 표시")
label_main_second_progress3.pack(side="top", anchor="w")



#6-2 재검사 오류 표시  - 5번과 같이

#6-2메인 프레임

#8-1
fram_center_eighth_first = Frame(frame_top, relief="solid", bd="1")

fram_second_top_contain = Frame(fram_center_eighth_first, relief="solid")
fram_second_top_contain.pack(fill="x",)

label_second_top_progress1 = Label(fram_second_top_contain, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_second_top_progress1.pack(side="left")

label_second_top_progress2 = Label(fram_second_top_contain, text = "이곳엔 진행시간 00 : 00 표시")
label_second_top_progress2.pack(side="right")

top_second_progressbar = ttk.Progressbar(fram_center_eighth_first, maximum = 100, mode = "indeterminate" )
top_second_progressbar.pack(fill="x", padx="5")

label_second_top_progress3 = Label(fram_center_eighth_first, text = "이곳엔 파일의 경로를 표시")
label_second_top_progress3.pack(side="top", anchor="w")

fram_center_seventh = Frame(frame_top, relief="solid", bd="1")

#7번 탑 프레임(삭제,복사,갱신 버튼)
fram_third_top_result = Frame(fram_center_seventh, relief="solid", bd="1")
fram_third_top_result.pack(side="top", pady="15")

third_btn_delete = Button(fram_third_top_result, text="삭제")
third_btn_delete.pack(side="left")
third_btn_copy = Button(fram_third_top_result, text="복사")
third_btn_copy.pack(side="left")
third_btn_refresh = Button(fram_third_top_result, text="갱신")
third_btn_refresh.pack(side="left") 

#7번 중앙 프레임
fram_third_middle_result = Frame(fram_center_seventh, relief="solid", bd="1")
fram_third_middle_result.pack(side="top", pady="5")

#7번 중앙 리스트박스
third_scrollbar = Scrollbar(fram_third_middle_result)
third_scrollbar.pack(side="right", fill="y")

third_middle_result_list = Listbox(fram_third_middle_result, selectmode="single", height = 10, width="50", yscrollcommand=third_scrollbar.set)
third_middle_result_list.pack(side="left", fill="x", pady="5")

third_scrollbar.config(command=third_middle_result_list.yview)

for i in range(50):
    third_middle_result_list.insert(END, f"test00000000 {i+1}")

#-------------------------------------------------------------------------------------

#하단 바
fram_bottombar = Frame(root,relief ="solid",bg="white", height = "1.5c")
fram_bottombar.pack(side="bottom",fill="both")
fram_bottombar.pack_propagate(0)

btn_Previous = Button(fram_bottombar,fg="gray", text= "이전", width="15", relief="solid", bd="1")
btn_Previous.pack(side="left", fill="y")
btn_begin = Button(fram_bottombar, text= "시작",  width="15", relief="solid", bd="1")
btn_begin.pack(side="right",fill="y")

root.resizable(False,False) #전체 화면 가로,세로 사이즈 조절x 


#프레임 변경 배열로 
frames = [fram_center_first, fram_center_second, fram_center_third, fram_center_fourth, fram_center_fifth, fram_center_sixth, fram_center_sixth_first, fram_center_eighth_first, fram_center_seventh]
labels = [label_step1, label_step2, label_step3]



current_index = 0

def update_ui():
    global current_index
    # 인덱스가 범위를 벗어나지 않도록 강제 제한 (IndexError 방지)
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
            # 현재 단계보다 이전 단계들은 회색 처리
            pass 
        elif i == current_index:
            # 현재 진행 중인 단계는 강조색 (흰색 또는 원래 색)
            label.config(bg="white")
        else:
            # 아직 도달하지 않은 단계는 기본 배경색 (시스템 기본색)
            label.config(bg="white")

# 6-1 프레임에서 "이상이 있음" 조건에 따라 이동할 프레임을 결정하는 함수
def handle_6_1_frame_navigation():
    # 나중에 실제 시스템과 연동할 때 이 변수에 실제 검사 결과를 대입하면 됩니다.
    이상이_있음 = True  # 현재는 테스트를 위해 True로 설정

    if 이상이_있음:
        return frames.index(fram_center_fifth)  # 5번 프레임(검사결과)으로 이동
    else:
        return frames.index(fram_center_eighth_first)  # 8-1번 프레임(최적화)으로 이동

def move_next():
    global current_index
    
    # 6-1 프레임(재검사 중)에서 다음으로 넘어갈 때의 특수 로직
    if current_index == frames.index(fram_center_sixth_first):
        current_index = handle_6_1_frame_navigation()
    elif current_index == 8:  # 마지막 7번 프레임에서 점프 로직 (기존 유지)
        current_index = 4
    elif current_index < len(frames) - 1:
        current_index = current_index + 1

    update_ui()

def move_prev():
    global current_index
    if current_index > 0:
        current_index = current_index - 1
        update_ui()    

btn_begin.config(command=move_next)
btn_Previous.config(command=move_prev)

# 초기 UI 상태 업데이트
update_ui()








# 5번 프레임 초기화면 삭제


def show_second_result_frame(frame_type):
    # 6-2 프레임 숨기기
    fram_62_del_middle_result.pack_forget()
    fram_62_del_bottom_result.pack_forget()
    
    fram_62_copy_middle_result.pack_forget()
    fram_62_copy_bottom_result.pack_forget()
    
    fram_62_renew_middle_result.pack_forget()
    fram_62_renew_bottom_result.pack_forget()

    if frame_type == "delete":
        fram_62_del_middle_result.pack(side="top", pady="5")
        fram_62_del_bottom_result.pack(side="top", pady="5")
    elif frame_type == "copy":
        fram_62_copy_middle_result.pack(side="top", pady="5")
        fram_62_copy_bottom_result.pack(side="top", pady="5")
    elif frame_type == "renew":
        fram_62_renew_middle_result.pack(side="top", pady="5")
        fram_62_renew_bottom_result.pack(side="top", pady="5")

# 6-2번 프레임 초기 화면 설정
show_second_result_frame("delete")

