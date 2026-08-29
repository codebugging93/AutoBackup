from time import time
import os





p = r"D:\WorkSpace\Alarm"
t = time()

for root, _, _ in os.walk(p):
    a = get_dirname_set(root) 
    b = get_dirname_set_faster(root)

    if a != b:
        print("불일치")
        print(a)
        print(b)
        print("-------------")


print(time() - t)