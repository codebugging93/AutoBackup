from system.DepthList import DepthList
from system.DepthList import get_depth
import os


class Folder:
    """
    폴더의 여러 정보를 저장한다.
    path, depth만 빼고 리셋
    """

    def __init__(self, tag):
        self.tag = tag
        self.path = ""
        self.depth = 0  # 경로의 깊이;슬래시 개수
        self.tree = DepthList()  # 폴더 Depth별 경로 모음
        self.folders = 0  # 폴더 수
        self.files = 0  # 파일 수
        self.size = 0  # 폴더 크기


    def reset(self):
        self.tree.clear()
        self.folders = 0
        self.files = 0
        self.size = 0


    def assign(self, path):
        self.path = os.path.normpath(path)
        self.depth = get_depth(path)


