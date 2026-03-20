import os


word = input()




for mode in ("utils", "implemented", "TKgui", "galaxy", "galaxy_deprecated", "new_TKgui"):



    cur = os.path.dirname(__file__)
    path = os.path.join(cur, mode)
    
    
    for i in os.listdir(path):
        if i.find(".py") != -1:
            p = os.path.join(path, i)
            
            with open(p, "r", encoding="utf8") as file:
                lines = file.readlines()
                k = 0
                temp = []
                for l in lines:
                    k += 1
                    if l.find(word) != -1:
                        temp.append(f"{k} {l}")
                        
                if len(temp) != 0:
                    print("___________________")
                    print(f"[{mode}.{i}]")
                    for t in temp:
                        print(t)
                               
                