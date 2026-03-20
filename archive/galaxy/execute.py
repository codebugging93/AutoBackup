# 입맛대로 커스텀 할 수 있는 모듈이다.

from galaxy.paths import NOTE8_PATHS, J3_PATHS
from galaxy.backup import backup_onlysame
 
def execute_task():
    """ execute_task는 스레드로 동작하도록 설계되었으므로 이 함수 이하의 것들은 스레드 처리를 할 필요가 거의 없다. """
    backup_onlysame(*NOTE8_PATHS)
    backup_onlysame(*J3_PATHS)