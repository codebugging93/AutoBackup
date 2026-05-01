from time import time
from system.compare import compare

a = r"e:\test_a"
b = r"e:\test_b"

a = r"g:\test_a"
b = r"g:\test_b"
t = time()
result = compare(a, b)
print(time() - t)

print()