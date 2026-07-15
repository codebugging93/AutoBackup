from system.depth import get_depth
import os
from system.path import norm_max_path 
p = r"D:\Projects\Wynncraft-Spell-Caster-2.2.8SpellCaster-2.2.8\.gradle\loom-cache\minecraftMaven\net\minecraft\minecraft-merged-fc109cbca2\1.21.11-net.fabricmc.yarn.1_21_11.1.21.11+build.3-v2\minecraft-merged-fc109cbca2-1.21.11-net.fabricmc.yarn.1_21_11.1.21.11+build.3-v2.jar"
print(os.path.exists(p))
p = norm_max_path(p)
print(p)
print(get_depth(p))

# for i in range(5):
#     p = norm_max_path(p)
#     print(os.path.exists(p))

p = r"\\?\E:\test_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_xtest_x\.gradle\loom-cache\minecraftMaven\net\minecraft"
for root, _, _ in os.walk(p):
    print(root)
