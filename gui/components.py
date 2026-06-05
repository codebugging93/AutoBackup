from tkinter import*
from tkinter import ttk 
from PIL import Image, ImageTk

root = Tk() 
root.title("Home_Layout")
root.geometry("900x600+220+40") #가로1060, 세로 700 x값 220, y값 40

C = {"bg":          "#F0F2F7"}

# 사용할 이미지 모음
# 1. 원본 이미지 로드 (PIL Image)
raw_label_home_img = Image.open(r"image\main_home.jpg")
raw_btn_org_img = Image.open(r"image\folder_origin (1).png")
raw_btn_tar_img = Image.open(r"image\대상폴더.png")
raw_btn_home = Image.open(r"image\btn_home_new.jpg")
raw_btn_search = Image.open(r"image\btn_search.png")

#단계표시용 이미지 원본

step_home_img = Image.open(r"image\btn_home.jpg") # 임시로 이걸로 해놓음
step_select_img = Image.open(r"image\step-2.png")  
step_progress_img = Image.open(r"image\step-3.png")
step_result_img = Image.open(r"image\step-4.png")
step_backup_img = Image.open(r"image\step-5.png")
step_complete_img = Image.open(r"image\step-6.png")

step_home_img_inverted = Image.open(r"image\btn_home.jpg") # 임시로 이걸로 해놓음
step_select_img_inverted = Image.open(r"image\step2.png")  
step_progress_img_inverted = Image.open(r"image\step3.png")
step_result_img_inverted = Image.open(r"image\step4.png")
step_backup_img_inverted = Image.open(r"image\step5.png")
step_complete_img_inverted = Image.open(r"image\step6.png")



# 2. 이미지 리사이즈 (PIL Image resized)
res_label_home_img = raw_label_home_img.resize((900, 600), Image.LANCZOS)
res_btn_org_img = raw_btn_org_img.resize((250, 250), Image.LANCZOS)
res_btn_tar_img = raw_btn_tar_img.resize((250, 250), Image.LANCZOS)
res_btn_home = raw_btn_home.resize((70, 70), Image.LANCZOS)
res_btn_search = raw_btn_search.resize((70, 70), Image.LANCZOS)

# 단계표시용 이미지 리사이즈
res_step_home_img = step_home_img.resize((70,70), Image.LANCZOS) 
res_step_select_img = step_select_img.resize((70,70), Image.LANCZOS) 
res_step_progress_img = step_progress_img.resize((70,70), Image.LANCZOS) 
res_step_result_img = step_result_img.resize((70,70), Image.LANCZOS) 
res_step_backup_img = step_backup_img.resize((70,70), Image.LANCZOS)
res_step_complete_img = step_complete_img.resize((70,70), Image.LANCZOS)

res_step_home_img_inverted = step_home_img_inverted.resize((70,70), Image.LANCZOS)
res_step_select_img_inverted = step_select_img_inverted.resize((70,70), Image.LANCZOS)
res_step_progress_img_inverted = step_progress_img_inverted.resize((70,70), Image.LANCZOS)
res_step_result_img_inverted = step_result_img_inverted.resize((70,70), Image.LANCZOS)
res_step_backup_img_inverted = step_backup_img_inverted.resize((70,70), Image.LANCZOS)
res_step_complete_img_inverted = step_complete_img_inverted.resize((70,70), Image.LANCZOS)


# 3. 실질적으로 사용하는 GUI 이미지 변환 (ImageTk.PhotoImage)
tk_label_home_img = ImageTk.PhotoImage(res_label_home_img)
tk_btn_org_img = ImageTk.PhotoImage(res_btn_org_img)
tk_btn_tar_img = ImageTk.PhotoImage(res_btn_tar_img)
tk_Img_step_home = ImageTk.PhotoImage(res_btn_home)
tk_Img_btn_search = ImageTk.PhotoImage(res_btn_search)


# 단계표시용 이미지 실사용

# 현재 단계가 아닐시 배경이 하얀색 이미지 사용
tk_step_home_img = ImageTk.PhotoImage(res_step_home_img)
tk_step_select_img = ImageTk.PhotoImage(res_step_select_img)
tk_step_progress_img = ImageTk.PhotoImage(res_step_progress_img)
tk_step_result_img = ImageTk.PhotoImage(res_step_result_img)
tk_step_backup_img = ImageTk.PhotoImage(res_step_backup_img)
tk_step_complete_img = ImageTk.PhotoImage(res_step_complete_img)

