from tkinter import*
from tkinter import ttk 
from PIL import Image, ImageTk

root = Tk() 
root.title("Home_Layout")
root.geometry("900x600+220+40") #가로1060, 세로 700 x값 220, y값 40

# 사용할 이미지 모음
# 1. 원본 이미지 로드 (PIL Image)
raw_label_home_img = Image.open(r"image\main_home.jpg")
raw_btn_org_img = Image.open(r"image\folder_origin (1).png")
raw_btn_tar_img = Image.open(r"image\target_folder.jpg")
raw_btn_home = Image.open(r"image\btn_home_new.jpg")
raw_btn_search = Image.open(r"image\btn_search.png")

# 2. 이미지 리사이즈 (PIL Image resized)
res_label_home_img = raw_label_home_img.resize((900, 600), Image.LANCZOS)
res_btn_org_img = raw_btn_org_img.resize((250, 250), Image.LANCZOS)
res_btn_tar_img = raw_btn_tar_img.resize((250, 250), Image.LANCZOS)
res_btn_home = raw_btn_home.resize((70, 70), Image.LANCZOS)
res_btn_search = raw_btn_search.resize((70, 70), Image.LANCZOS)

# 3. 실질적으로 사용하는 GUI 이미지 변환 (ImageTk.PhotoImage)
tk_label_home_img = ImageTk.PhotoImage(res_label_home_img)
tk_btn_org_img = ImageTk.PhotoImage(res_btn_org_img)
tk_btn_tar_img = ImageTk.PhotoImage(res_btn_tar_img)
tk_Img_btn_home = ImageTk.PhotoImage(res_btn_home)
tk_Img_btn_search = ImageTk.PhotoImage(res_btn_search)


#ui구성

#왼쪽바와 중앙 화면을 포함하는 메인 프레임
frame_main = Frame(root, bg="white")
frame_main.pack(side = "top",fill="both", expand="true")
frame_main.pack_propagate(0) 

#왼쪽 단계 표시 바
frame_LeftBar = Frame(frame_main, relief="solid",  width="2c", bg="white")
frame_LeftBar.pack(side = "left",fill="both")
frame_LeftBar.pack_propagate(0)
label_step_img = Label(frame_LeftBar, image=tk_Img_btn_home)
label_step_img.pack(pady="1", padx="0.2c")
label_step_img2 = Label(frame_LeftBar, image=tk_Img_btn_search)
label_step_img2.pack()
label_step_img3 = Label(frame_LeftBar, text= "단계3", height="3")
label_step_img3.pack()
label_step_img4 = Label(frame_LeftBar, text= "단계4", height="3")
label_step_img4.pack()

#중앙 화면 -> 앞으로 계속 불러올 화면

#1번 홈 화면

frame_center_home = Frame(frame_main, bg="black", relief="solid") #중앙 화면 프레임대신 레이블로 로고 넣기
lable_home_img = Label(frame_center_home,image=tk_label_home_img, bd="0")
lable_home_img.pack(expand=True)
frame_center_home.pack(fill="both", expand = True)

#2번 폴더선택 화면
#원본폴더 선택

frame_center_select = Frame(frame_main, relief="solid", bd="1", bg="white")
frame_org_part = Frame(frame_center_select, relief="solid", bd=1) 
frame_org_part.pack(side="left", fill="both", expand = True)

label_original = Label(frame_org_part, text="원본폴더")
label_original.pack(pady= (80,10))
btn_sel_org = Button(frame_org_part, text="백업폴더",image=tk_btn_org_img)
btn_sel_org.pack()



#중앙 화살표 위치
frame_mid_part = Frame(frame_center_select, width="0.5c", relief="solid", bd=1, bg="white") 
frame_mid_part.pack(side = "left", fill="both", expand = "false")
frame_mid_part.pack_propagate(0)

#백업폴더 선택
frame_tar_part = Frame(frame_center_select, relief="solid", bd=1, bg="white") 
frame_tar_part.pack(side="left", fill="both", expand = "true")

