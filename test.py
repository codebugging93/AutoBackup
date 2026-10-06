# from system.compare import compare



# r = compare(a, b)
# r.cache


import stat

from system.compare import compare
from system.path import ListdirSplitResult, get_listdir_split 

a = "c:\\"
b = "f:\\"

c = compare(a, b, root_only=True, skip_hidden=False)
input()

"""
검사할 폴더 : Programs 
복사할 폴더 : Projects, Studying, WorkSpace, 내 파일, 씹덕, 아카이브 
삭제할 폴더 : 현재 없음
화면에 이 3가지 요소를 모두 표시해야함

복사할 항목 (6개):
    Projects
    Studying
    WorkSpace
    내 파일
    씹덕
    아카이브 
    복사할 파일 M개 

검사할 항목 (1개)
    Programs
    검사할 파일 I개 

삭제할 항목
    삭제할 파일 N개

폴더 선택을 하고 나서 다음 페이지로 넘어가면 기존은 빠른검사/정밀검사창이 떴지만
이제부터는 그 창을 폴더 선택창으로 할 생각이다.



"""

