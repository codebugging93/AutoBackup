from galaxy.level_main import compare_run
from utils.constants import CMP_MODES
from implemented.main_datas import configs


def backup_onlysame(org_path, tar_path):
    configs.compare_mode = CMP_MODES.ALL
    compare_run(org_path, tar_path)


def backup_single(org_path, tar_path):
    configs.compare_mode = CMP_MODES.TOP_ONLY
    compare_run(org_path, tar_path)
    