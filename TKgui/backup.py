""" backup 커맨드를 모아놓은 것; 로그를 표시하고, 지정된 작업만 수행한다. """

from utils.Classes.BackupData import BackupData
from implemented.trashbin import RemovePathNotEmpty, get_app_trashbin_path, chk_trashbin_empty
from implemented.trashbin import mk_trashbin
from TKgui.widgets import text_log
from TKgui.implemented_tasks import boost_files, copy_files, copy_folders, remove_files, remove_folders, renew_files



def backup_file(backup_data: BackupData) -> bool:
    """ 
    data의 파일을 삭제하고 복사하고, 갱신함 
    return값은 파일이 백업 되었는가를 나타냄
    """

    is_able_to_backup = backup_data.is_able_to_backup_file()
    if not is_able_to_backup:
        text_log.print("백업할 파일이 없습니다.")
        return is_able_to_backup

    # 삭제
    need_remove = not (len(backup_data.set_file_rmv) == len(backup_data.set_file_renew) == 0)
    if need_remove: # 삭제하거나 갱신할게 있으면 쓰레기통 생성
        mk_trashbin()        
        remove_files(backup_data.set_file_rmv)
        renew_files(backup_data.set_file_renew)
        text_log.print(f"[로그] 삭제되었거나 갱신되기 이전의 파일은 {get_app_trashbin_path()}에 보관되었습니다.")
    
    # 복사
    need_copy = len(backup_data.set_file_copy) != 0
    if need_copy:
        copy_files(backup_data.set_file_copy)

    text_log.print("백업을 완료했습니다.")
    is_backuped = is_able_to_backup 
    return is_backuped


def backup_all(backup_data: BackupData, is_aftercheck=False) -> bool:
    """ 
    data의 파일과 폴더를 삭제하고, 복사하고, 갱신함 
    return값은 백업이 되었는가를 나타냄
    """
    is_able_to_backup = backup_data.is_able_to_backup_all()
    if not is_able_to_backup:
        text_log.print("백업할 파일이 없습니다.")
        return is_able_to_backup

    # 삭제
    need_remove = not (len(backup_data.set_file_rmv) == len(backup_data.set_file_renew) == backup_data.tree_rmv.num == 0)
    if need_remove:
        mk_trashbin()
        remove_folders(backup_data.tree_rmv)
        remove_files(backup_data.set_file_rmv)
        renew_files(backup_data.set_file_renew)
        text_log.print(f"[로그] 삭제되었거나 갱신되기 이전의 개체는 {get_app_trashbin_path()}에 보관되었습니다.")
    
    # 복사
    need_copy = not (len(backup_data.set_file_copy) == backup_data.tree_copy.num == 0)
    if need_copy: # need_copy가 True이면 반드시 어느 하나는 로그를 출력함
        copy_folders(backup_data.tree_copy)
        copy_files(backup_data.set_file_copy)

    if is_aftercheck:
        text_log.print("백업을 다시 완료했습니다.")
    else: 
        text_log.print("백업을 완료했습니다.")
    is_backuped = is_able_to_backup # 반드시 True
    return is_backuped


# 최적화
def backup_boost(backup_data: BackupData):
    boost_files(backup_data.set_file_same)
    text_log.print(f"[로그] {len(backup_data.set_file_same)}개의 파일을 최적화했습니다.")
    