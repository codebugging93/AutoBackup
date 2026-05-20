""" 
이 모듈 내의 함수 init()으로 프로그램이 시작할 수 있다.

1 페이즈;경로 지정과 버튼 클릭, 비교를 한 후에 대답(2페이즈)으로 넘긴다. 
여기에서 버튼이 바인딩 된다.
"""

from threading import Thread
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo, showerror, askyesno

from implemented.compare_state import CMP_STATS, get_state, get_state_str
from gui.binding import bind_progress
from gui.layout import decorate_layout, expand_layout
from gui.widgets import *
from gui.handle_widgets import *
from gui.implemented_tasks import compare, get_dir_size, get_path_info, get_root_size, get_samedir_tree, listbox_clear, listbox_update
from gui.messages import *
from gui.exfat import toggle_exfat_btn
from system.byte import convert_byte
from implemented.main_datas import main_prog, sub_prog, backup_data, configs, original, target, reset_datas
from system.constants import APPNAME, CMP_MODES
from system.path import get_root_files_count

from gui.level_2 import ready_backup_answer



# 프로그램의 시작 지점 
def init(): 
    # 바인딩
    btn_newtask.config(command=btncmd_newtask)
    btn_compare.config(command=btncmd_compare)
    btn_single.config(command=btncmd_toponly)
    btn_exfat.config(command=btncmd_exfat)
    btn_macro.config(command=btncmd_macro)

    # UI 요소 초기화
    reset_datas()
    reset_screen()
    lock_ui()
    unlock_widget(btn_newtask)

    # UI 요소 시동    
    decorate_layout()
    expand_layout()


def reset_screen():
    """ 
    버튼, 텍스트, 엔트리, Progress, 리스트박스 초기화 
    모든 UI 요소를 비활성화시킴
    """ 
    entry_ans.reset()
    listbox_clear()
    text_log.clear()
    main_prog.clear()
    sub_prog.clear()

    

def newtask(): 
    """ 
    Folder.path, .depth를 
    초기화하는 유일한 곳 
    """
    if backup_data.cmp_state is not None:
        ans = askyesno(APPNAME, "현재 작업을 삭제하고 새 작업을 시작할까요?")
        if not ans:
            return None

    # 초기화; init부분이랑 같은 코드임
    reset_datas()
    reset_screen()
    configs.exfat(False) # "새 작업" 버튼을 누를 때는 이 옵션이 기본값으로 설정되어야 함; configs의 속성이 추가될 가능성이 있어 configs.reset()을 사용하지 않았음
    lock_ui()
    unlock_widget(btn_newtask)
    
    while True:
        # 첫번째 폴더 선택
        _list = [] 
        for i in ("원본", "대상"):
            showinfo(APPNAME, f"{i} 폴더를 선택해주세요.")
            path = askdirectory(title=f"{i} 폴더 선택")
            if not path:
                text_log.clear()
                showinfo(APPNAME, "취소하셨습니다.")
                return None
            
            _list.append(path)
            text_log.print(f"{i} 폴더 : {path}") 


            # # 디버깅 용 코드
            # original.assign(path)
            # target.assign(path)
            # unlock_buttons()
            # return None


        # 폴더 검사
        path1, path2 = _list[0] , _list[1]
        if path1 == path2: 
            showerror(APPNAME, "같은 폴더를 선택하셨습니다. \n다시 선택해주세요.")
            text_log.clear()
            continue
        # 통과
        else:
            break
        
    # 폴더별 설정
    original.assign(path1)
    target.assign(path2)

    # 버튼 잠금해제
    unlock_buttons()
    

# 폴더 로딩 
def loading_folder(): 
    """
    original, target 새로고침
    """
    _mode = configs.compare_mode

    for i in (original, target):
        text_log.print(f"[로딩] {i.tag} 폴더 로딩")
        text_log.print(f"경로 : {i.path}")
    
        # 트리, 폴더수, 파일수   
        if _mode == CMP_MODES.ALL:
            i.tree, i.folders, i.files = get_path_info(i) 
        elif _mode == CMP_MODES.TOP_ONLY:
            i.tree.attach("", 0) 
            i.folders = 0
            i.files = get_root_files_count(i.path)
        text_log.print(f"폴더 수 : {i.folders}")
        text_log.print(f"파일 수 : {i.files}")
        
        # 크기
        if _mode == CMP_MODES.ALL:
            i.size = get_dir_size(i.path)
        elif _mode == CMP_MODES.TOP_ONLY:
            i.size = get_root_size(i.path)
            pass
        byte_str, detail = convert_byte(i.size)
        text_log.print(f"크기 : {byte_str} {detail}")

        
        text_log.print() # 행갈이

    # 데이터 정리
    if _mode == CMP_MODES.ALL: # 전체비교
        backup_data.tree_same = get_samedir_tree()
        backup_data.cmp_state = get_state(backup_data.tree_same) 
    elif _mode == CMP_MODES.TOP_ONLY: # 탑비교
        backup_data.tree_same.attach("", 0) # it only contains root folder
        backup_data.cmp_state = CMP_STATS.ROOT
    else:
        raise ValueError("wrong compare modes: " + str(_mode))
    
    # 위의 for문에서 행갈이가 이미 되어있음
    text_log.print("[백업 전 상태 확인]")
    text_log.print(get_state_str(backup_data.cmp_state))
    text_log.print(f"백업 가능한 폴더 수 : {backup_data.tree_same.num}")



