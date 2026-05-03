import os
from datetime import datetime
from system.constants import APPNAME
from system.path import add_dir_num



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



class Trashbin:
    """
    파일 백업 중에 삭제/수정 등의 작업이 일어나면, 
    그 파일을 전용 휴지통에 보관한다.

    app_trashbin_path는 그 전용 휴지통의 경로이며, 
    유저 다운로드 폴더/Autobackup_휴지통이 기본값으로 되어있다.

    그리고 백업을 할 때마다 휴지통 안에 
    xxx 백업본과 같은 고유한 이름을 붙여야 한다.

    그렇게 정해진 이름을 remove_path라고 한다.
    """
    remove_path = ""

    @classmethod
    def make_trashbin(
        cls, 
        path,
        trashbin_name=APPNAME + "_휴지통",
        folder_name="%Y-%m-%d %H시%M분%S초 백업본"):
        """
        날짜를 이름으로 한 폴더 생성.
        Trashbin.remove_path가 갱신된다.
        """
        # 날짜 불러오고 폴더 이름 설정
        name = datetime.now().strftime(folder_name)
        p = os.path.join(path, trashbin_name, name)
        p = add_dir_num(p, os.path.dirname(p)) # 혹시나 있을 중복 방지
        os.makedirs(p, exist_ok=True)
        cls.remove_path = p


    @classmethod
    def get_remove_path(cls):
        if cls.remove_path == "":
            raise Exception("먼저 make_trashbin을 실행하세요.")
        return cls.remove_path







