"""
이 모듈은 pkg가 필요없으니 독립 실행 가능
"""

import os
from tkinter.filedialog import askdirectory, askopenfilename
from time import time, sleep
from threading import Thread
from math import floor
import tkinter as tk


mode = ""
thread_msg = "" # 전역 변수
isupdate = False




def get_thread_msg():
    global thread_msg
    return thread_msg


def thread_setmsg(prefix, num, total):
    global thread_msg
    # 문자열 생성
    thread_msg = f"{prefix} {num}/{total}"


def thread_run():
    fps = 1
    fpsdt = 1 / fps
    tick1 = time()

    while isupdate:
        # 텍스트 출력
        message = get_thread_msg()
        text_log.insert('end', message + "\n")        
        text_log.see('end')

        # 프레임 처리
        dt = time() - tick1
        if dt < fpsdt:
            sleep(fpsdt - dt)
        tick1 = time()

        
    # 99%로 보이는거 방지
    text_log.insert('end', get_thread_msg() + "\n")
    text_log.insert('end', "완료\n")
    text_log.see('end')


def adapt_mtime(data_path, folder_path):
    global isupdate 
    
    with open(data_path, "r", encoding='utf8') as file:
        lines = file.readlines()
        total = len(lines)

    thread_setmsg("[최적화]", 0, total)
    isupdate = True
    thr = Thread(target=thread_run)
    thr.start()
    
    i = 0
    for line in lines:
        i += 1
        fname, time = line.split(":")
        time = float(time)
        file_path = os.path.join(folder_path, fname)
        os.utime(file_path, (time, time))
        thread_setmsg("[최적화]", i, total)
        
    isupdate = False
    thr.join()
    
    
def remove_files(data_path, folder_path):
    global isupdate
    
    with open(data_path, "r", encoding='utf8') as file:
        lines = file.readlines()
        total = len(lines)

    thread_setmsg("[파일 삭제]", 0, total)
    isupdate = True
    thr = Thread(target=thread_run)
    thr.start()
    
    i = 0
    for line in lines:
        i += 1
        fname = line.replace("\n", "")
        fpath = os.path.join(folder_path, fname)
        os.remove(fpath)
        thread_setmsg("[파일 삭제]", i, total)
        
    isupdate = False
    thr.join()
    

def btncmd(mode, data_path, folder_path):
    if mode == 'mtime':
        Thread(target=adapt_mtime, args=(data_path, folder_path)).start()
    elif mode == 'rmv':
        Thread(target=remove_files, args=(data_path, folder_path)).start()
    
    
    

if __name__ == "__main__":
    
    # ui 시작
    root = tk.Tk()
    text_log = tk.Text(root, font=("monospace", 14), height=15)
    text_log.pack()
    bt = tk.Button(root, text="실행")
    bt.pack()
    

    # data_path는 삭제할 파일 리스트가 보관된 파일이거나
    # 수정할 시간 파일 리스트가 보관된 파일이다.
    data_path = askopenfilename(title="Select Data File")
    if not data_path:
        raise Exception
        
    # folder_path는 시간을 적용할 폴더
    folder_path = askdirectory(title="Select Folder")
    if not folder_path:
        raise Exception
    
    # 화면에 표시
    string = f"데이터 파일 : {data_path}\n적용할 폴더 : {folder_path}\n"
    text_log.insert('end', string)
    
    # 파일명이 _rmv로 끝나거나 _mtime으로 끝나지 않으면 오류를 일으키게 설계됨
    _filename = os.path.basename(data_path)
    name = os.path.splitext(_filename)[0]
    i = name.rfind("_")
    mode = name[i + 1:]
    if mode not in ("rmv", "mtime"):
        raise Exception("unidentified file type")
    
    # 버튼 바인딩
    bt.config(command=lambda: btncmd(mode, data_path, folder_path))

    root.mainloop()