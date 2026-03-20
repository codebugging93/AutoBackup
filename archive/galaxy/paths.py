import os.path
pjoin = os.path.join

# 경로 설정
STORAGE = "/storage"
USB_ID = "70AC-6310"
SD_ID = "9016-4EF8"
USB_PATH = pjoin(STORAGE, USB_ID, "폰에서_컴퓨터로")
SD_PATH = pjoin(STORAGE, SD_ID)
INTERNAL = pjoin(STORAGE, "emulated/0")

NOTE8 = "Galaxy Note 8"
J3 = "J3"
DCIM = "DCIM"
RECORDER = "Voice Recorder"
SNOTE = "삼성노트"

NOTE8_DCIM = pjoin(INTERNAL, DCIM), pjoin(USB_PATH, NOTE8, DCIM)
NOTE8_RECORDER = pjoin(INTERNAL, RECORDER), pjoin(USB_PATH, NOTE8, RECORDER)
NOTE8_SNOTE = pjoin(INTERNAL, SNOTE), pjoin(USB_PATH, NOTE8, SNOTE)

J3_PATHS = pjoin(SD_PATH, J3), pjoin(USB_PATH, J3)

RESULT_PATH = os.path.normpath("result")