# 비교 커맨드
# 일반모드/싱글모드 각각 테스트
def compare_run():
    # 재확인
    if backup_data.cmp_state != None:
        ans = askyesno(APPNAME, "현재 결과를 삭제하고 다시 비교할까요?")
        if not ans:
            return None
        
    # 화면 초기화
    lock_ui()
    reset_screen()
    reset_datas()

    # 폴더 정보, data.state 로딩
    loading_folder() 
    
    # 검사 
    compare() 
    
    # 리스트박스 새로고침
    listbox_update(backup_data)
    
    # 여러 정보 표시
    text_log.print("\n[검사 완료 / 중간 점검]")
    text_log.print(f"원본 폴더 : {original.path}\n대상 폴더 : {target.path}")
    text_log.print(get_state_str(backup_data.cmp_state))

    msg_list = [
        ("백업 가능 폴더", backup_data.tree_same.num),
        ("복사할 폴더", backup_data.tree_copy.num),
        ("삭제할 폴더", backup_data.tree_rmv.num),
        ("동일한 파일", len(backup_data.set_file_same)),
        ("복사할 파일", len(backup_data.set_file_copy)),
        ("삭제할 파일", len(backup_data.set_file_rmv)),
        ("갱신할 파일", len(backup_data.set_file_renew)),
    ]
    text_log.print()
    for text, num in msg_list:
        msg = f"{text} 수 : {num} 개"
        text_log.print(msg)
    
    
    # 검사 현황 안내
    text_log.print()
    if configs.compare_mode == CMP_MODES.TOP_ONLY:
        text_log.print(msg_chk_toponly)
    elif configs.compare_mode == CMP_MODES.ALL:
        if backup_data.cmp_state == CMP_STATS.SAME:
            text_log.print(msg_chk_same)
        elif backup_data.cmp_state == CMP_STATS.PARTIAL:
            text_log.print(msg_chk_partial)
        elif backup_data.cmp_state == CMP_STATS.NOTSAME:
            text_log.print(msg_chk_notsame)
        else:
            raise ValueError("backup_data.cmp_state can't be this value: " + str(backup_data.cmp_state))
    else:
        raise ValueError("configs.compare_mode assigned wrong value:" + str(configs.compare_mode))
    
    # 경고
    bool1 = len(backup_data.set_file_copy) == original.files
    bool2 = len(backup_data.set_file_rmv) == target.files
    bool3 = backup_data.tree_copy.num == original.tree.num
    bool4 = backup_data.tree_rmv.num == target.tree.num
    if bool1 or bool2 or bool3 or bool4:
        text_log.print("※경고※\n폴더를 제대로 선택하셨는지 다시 한번 확인해주세요.")
                
    # TKgui.level_2 넘어갈 준비, 대답 받을 준비
    ready_backup_answer()

  
# 경로 선택 버튼 클릭 
def btncmd_newtask():
    Thread(target=newtask).start()


# 비교 버튼 클릭 
def btncmd_compare():
    configs.compare_mode = CMP_MODES.ALL
    Thread(target=compare_run).start()
    
    
# 단일 백업 버튼 클릭 
def btncmd_toponly():
    configs.compare_mode = CMP_MODES.TOP_ONLY
    Thread(target=compare_run).start()


# exFAT 버튼 클릭
def btncmd_exfat():
    toggle_exfat_btn()






    
def task1(path1, path2):
    # 새 작업
    lock_buttons()
    reset_datas()
    reset_screen()

    original.assign(path1)
    target.assign(path2)


    # 비교
    compare_run()

    
def btncmd_macro():
    backup_data.mode = "compare"
    Thread(target=macro).start()