label_target = Label(frame_tar_part, text="백업폴더")
label_target.pack(pady= (80,10))

btn_sel_target = Button(frame_tar_part, text="백업폴더", image=tk_btn_tar_img)
btn_sel_target.pack()
#ui구성후 프레임 구성하는 선 지우기 relief값 bd값 삭제
#-------------------------------------------------------------------------------2번콘티

#3번 검사선택

frame_center_check = Frame(frame_main, relief="solid", bd="1")

#좌측 빠른검사 프레임
frame_fast_check = Frame(frame_center_check, relief="solid", bd="1")
frame_fast_check.pack(side = "left", fill="both", expand="true")
frame_fast_check.pack_propagate(0) 


label_fast_check = Label(frame_fast_check, text="빠른검사")
label_fast_check.pack(pady=(30, 10))

label_fast_expl = Label(frame_fast_check, text="파일의 메타데이터를 기반으로\n빠른 검사를 진행합니다.")
label_fast_expl.pack()

btn_fast_sel = Button(frame_fast_check, text="선택")
btn_fast_sel.pack()

#우측 정밀검사 프레임
fram_detail = Frame(frame_center_check,  relief="solid", bd="1")
fram_detail.pack(side = "right",  fill="both", expand="true")
fram_detail.pack_propagate(0) 

label_det_check = Label(fram_detail, text="정밀검사")
label_det_check.pack(pady=(30, 10))

label_det_expl = Label(fram_detail, text="파일을 바이트 단위로 정밀 검사합니다.\n시간이 오래 걸릴수 있습니다.")
label_det_expl.pack()

btn_det_sel = Button(fram_detail, text="선택")
btn_det_sel.pack()

#4번 프로그레스바
frame_center_progress = Frame(frame_main, relief="solid", bd="1")

frame_top_progress = Frame(frame_center_progress, relief="solid")
frame_top_progress.pack(fill="x",)

