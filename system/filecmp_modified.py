""" EXFAT 드라이브에서 filecmp의 cmp 함수가 속도가 느리다.
    그래서 속도를 개선한 함수 cmp_filter과 auto_set_filter 함수를 탑재하였다.

    서로 다른 드라이브 간에 여러 파일의 cmp 작업을 하기 전에
    auto_set_filter 함수를 반드시 사용해서 필터를 자동 선택 해야 한다.
"""


__all__ = [
    "cmp_filter",
    "auto_set_filter",
]

import stat
import os
from system.path import add_file_num


###################################### 
# 원본 CMP 함수 (cmp_filter는 아래에 있음)

_cache = {}
BUFSIZE = 8*1024

def cmp(f1, f2, shallow=True):
    """Compare two files.

    Arguments:

    f1 -- First file name

    f2 -- Second file name

    shallow -- treat files as identical if their stat signatures (type, size,
               mtime) are identical. Otherwise, files are considered different
               if their sizes or contents differ.  [default: True]

    Return value:

    True if the files are the same, False otherwise.

    This function uses a cache for past comparisons and the results,
    with cache entries invalidated if their stat information
    changes.  The cache may be cleared by calling clear_cache().

    """

    s1 = _sig(os.stat(f1))
    s2 = _sig(os.stat(f2))
    if s1[0] != stat.S_IFREG or s2[0] != stat.S_IFREG:
        return False
    if shallow and s1 == s2:
        return True
    if s1[1] != s2[1]:
        return False
    outcome = _cache.get((f1, f2, s1, s2))
    if outcome is None:
        outcome = _do_cmp(f1, f2)
        if len(_cache) > 100:      # limit the maximum size of the cache
            clear_cache()
        _cache[f1, f2, s1, s2] = outcome
    return outcome


def _sig(st):
    return (stat.S_IFMT(st.st_mode),
            st.st_size,
            st.st_mtime)


def _do_cmp(f1, f2):
    bufsize = BUFSIZE
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            if b1 != b2:
                return False
            if not b1:
                return True
            

def clear_cache():
    """Clear the filecmp cache."""
    _cache.clear()


# 원본 내용은 여기까지
############################################


def cmp_filter(f1, f2, shallow=True): 
    """
    중요: auto_set_filter()를 실행해서 필터를 정해주고 이 함수를 실행해야 한다.

    f1을 원본 파일로, f2를 대상 파일로 간주하여 비교한다.
    f1의 수정된 시간에 필터를 적용시켜 f2와 빠른 비교를 한다.

    검사가 빨리 끝나려면 파일의 용량과 수정된 시간이 일치해야 한다.
    그런데 똑같은 파일을 복사해도 드라이브/운영체제마다 수정된 시간이 정확히 기록되지 않는다.

    예를 들어, 윈도우에서 exFAT 드라이브에 어떤 파일을 저장한다고 치자.
    이 원본 파일의 수정된 시간은 2000392.1234567이다. 
    이것을 똑같이 복사해서 exFAT 드라이브에 넣으면, 2000394.0초로 변한다.
    완전히 똑같은 파일인데 수정된 시간이 다르게 저장되는 것이다. 

    그래서 수정된 시간을 일치시키기 위해, 
    원본 파일 f1의 수정된 시간을 2초 반올림 시키거나, 소수점을 없애거나 하는 등의 필터를 적용시킨다.
    이렇게 일치시키면 정확도는 다소 떨어질 수 있지만 그래도 검사가 빨리 끝난다.
    """

    s1 = _sig_filter(os.stat(f1))
    s2 = _sig(os.stat(f2))
    if s1[0] != stat.S_IFREG or s2[0] != stat.S_IFREG:
        return False
    if shallow and s1 == s2:
        return True
    if s1[1] != s2[1]:
        return False
    outcome = _cache.get((f1, f2, s1, s2))
    if outcome is None:
        outcome = _do_cmp(f1, f2)
        if len(_cache) > 100:      # limit the maximum size of the cache
            clear_cache()
        _cache[f1, f2, s1, s2] = outcome
    return outcome
    


def _sig_filter(st):
    global _filter # auto_set_filter로 정해진 필터 사용
    return (stat.S_IFMT(st.st_mode),
            st.st_size,
            _filter(st.st_mtime)) # 바뀔 수 있음


def _get_filter():
    global _filter
    return _filter


def auto_set_filter(target_dir):
    """
    https://superuser.com/questions/1685706/timestamp-changes-when-copying-file-to-exfat-drive

    https://blog.npcode.com/2013/02/03/%ED%8C%8C%EC%9D%BC%EC%8B%9C%EC%8A%A4%ED%85%9C%EC%9D%98-timestamp-%EC%A0%95%EB%B0%80%EB%8F%84/

    이렇게 기기마다 수정된 시간을 저장하는 방법이 다 다르다..

    원본 파일은 윈도우에 있고 대상 파일은 외부 저장장치(exFAT)에 있다고 가정하자.

    내가 생각한 방법은, 123.12345678의 수정시간을 가지는 파일을 만들어서
    만약 결과가 123.0으로 나오면 앞으로 원본 파일에 int를 씌워서 대상 파일과 검사시킨다.
    만약 결과가 124.0으로 나오면 2초 반올림을 적용해서 대상 파일과 비교한다.
    만약 결과가 123.123으로 나오면 이런식의 필터를 적용해서 비교한다.

    여러가지 케이스를 두고 비교해서, 사전에 적절한 필터를 선택하도록 하면 된다.

    """
    global _filter 
    
    name = "modified_time_test_file.txt"
    name = add_file_num(name, target_dir) # 중복 체크
    path = os.path.join(target_dir, name)

    with open(path, "w", encoding="utf8"):
        pass

    test_time = 1772990348.1234567 # float는 소수점 7자리까지만
    os.utime(path, (test_time, test_time)) # float가 들어감

    result_time = os.stat(path).st_mtime
    # 2초 반올림 
    if result_time == _filter_mtime_subsecond(test_time):
        _filter = _filter_mtime_subsecond
    # 소수점 제거
    elif result_time == _filter_mtime_int(test_time):
        _filter = _filter_mtime_int
    # 동일 (동일한 타입의 드라이브에서 발생)
    elif result_time == test_time:
        _filter = _filter_nothing
    else:
        _filter = _filter_nothing

    os.remove(path) # 테스트 파일 제거


def _filter_mtime_int(t):
    return float(int(t))


def _filter_mtime_subsecond(t):
    """ sub-second 반올림이다. 14.0초면 그대로, 14.1초면 16.0초로 반올림된다. """
    # t는 실수

    if t % 2 != 0: # 14.0초같이 완전한 짝수가 아니라면 
        t = int(t) # 소수점 절삭하고 
        if t % 2 == 0: # 짝수면 2초 올림
            t += 2
        else:           # 홀수면 1초 올림 
            t += 1

    return float(t)


def _filter_nothing(t):
    return t


# 필터 함수 (전역변수)
_filter = _filter_nothing




