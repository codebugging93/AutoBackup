import os

import implemented.compare
import implemented.file
import implemented.aftercheck 
import implemented.path
from utils.constants import BACKUP_MODES
import utils.path
import implemented.DepthList

from utils.Classes.BackupData import BackupData
from implemented.main_datas import main_prog, original, target, sub_prog, backup_data, configs, aftercheck_data
from utils.Classes.Folder import Folder

from TKgui.custom_widgets import LabelListboxWithFrame
from TKgui.widgets import (
    text_log, 
    llboxes, 
    llbox_file_copy, 
    llbox_file_renew, 
    llbox_file_rmv, 
    llbox_folder_copy, 
    llbox_folder_rmv,
)



    

""" utils.path 구현 """

def get_dir_size(path):
    main_prog.reset(prefix="[폴더 용량 측정]")
    main_prog.update_byte()

    size = implemented.path.get_dir_size(path)

    main_prog.stop()
    
    return size


def get_root_size(path):
    main_prog.reset(prefix="[폴더 용량 측정]")
    main_prog.update_byte()

    size = implemented.path.get_root_size(path)

    main_prog.stop()
    
    return size


""" utils.DepthList 구현 """

def get_samedir_tree():
    main_prog.reset(prefix="[백업 가능한 폴더 탐색]")
    main_prog.update_wait()
    
    sametree = utils.DepthList.get_samedir_tree(original.tree, target.tree)
    
    main_prog.stop()
    
    return sametree
    


""" implemented.path 구현 """
def get_path_info(folobj: Folder):
    main_prog.reset(prefix="[폴더 로딩]")
    main_prog.update_count()
    
    tree, folders, files = implemented.path.get_path_info(folobj.path)
    
    main_prog.stop()
    
    return tree, folders, files



""" implemented.file 구현 """
def renew_files(_set):
    if len(_set) == 0:
        return None

    main_prog.reset(prefix="[파일 갱신]", total=len(_set))
    main_prog.update_progress()
    
    implemented.file.renew_files(main_prog, _set)
    
    main_prog.stop()
    text_log.print("[로그] 파일 갱신 완료")
    

# 파일 삭제
def remove_files(_set):
    if len(_set) == 0:
        return None
    
    main_prog.reset(prefix="[파일 삭제]", total=len(_set))
    main_prog.update_progress()

    implemented.file.remove_files(main_prog, _set)

    main_prog.stop()
    text_log.print("[로그] 파일 삭제 완료")
    
    
# 파일 복사
def copy_files(_set):
    if len(_set) == 0:
        return None
    
    main_prog.reset(prefix="[파일 복사]", total=len(_set))
    main_prog.update_progress()
    
    implemented.file.copy_files(main_prog, _set)
    
    main_prog.stop()
    text_log.print("[로그] 파일 복사 완료")
    
        
# 폴더 삭제
def remove_folders(tree: implemented.DepthList.DepthList):
    if tree.num == 0:
        return None
    
    main_prog.reset(prefix="[폴더 삭제]", total=tree.num)
    sub_prog.reset(prefix="[파일 삭제]")
    main_prog.update_progress()
    sub_prog.update_progress()

    implemented.file.remove_folders(tree)
    
    main_prog.stop()
    sub_prog.stop()
    sub_prog.clear()
    text_log.print("[로그] 폴더 삭제 완료")
    

# 폴더 복사
def copy_folders(tree: implemented.DepthList.DepthList):
    if tree.num == 0:
        return None
    
    main_prog.reset(prefix="[폴더 복사]", total=tree.num)
    sub_prog.reset(prefix="[파일 복사]")
    main_prog.update_progress()
    sub_prog.update_progress()

    implemented.file.copy_folders(tree)
    
    main_prog.stop()
    sub_prog.stop()
    sub_prog.clear()
    text_log.print("[로그] 폴더 복사 완료")


# 백업 최적화
def boost_files(_set):
    if len(_set) == 0:
        return None
    
    main_prog.reset(prefix="[백업 최적화]", total=len(_set))
    main_prog.update_progress()

    implemented.file.boost_files(_set)

    main_prog.stop()


""" 리스트박스 구현"""


# 초기화
def listbox_clear():
    for i in llboxes:
        i.clear()
    

# listbox 업데이트
def listbox_update(data: BackupData):
    total = 0
    for i in (data.tree_rmv, data.tree_copy):
        total += i.num
    for i in (data.set_file_renew, data.set_file_rmv, data.set_file_copy):
        total += len(i)

    sub_prog.reset(prefix="[파일/폴더 표시]", total=total)
    sub_prog.update_progress()
    
    _folder_update(llbox_folder_rmv, data.tree_rmv, target.path)
    _folder_update(llbox_folder_copy, data.tree_copy, original.path)
    _file_update(llbox_file_renew, data.set_file_renew, target.path)
    _file_update(llbox_file_rmv, data.set_file_rmv, target.path)
    _file_update(llbox_file_copy, data.set_file_copy, original.path)
    
    sub_prog.off()
    sub_prog.stop()
    
    
def _file_update(llbox: LabelListboxWithFrame, _set, path):
    llbox.hide_listbox()
    for i in _set:
        p = os.path.join(path, i)
        llbox.add(p)
        sub_prog.num += 1 
    llbox.indicate_num()
    llbox.show_listbox()
    
    