label_top_progress = Label(frame_top_progress, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_top_progress.pack(side="left")

label_top_progress2 = Label(frame_top_progress, text = "이곳엔 진행시간 00 : 00 표시")
label_top_progress2.pack(side="right")

top_progressbar = ttk.Progressbar(frame_center_progress, maximum = 100, mode = "indeterminate" )
top_progressbar.pack(fill="x", padx="5")

label_top_progress3 = Label(frame_center_progress, text = "이곳엔 파일의 경로를 표시")
label_top_progress3.pack(side="top", anchor="w")

frame_bottom_progress = Frame(frame_center_progress, relief="solid")
frame_bottom_progress.pack(fill="x",)

label_bottom_progress = Label(frame_bottom_progress, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_bottom_progress.pack(side="left")

label_bottom_progress2 = Label(frame_bottom_progress, text = "이곳엔 진행시간 00 : 00 표시")
label_bottom_progress2.pack(side="right")

bottom_progressbar = ttk.Progressbar(frame_center_progress, maximum = 100, mode = "indeterminate" )
bottom_progressbar.pack(fill="x", padx="5")

label_bottom_progress3 = Label(frame_center_progress, text = "이곳엔 파일의 경로를 표시")
label_bottom_progress3.pack(side="top", anchor="w")

#5번 검사결과표시

#5번 메인프레임 
frame_center_result = Frame(frame_main, relief="solid", bd="1")

# 5  탑 프레임(삭제,복사,갱신 버튼)
frame_btn_result = Frame(frame_center_result, relief="solid", bd="1")
frame_btn_result.pack(side="top", pady="15")
btn_result_delete = Button(frame_btn_result, text="삭제")
btn_result_delete.pack(side="left")
btn_result_copy = Button(frame_btn_result, text="복사")
btn_result_copy.pack(side="left")
btn_result_refresh = Button(frame_btn_result, text="갱신")
btn_result_refresh.pack(side="left")

# 5 삭제 프레임 
frame_mid_del_result = Frame(frame_center_result, relief="solid", bd="1")
Label(frame_mid_del_result, text="삭제할 파일").pack()
mid_del_scroll = Scrollbar(frame_mid_del_result)
mid_del_scroll.pack(side="right", fill="y")
mid_del_list = Listbox(frame_mid_del_result, selectmode="single", height=10, width="50", yscrollcommand=mid_del_scroll.set)
mid_del_list.pack(side="left", fill="x", pady="5")
mid_del_scroll.config(command=mid_del_list.yview)

frame_bot_del_result = Frame(frame_center_result, relief="solid", bd="1")
Label(frame_bot_del_result, text="삭제 관련 하단 목록").pack()
bot_del_scroll = Scrollbar(frame_bot_del_result)
bot_del_scroll.pack(side="right", fill="y")
bot_del_list = Listbox(frame_bot_del_result, selectmode="single", width="50", height=10, yscrollcommand=bot_del_scroll.set)
bot_del_list.pack(side="left", fill="x")
bot_del_scroll.config(command=bot_del_list.yview)

# 5 복사 프레임 
frame_mid_copy_result = Frame(frame_center_result, relief="solid", bd="1")
Label(frame_mid_copy_result, text="복사할 파일").pack()
mid_copy_scroll = Scrollbar(frame_mid_copy_result)
mid_copy_scroll.pack(side="right", fill="y")
mid_copy_list = Listbox(frame_mid_copy_result, selectmode="single", height=10, width="50", yscrollcommand=mid_copy_scroll.set)
mid_copy_list.pack(side="left", fill="x", pady="5")
mid_copy_scroll.config(command=mid_copy_list.yview)

frame_bot_copy_result = Frame(frame_center_result, relief="solid", bd="1")
Label(frame_bot_copy_result, text="복사 관련 하단 목록").pack()
bot_copy_scroll = Scrollbar(frame_bot_copy_result)
bot_copy_scroll.pack(side="right", fill="y")
bot_copy_list = Listbox(frame_bot_copy_result, selectmode="single", width="50", height=10, yscrollcommand=bot_copy_scroll.set)
bot_copy_list.pack(side="left", fill="x")
bot_copy_scroll.config(command=bot_copy_list.yview)

# 5 갱신 프레임 
frame_mid_renew_result = Frame(frame_center_result, relief="solid", bd="1")
Label(frame_mid_renew_result, text="갱신할 파일").pack()
mid_renew_scroll = Scrollbar(frame_mid_renew_result)
mid_renew_scroll.pack(side="right", fill="y")
mid_renew_list = Listbox(frame_mid_renew_result, selectmode="single", height=10, width="50", yscrollcommand=mid_renew_scroll.set)
mid_renew_list.pack(side="left", fill="x", pady="5")
mid_renew_scroll.config(command=mid_renew_list.yview)

frame_bot_renew_result = Frame(frame_center_result, relief="solid", bd="1")
Label(frame_bot_renew_result, text="갱신 관련 하단 목록").pack()
bot_renew_scroll = Scrollbar(frame_bot_renew_result)
bot_renew_scroll.pack(side="right", fill="y")
bot_renew_list = Listbox(frame_bot_renew_result, selectmode="single", width="50", height=10, yscrollcommand=bot_renew_scroll.set)
bot_renew_list.pack(side="left", fill="x")
bot_renew_scroll.config(command=bot_renew_list.yview)

# 5 리스트박스 데이터
for i in range(50):
    mid_del_list.insert(END, f"삭제 중앙 {i+1}")
    bot_del_list.insert(END, f"삭제 하단 {i+1}")
    mid_copy_list.insert(END, f"복사 중앙 {i+1}")
    bot_copy_list.insert(END, f"복사 하단 {i+1}")
    mid_renew_list.insert(END, f"갱신 중앙 {i+1}")
    bot_renew_list.insert(END, f"갱신 하단 {i+1}")



# 백업확인알림창

#6번 백업화면&프로그레스바
fram_center_backup = Frame(frame_main, relief="solid", bd="1")

fram_backup_contain = Frame(fram_center_backup, relief="solid")
fram_backup_contain.pack(fill="x",)

label_backup = Label(fram_backup_contain, text = "백업이 진행됩니다")
label_backup.pack()

label_backup_progress = Label(fram_backup_contain, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_backup_progress.pack(side="left")

label_backup2 = Label(fram_backup_contain, text = "이곳엔 진행시간 00 : 00 표시")
label_backup2.pack(side="right")

backup_progressbar = ttk.Progressbar(fram_center_backup, maximum = 100, mode = "indeterminate" )
backup_progressbar.pack(fill="x", padx="5")

label_backup3 = Label(fram_center_backup, text = "이곳엔 파일의 경로를 표시")
label_backup3.pack(side="top", anchor="w")


#6-1 이후 바로 재검사 실시

frame_center_recheck = Frame(frame_main, relief="solid", bd="1")

fram_recheck_contain = Frame(frame_center_recheck, relief="solid")
fram_recheck_contain.pack(fill="x",)

label_recheck = Label(fram_recheck_contain, text = "재검사 중입니다")
label_recheck.pack()

label_label_recheck = Label(fram_recheck_contain, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_label_recheck.pack(side="left")

label_recheck2 = Label(fram_recheck_contain, text = "이곳엔 진행시간 00 : 00 표시")
label_recheck2.pack(side="right")

recheck_progressbar = ttk.Progressbar(frame_center_recheck, maximum = 100, mode = "indeterminate" )
recheck_progressbar.pack(fill="x", padx="5")

label_recheck3 = Label(frame_center_recheck, text = "이곳엔 파일의 경로를 표시")
label_recheck3.pack(side="top", anchor="w")

#8-1 최적화 진행
fram_center_optimize = Frame(frame_main, relief="solid", bd="1")

fram_optimize_contain = Frame(fram_center_optimize, relief="solid")
fram_optimize_contain.pack(fill="x",)

label_optimize = Label(fram_optimize_contain, text = "이곳엔 파일의 전체 진행도가 000/000로 표시")
label_optimize.pack(side="left")

label_optimize2 = Label(fram_optimize_contain, text = "이곳엔 진행시간 00 : 00 표시")
label_optimize2.pack(side="right")

optimize_progressbar = ttk.Progressbar(fram_center_optimize, maximum = 100, mode = "indeterminate" )
optimize_progressbar.pack(fill="x", padx="5")

label_optimize3 = Label(fram_center_optimize, text = "이곳엔 파일의 경로를 표시")
label_optimize3.pack(side="top", anchor="w")


#7번 백업완료
fram_center_complete = Frame(frame_main, relief="solid", bd="1")

#7번 탑 프레임(삭제,복사,갱신 버튼)
frame_btn_complete = Frame(fram_center_complete, relief="solid", bd="1")
frame_btn_complete.pack(side="top", pady="15")

btn_comp_del = Button(frame_btn_complete, text="삭제")
btn_comp_del.pack(side="left")
btn_comp_copy = Button(frame_btn_complete, text="복사")
btn_comp_copy.pack(side="left")
btn_comp_renew = Button(frame_btn_complete, text="갱신")
btn_comp_renew.pack(side="left") 

#7번 중앙 프레임
frame_mid_complete = Frame(fram_center_complete, relief="solid", bd="1")
frame_mid_complete.pack(side="top", pady="5")

#7번 중앙 리스트박스
label_complete = Label(frame_mid_complete, text = "결과내용1")
label_complete2 = Label(frame_mid_complete, text = "결과내용2")
label_complete3 = Label(frame_mid_complete, text = "결과내용3")
label_complete4 = Label(frame_mid_complete, text = "결과내용4")

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

# 프레임 변경 배열
frames = [
    frame_center_home, frame_center_select, frame_center_check, 
    frame_center_progress, frame_center_result, fram_center_backup, 
    frame_center_recheck, fram_center_optimize, fram_center_complete
]
labels = [label_step_img, label_step_img2, label_step_img3, label_step_img4]

current_index = 0
