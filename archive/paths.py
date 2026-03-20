import os
pjoin = os.path.join

# 경로 설정
NAMES = [
    "DCIM",
    "Documents",
    "Recordings",
    "Virtual Partition",
    "노트",
]

STORAGE = "/storage/emulated/0"

EXT_STORAGE = "/mnt/media_rw"
USB_ID = "64A5-F009"
S23U = "Suisei Galaxy S23 Ultra"

USB_PATH = pjoin(EXT_STORAGE, USB_ID, "폰에서_컴퓨터로", S23U)


paths = [

]
for i in NAMES:
    org_path = pjoin(STORAGE, i)
    tar_path = pjoin(USB_PATH, i)
    paths.append((org_path, tar_path))