# _inverted 붙은거는 파랑 배경이미지 -> 현재 단계의 이미지에 사용
tk_step_home_img_inverted = ImageTk.PhotoImage(res_step_home_img_inverted)
tk_step_select_img_inverted = ImageTk.PhotoImage(res_step_select_img_inverted)
tk_step_progress_img_inverted = ImageTk.PhotoImage(res_step_progress_img_inverted)
tk_step_result_img_inverted = ImageTk.PhotoImage(res_step_result_img_inverted)
tk_step_backup_img_inverted = ImageTk.PhotoImage(res_step_backup_img_inverted)
tk_step_complete_img_inverted = ImageTk.PhotoImage(res_step_complete_img_inverted)



# 스이세이블루는 상수로 정의됨(system/constants/SUISEI_BLUE)
#ui구성



#왼쪽 단계 표시 바
frame_LeftBar = Frame(root, relief="solid",  width="2c", bg="#f0f2f7", highlightbackground="#cdd2e0", highlightthickness=1)
frame_LeftBar.pack(side = "left",fill="y")
frame_LeftBar.pack_propagate(0)
label_step_img = Label(frame_LeftBar, text = "test")
label_step_img.pack(pady="1", padx="0.2c")
label_step_img2 = Label(frame_LeftBar, image = tk_step_select_img)
label_step_img2.pack()
label_step_img3 = Label(frame_LeftBar, image = tk_step_progress_img)
label_step_img3.pack()
label_step_img4 = Label(frame_LeftBar, image = tk_step_result_img)
label_step_img4.pack()
label_step_img5 = Label(frame_LeftBar, image = tk_step_backup_img)
label_step_img5.pack()
label_step_img6 = Label(frame_LeftBar, image = tk_step_complete_img)
label_step_img6.pack()

#중앙 화면 메인 프레임
frame_main = Frame(root, bg="#f0f2f7", highlightbackground="#cdd2e0", highlightthickness=1)
frame_main.pack(side = "top",fill="both", expand="true")
frame_main.pack_propagate(0) 


#1번 홈 화면

frame_center_home = Frame(frame_main, relief="solid") #중앙 화면 프레임대신 레이블로 로고 넣기
#lable_home_img = Label(frame_center_home,image=tk_label_home_img, bd="0")
#lable_home_img.pack(expand=True)
frame_center_home.pack(fill="both", expand = True)

#2번 폴더선택 화면
#원본폴더 선택

frame_center_select = Frame(frame_main, relief="solid")
frame_org_part = Frame(frame_center_select, relief="solid", bg="#f0f2f7") 
frame_org_part.pack(side="left", fill="both", expand = True)

label_original = Label(frame_org_part, text="원본폴더", bg="#f0f2f7")
label_original.pack(pady= (80,10))
btn_sel_org = Button(frame_org_part, text="백업폴더",image=tk_btn_org_img)
btn_sel_org.pack()

label_org_path = Label(frame_org_part, text="원본폴더의 주소경로가 들어갈위치길이 테스트 시공의폭풍은 언제나 최고야 지금즉시 가입시 무료똥말 증정 매주 무료 영웅 20종 꾸준한 밸런스 패치", wraplength=250, justify="center", bg="#f0f2f7")
label_org_path.pack(pady = (40,10))


#중앙 화살표 위치
frame_mid_part = Frame(frame_center_select, width="0.5c", relief="solid", bg="#f0f2f7") 
frame_mid_part.pack(side = "left", fill="both", expand = "false")
frame_mid_part.pack_propagate(0)

#백업폴더 선택
frame_tar_part = Frame(frame_center_select, relief="solid", bg="#f0f2f7") 
frame_tar_part.pack(side="left", fill="both", expand = "true")

label_target = Label(frame_tar_part, text="백업폴더",bg="#f0f2f7")
label_target.pack(pady= (80,10))

btn_sel_target = Button(frame_tar_part, text="백업폴더", image=tk_btn_tar_img)
btn_sel_target.pack()


label_tar_path = Label(frame_tar_part, text="백업폴더의 주소경로가 들어갈위치", bg="#f0f2f7")
label_tar_path.pack(pady= (40,10))



#3번 검사선택

frame_center_check = Frame(frame_main, relief="solid")

#좌측 빠른검사 프레임
frame_fast_check = Frame(frame_center_check, relief="solid", bg="#f0f2f7")
frame_fast_check.pack(side = "left", fill="both", expand="true")
frame_fast_check.pack_propagate(0) 


label_fast_check = Label(frame_fast_check, text="빠른검사", bg="#f0f2f7")
label_fast_check.pack(pady=(30, 10))

label_fast_expl = Label(frame_fast_check, text="파일의 메타데이터를 기반으로\n빠른 검사를 진행합니다.", bg="#f0f2f7")
label_fast_expl.pack()