def _folder_update(llbox: LabelListboxWithFrame, _deplist, path):
    llbox.hide_listbox()
    for _set in _deplist:
        for k in _set:
            p = os.path.join(path, k)
            llbox.add(p)
            sub_prog.num += 1
    llbox.indicate_num()
    llbox.show_listbox()


""" compare 구현 """
def _checkloading(sametree: implemented.DepthList.DepthList) -> tuple[list, int]:
    main_prog.reset(prefix="[체크 전 로딩]", total=backup_data.tree_same.num)
    main_prog.update_progress()
    
    file_list, total_file = implemented.compare.checkloading(sametree)
    
    main_prog.stop()
    
    return file_list, total_file
    

def _checkfolder(sametree: implemented.DepthList.DepthList):
    main_prog.reset(prefix="[폴더 체크]")
    main_prog.update_wait()
    
    copy, rmv = implemented.compare.checkfolder(sametree)
    
    main_prog.stop()

    return copy, rmv


def _checkfile(file_list: list, total_file: int): 
    """ total_file은 검사할 파일의 수 """
    main_prog.reset(prefix="[파일 체크]", total=total_file)
    sub_prog.reset(prefix="[파일 분류]")
    sub_prog.off()
    main_prog.update_progress()
    sub_prog.update_progress()
    
    copy, renew, rmv, same = implemented.compare.checkfile(file_list)
    
    main_prog.stop()
    sub_prog.stop()

    return copy, renew, rmv, same
    

def compare():
    """
    사용하기 위해 필요한 변수
    original.path
    original.depth
    original.tree(선택)
    target.path
    target.depth
    target.tree(선택)
    data.tree_same
    """

    # 1. 로딩
    file_list, total_file = _checkloading(backup_data.tree_same)
    
    # 2. 폴더 검사
    backup_data.tree_copy, backup_data.tree_rmv = _checkfolder(backup_data.tree_same)
    
    # 3. 파일 검사
    values = _checkfile(file_list, total_file) # copy, renew, rmv, same
    backup_data.set_file_copy, backup_data.set_file_renew, backup_data.set_file_rmv, backup_data.set_file_same = values


"""
implemented.aftercheck 구현
"""
def aftercheck():
    """ 백업에 실패한 파일의 리스트를 업데이트하고 반환한다. """
    failed = aftercheck_data
    failed.reset()

    # 1. 파일 복사 확인 
    copy, renew = _aftercheck_file_copy()
    failed.set_file_copy.update(copy)
    failed.set_file_renew.update(renew)

    # 2. 파일 삭제 확인
    rmv = _aftercheck_file_rmv()
    failed.set_file_rmv.update(rmv)

    # 3. 파일 갱신 확인
    copy, renew = _aftercheck_file_renew()
    failed.set_file_copy.update(copy)
    failed.set_file_renew.update(renew)
    
    # 4. 트리 복사/삭제 확인   +전체 백업을 했다면 트리 복사/삭제까지 확인해야 한다.
    if configs.backup_mode == BACKUP_MODES.ALL:
        copy, renew, tcopy = _aftercheck_tree_copy()
        failed.set_file_copy.update(copy)
        failed.set_file_renew.update(renew)
        failed.tree_copy = tcopy
        failed.tree_rmv = _aftercheck_tree_rmv()
    elif configs.backup_mode == BACKUP_MODES.FILE:
        pass
    else:
        raise ValueError("wrong backup modes:", configs.backup_mode)


# 파일 복사 확인
def _aftercheck_file_copy():
    main_prog.reset(prefix="[파일 복사 확인]", total=len(backup_data.set_file_copy))
    main_prog.update_progress()

    copy, renew = implemented.aftercheck.aftercheck_file_copy(backup_data.set_file_copy)

    main_prog.stop()

    return copy, renew


# 파일 삭제 확인
def _aftercheck_file_rmv():
    main_prog.reset(prefix="[파일 삭제 확인]", total=len(backup_data.set_file_rmv))
    main_prog.update_progress()

    rmv = implemented.aftercheck.aftercheck_file_rmv(backup_data.set_file_rmv)

    main_prog.stop()

    return rmv


# 파일 갱신 확인
def _aftercheck_file_renew():
    main_prog.reset(prefix="[파일 갱신 확인]", total=len(backup_data.set_file_renew))
    main_prog.update_progress()

    copy, renew = implemented.aftercheck.aftercheck_file_renew(backup_data.set_file_renew)

    main_prog.stop()

    return copy, renew


# 폴더 복사 확인
def _aftercheck_tree_copy():
    main_prog.reset(prefix="[폴더 복사 누락 확인]", total=backup_data.tree_copy.num)
    sub_prog.reset()
    sub_prog.off()
    main_prog.update_progress()
    sub_prog.update_progress()

    files_copy, files_renew, tree_copy = implemented.aftercheck.aftercheck_tree_copy(backup_data.tree_copy)

    main_prog.stop()
    sub_prog.stop()
    sub_prog.clear()

    return files_copy, files_renew, tree_copy


# 폴더 삭제 확인
def _aftercheck_tree_rmv():
    main_prog.reset(prefix="[폴더 삭제 누락 확인]", total=backup_data.tree_rmv.num)
    main_prog.update_progress()

    tree = implemented.aftercheck.aftercheck_tree_rmv(backup_data.tree_rmv)

    main_prog.stop()

    return tree