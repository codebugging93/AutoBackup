from random import randint, shuffle
from pkg.byte import convert_byte
import os

seed = "abcdefghijklmnopqrstuvwxyz0123456789"

listseed = [i for i in seed]


def generate():
    file = ""
    limit = 1024 ** 2
    while True:
        shuffle(listseed)
        for c in listseed:
            file += c
            if len(file) == limit:
                return file


for i in range(100):
    root = "/storage/emulated/0/Download/A"
    filename = os.path.join(root, f"seed_{i}")
    
    with open(filename, "w", encoding="utf8") as data:
        data.write(generate())
        print(i)