btn_fast_sel = Button(frame_fast_check, text="선택")
btn_fast_sel.pack()

#우측 정밀검사 프레임
fram_detail = Frame(frame_center_check,  relief="solid", bg="#f0f2f7")
fram_detail.pack(side = "right",  fill="both", expand="true")
fram_detail.pack_propagate(0) 

label_det_check = Label(fram_detail, text="정밀검사", bg="#f0f2f7")
label_det_check.pack(pady=(30, 10))

label_det_expl = Label(fram_detail, text="파일을 바이트 단위로 정밀 검사합니다.\n시간이 오래 걸릴수 있습니다.", bg="#f0f2f7")
label_det_expl.pack()

btn_det_sel = Button(fram_detail, text="선택")
btn_det_sel.pack()

#4번 프로그레스바
frame_center_progress = Frame(frame_main, relief="solid", bd="1")

# 부모속성의 값을 불러오지 못하는 프레임
frame_top_progress = Frame(frame_center_progress, relief="solid")
frame_top_progress.pack(fill="x",)

# 상위 레이블 2개를 담을 프레임을 따로 제작하였음
frame_top_progress_label = Frame(frame_top_progress, bg="#f0f2f7")
frame_top_progress_label.pack(fill="x", )

label_top_progress = Label(frame_top_progress_label, text = "이곳엔 파일의 전체 진행도가 000/000로 표시", bg="#f0f2f7")
label_top_progress.pack(side="left")

label_top_progress2 = Label(frame_top_progress_label, text = "이곳엔 진행시간 00 : 00 표시", bg="#f0f2f7")
label_top_progress2.pack(side="right")

# 이 프로그레스바는 frame_top_progress 소속
long_path = r'"C:\Users\kls77\AppData\Local\Programs\Python\Python314\python.exe "c:/Users/kls77/Desktop/AutoBackup_WIP 260529 0/main.sssssssssspy"'
top_progressbar = ttk.Progressbar(frame_top_progress, maximum = 100, mode = "determinate" )
top_progressbar.pack(fill="x", padx="5")

label_top_progress3 = Label(frame_top_progress, text=(lambda p: p if len(p) <= 100 else p[:50] + "..." + p[-50:])(long_path), bg="#f0f2f7", wraplength=700, justify="left")
label_top_progress3.pack(side="top", anchor="w")


""" top_progressbar = ttk.Progressbar(frame_top_progress, maximum = 100, mode = "determinate" )
top_progressbar.pack(fill="x", padx="5")

label_top_progress3 = Label(frame_top_progress, text = "이곳엔 파일의 경로를 표시", bg="#f0f2f7", wraplength=450, justify="left")
label_top_progress3.pack(side="top", anchor="w") """

frame_bottom_progress = Frame(frame_center_progress, relief="solid", bg="#f0f2f7")
# frame_bottom_progress.pack(fill="x",)

# 상위 레이블 2개를 담을 프레임을 따로 제작하였음
frame_bottom_progress_label = Frame(frame_bottom_progress, bg="#f0f2f7")
frame_bottom_progress_label.pack(fill="x", )

label_bottom_progress = Label(frame_bottom_progress_label, text = "이곳엔 파일의 전체 진행도가 000/000로 표시", bg="#f0f2f7")
label_bottom_progress.pack(side="left")

bottom_progressbar = ttk.Progressbar(frame_bottom_progress, maximum = 100, mode = "determinate" )
bottom_progressbar.pack(fill="x", padx="5")

label_bottom_progress3 = Label(frame_bottom_progress, text = "이곳엔 파일의 경로를 표시", bg="#f0f2f7",wraplength=500, justify="left")
label_bottom_progress3.pack(side="top", anchor="w")

#5번 검사결과표시

#5번 메인프레임 
frame_center_result = Frame(frame_main, relief="solid", bd="1")

# 1:2 비율 설정을 위한 그리드 가중치 설정 (0번 행: 상단, 1번 행: 리스트)
frame_center_result.grid_rowconfigure(0, weight=1)
frame_center_result.grid_rowconfigure(1, weight=2)
frame_center_result.grid_columnconfigure(0, weight=1)

# 상단 구성 요소들을 묶을 프레임 (비율 1 영역)
frame_result_header = Frame(frame_center_result, bg="#f0f2f7")
frame_result_header.grid(row=0, column=0, sticky="nsew")

