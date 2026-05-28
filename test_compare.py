from time import time
from system.aftercheck import aftercheck, aftercheck_dirs_rmv, aftercheck_files_renew, aftercheck_files_rmv, aftercheck_files_copy
from system.compare import compare
from system.backup import backup


a = r"e:\test_a"
b = r"e:\test_b"

while True:
    t = time()
    result = compare(a, b)
    print(time() - t)
    result.print()

    input()

    backup(result)

    failed = aftercheck(result)

    input("백업 완료")
    
    backup(failed)




