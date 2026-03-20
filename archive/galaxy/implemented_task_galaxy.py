from gui.implemented_tasks import compare
from galaxy.implemented.discard import discard_dummy_datas
from implemented.main_datas import main_prog, sub_prog, backup_data
from galaxy.implemented.backup import backup_copy, backup_remove, backup_boost


def compare_galaxy():
    compare() # backup_data에 모든 정보 저장

    main_prog.reset(prefix="[.nomedia 제외 중]")
    main_prog.update_wait()
    discard_dummy_datas()
    main_prog.stop()
    

def create_backup_datas():
    main_prog.reset(prefix="[파일 복사]", total=len(backup_data.set_file_copy))
    main_prog.update_progress()

    backup_copy()

    main_prog.stop()

    main_prog.reset(prefix="[데이터 작성]", total=len(backup_data.set_file_rmv))
    main_prog.update_progress()

    backup_remove()

    main_prog.stop()


def create_boost_data():
    main_prog.reset(prefix="[데이터 작성]", total=len(backup_data.set_file_same))
    main_prog.update_progress()

    backup_boost()

    main_prog.stop()
