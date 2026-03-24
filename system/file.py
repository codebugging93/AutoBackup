import shutil
import os


def copy_file(src, dst, mkdirs=True, metadata=True):
    """
    mkdirs: 어떤 파일이 속할 폴더를 자동 생성하는 기능
    metadata: 파일의 메타데이터까지 복사하는 기능(수정된 시간 포함)

    권한이 없는 경우 metadata는 복사되지 않을 수 있다.
    가능한 한 chmod 권한까지 복사하려고 하기 때문이다.
    """

    if mkdirs:
        _dir = os.path.dirname(dst)
        os.makedirs(_dir, exist_ok=mkdirs)

    shutil.copyfile(src, dst) # 파일 복사
    if metadata:
        try: 
            shutil.copystat(src, dst) # 메타데이터 복사
        except PermissionError:
            # chmod를 사용할 권한이 없는 경우 PermissionError가 발생함 
            pass 


def move_file(src, dst, mkdirs=True, metadata=True):
    """
    copy_file(src, dst)로 파일을 복사하고
    src 파일을 os.remove로 삭제한다.
    """

    copy_file(src, dst, mkdirs=mkdirs, metadata=metadata)
    os.remove(src)



