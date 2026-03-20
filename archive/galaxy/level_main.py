from gui.handle_widgets import lock_widget, unlock_widget
from galaxy.implemented_task_galaxy import compare_galaxy, create_backup_datas, create_boost_data
from galaxy.level_1 import loading_folder, print_datas
from galaxy.level_2 import get_answer_for_backup, get_answer_for_boost
from galaxy.widgets import entry_ans_with_frame, text_log
from implemented.main_datas import reset_datas, original, target


def compare_run(org_path, tar_path): 
    reset_datas()
    original.assign(org_path)
    target.assign(tar_path)

    lock_widget(entry_ans_with_frame.entry)
    reset_datas()
    loading_folder()
    compare_galaxy()
    print_datas()

    if get_answer_for_backup(): 
        create_backup_datas()
    if get_answer_for_boost():
        create_boost_data()
    text_log.print("\n\n\n모든 작업이 끝났습니다.\n\nㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

    
    