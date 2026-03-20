import os
from datetime import datetime
from utils.constants import APPNAME
from utils.path import add_dir_num



def mk_trashbin(format_data="%Y-%m-%d %H시%M분%S초 백업본"):
    """
    날짜를 이름으로 한 폴더 생성
    파일/폴더 삭제 전에 반드시 행해야함
    """
    # 날짜 불러오고 폴더 이름 설정
    name = datetime.now().strftime(format_data)
    name = add_dir_num(name, get_app_trashbin_path()) # 혹시나 있을 중복 방지

    # 휴지통 생성
    if not os.path.isdir(get_app_trashbin_path()):
        os.mkdir(get_app_trashbin_path())

    # remove_path 재정의
    p = os.path.join(get_app_trashbin_path(), name)
    set_backup_remove_path(p)
    os.mkdir(get_backup_remove_path())


def chk_trashbin_empty():
    """ 휴지통이 비어있는 지 확인 """
    contents = os.listdir(get_backup_remove_path())
    return len(contents) == 0




def get_backup_remove_path():
    return _backup_remove_path


def set_backup_remove_path(path):
    global _backup_remove_path
    _backup_remove_path = path


def get_app_trashbin_path():
    return _app_trashbin_path


def set_app_trashbin_path(path):
    global _app_trashbin_path
    _app_trashbin_path = path


def _get_download_path(folder_name=""):
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:

            p = winreg.QueryValueEx(key, downloads_guid)[0]
    elif os.name == 'posix':
        p = "/storage/emulated/0/Download"
    else:
        p = os.path.join(os.path.expanduser('~'), 'downloads')

    return os.path.join(p, folder_name)


_backup_remove_path = ""
_app_trashbin_path = _get_download_path(folder_name=APPNAME + "_휴지통")






