from implemented.compare_state import get_state, get_state_str
from utils.byte import convert_byte
from implemented.main_datas import original, target, backup_data, configs
from utils.constants import CMP_MODES, CMP_STATS
from utils.path import get_root_files_count
from gui.messages import msg_chk_toponly, msg_chk_same, msg_chk_notsame, msg_chk_partial
from gui.implemented_tasks import get_dir_size, get_path_info, get_root_size, get_samedir_tree

from galaxy.widgets import *


"""
시작버튼을 누르면:
    for 폴더 in 폴더들:
        폴더의 경로를 original, target에 고루 분배한다.
        폴더를 로딩한다.
        파일 체크를 한다.
        파일 복사/데이터 생성을 한다.
"""

def loading_folder():
    """
    TKgui.level_1의 loading_folder를 복제해서 사용하였음
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


def print_datas():
    # 여러 정보 표시 (TKgui.level_1.loading_folder을 복제함)
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

    
