from time import time
from system.compare import compare
from system.backup import backup


a = r"e:\test_a"
b = r"e:\test_b"
# a = r"g:\Studying"
# b = r"g:\Studying-백업본"
# a = r"d:\WorkSpace\Alarm\windows\flutter\ephemeral\.plugin_symlinks"
# b = r"d:\WorkSpace\Alarm\windows\flutter\ephemeral\.plugin_symlinks"
# a = r"d:\Projects"
# b = r"g:\Projects"


# 시간을 단축하려면 os.stat 호출 횟수를 줄여야 한다.

while True:
    t = time()
    result = compare(a, b)
    print(time() - t)
    result.print()

    input()

    # backup(result)

    input("백업 완료")
    