# 5  탑 프레임(삭제,복사,갱신 버튼)
frame_btn_result = Frame(frame_result_header, relief="solid", bd="1", bg="#f0f2f7")
frame_btn_result.pack(side="top", fill='x', pady=5)
btn_result_delete = Button(frame_btn_result, text="삭제할 파일(n)")
btn_result_delete.pack(side="left")
btn_result_delete2 = Button(frame_btn_result, text="삭제할 파일(n)")
btn_result_delete2.pack(side="left")
btn_result_copy = Button(frame_btn_result, text="복사할 파일(n)")
btn_result_copy.pack(side="left")
btn_result_copy2 = Button(frame_btn_result, text="복사할 파일(n)")
btn_result_copy2.pack(side="left")
btn_result_refresh = Button(frame_btn_result, text="갱신할 파일(n)")
btn_result_refresh.pack(side="left")

lable_expl_result = Label(frame_result_header, text="다음파일들을 백업합니다", bg="#f0f2f7", font = ("굴림", 14))
lable_expl_result.pack(side="top", expand=True)

# 5 버튼배열 하단에 리스트 
frame_mid_result = Frame(frame_center_result,  bg="#f0f2f7")
frame_mid_result.grid(row=1, column=0, sticky="nsew")

mid_result_scroll = Scrollbar(frame_mid_result)
mid_result_scroll.pack(side="right", fill="y")
mid_result_list = Listbox(frame_mid_result, selectmode="single", height=10, width="70", yscrollcommand=mid_result_scroll.set)
mid_result_list.pack(fill="both", expand=True, padx=10, pady=10)
mid_result_scroll.config(command=mid_result_list.yview)



# 5 리스트박스 데이터
for i in range(50):
    mid_result_list.insert(END, f"삭제 중앙 {i+1}")
    #bot_del_list.insert(END, f"삭제 하단 {i+1}")
    #mid_copy_list.insert(END, f"복사 중앙 {i+1}")
    #bot_copy_list.insert(END, f"복사 하단 {i+1}")
    #mid_renew_list.insert(END, f"갱신 중앙 {i+1}")
    #bot_renew_list.insert(END, f"갱신 하단 {i+1}")



# 백업확인알림창

#6번 백업화면&프로그레스바



#6-1 이후 바로 재검사 실시


#8-1 최적화 진행



#7번 백업완료
frame_center_complete = Frame(frame_main, relief="solid", bd="1")

#7번 중앙 리스트박스

frame_btn_complete = Frame(frame_center_complete, relief="solid", bd="1")
frame_btn_complete.pack(side="top")
btn_compl_delete = Button(frame_btn_complete, text="삭제할 파일(n)")
btn_compl_delete.pack(side="left")
btn_compl_delete2 = Button(frame_btn_complete, text="삭제할 파일(n)")
btn_compl_delete2.pack(side="left")
btn_compl_copy = Button(frame_btn_complete, text="복사할 파일(n)")
btn_compl_copy.pack(side="left")
btn_compl_copy2 = Button(frame_btn_complete, text="복사할 파일(n)")
btn_compl_copy2.pack(side="left")
btn_compl_refresh = Button(frame_btn_complete, text="갱신할 파일(n)")
btn_compl_refresh.pack(side="left")

label_complete = Label(frame_center_complete, text = "결과내용1", bg="#f0f2f7")
label_complete.pack()
label_complete2 = Label(frame_center_complete, text = "결과내용2", bg="#f0f2f7")
label_complete2.pack()
label_complete3 = Label(frame_center_complete, text = "결과내용3", bg="#f0f2f7")
label_complete3.pack()





#-------------------------------------------------------------------------------------

#하단 바
frame_bottombar = Frame(root,bg="#F0F2F7", height = "1.5c", highlightbackground="#cdd2e0", highlightthickness=1)
frame_bottombar.pack(side="bottom",fill="both")
frame_bottombar.pack_propagate(0)

# 완료단계에서만 표시
btn_optimize = Button(frame_bottombar, text= "최적화",  width="15", highlightbackground="#cdd2e0", highlightthickness=1)
# btn_begin.pack(side="right",fill="y")

btn_Previous = Button(frame_bottombar, text= "이전", width="15", highlightbackground="#cdd2e0", highlightthickness=1)
btn_Previous.pack(side="left", fill="y")
btn_begin = Button(frame_bottombar, text= "시작",  width="15", highlightbackground="#cdd2e0", highlightthickness=1)
btn_begin.pack(side="right",fill="y")

root.resizable(False,False) #전체 화면 가로,세로 사이즈 조절x 

# 프레임 변경 배열
frames = [
    frame_center_home, frame_center_select, frame_center_check, 
    frame_center_progress, frame_center_result, frame_center_complete
]

#모든 프레임 bg값 자동화
for f in frames:
    f.config(bg="#f0f2f7")


labels = [label_step_img, label_step_img2, label_step_img3, label_step_img4, label_step_img5, label_step_img6]

current_index = 0
