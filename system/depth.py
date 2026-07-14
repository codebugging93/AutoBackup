""" 
DepthList라는 새로운 자료형을 정의해 놓았다.

depth의 정의는 get_depth 함수를 참고하라.
"""
from pathlib import Path



#########################
# depth에 관한 기본적인 정의
#########################
class DepthError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"depth는 음수일 수 없음 : {self.value}"


def split_path(path_string) -> list:
    """
    경로를 경로 구분자를 기준으로 쪼개어 리스트로 저장
    복호화는 Path(*path_list)

    "/storage/emulated/0/DCIM/abcde.txt"는 
    ['\\', 'storage', 'emulated', '0', 'DCIM', 'abcde.txt']가 됨
    """
    p = Path(path_string)
    return list(p.parts)


def get_depth(path):
    """ 
    A/B/C/D에서 depth = 4
    /A/B/C/D에서 depth = 5

    return len(split_path(path))를 실행할 뿐임.
    그래서 이미 path list가 있을때는 쓰지 말 것.

    * 260자를 넘나드는 경로에서 테스트 완료
    """
    return len(split_path(path))





#########################
# DepthList 정의
#########################
# MAX_DEPTH = 64  # DepthList의 최대 깊이
# class DepthList:
#     """
#     한 폴더의 내용물을 depth에 따라 분류하여 보관하는 리스트.
#     리스트 안에 집합이 MAX_DEPTH개만큼 있으며,

#     경로 추가시에는 add() 메소드로 추가해야만 하며,
#     get_depth() 함수를 사용하여 depth 측정 후 
#     리스트의 N번째 집합에 경로를 넣는 방식으로 분류한다.

#     이외에도 교집합, 차집합 같은 편리한 기능들을 제공한다.
#     """

#     def __init__(self):
#         _list = [set() for i in range(MAX_DEPTH)]
#         self._data = tuple(_list)


#     def __str__(self):
#         return str(self._data)


#     def __len__(self):
#         return len(self._data)
    

#     # 인덱스 기능 정의
#     def __getitem__(self, depth) -> set:
#         if depth < 0:
#             raise DepthError(depth)

#         return self._data[depth]


#     def __iter__(self):
#         self._index = -1
#         return self


#     def __next__(self):
#         try:
#             self._index += 1
#             return self[self._index]
#         except IndexError:
#             raise StopIteration

    
#     def count(self):
#         t = 0
#         for i in self._data:
#             t += len(i)
#         return t


#     # def attach(self, path, depth_to_cut):
#     #     """
#     #     fpath를 depth만큼 cut_path해서 자료에 추가
#     #     depth_to_cut이 0이면 path의 depth 그대로 리스트에 들어간다.
#     #     """
#     #     org_depth = get_depth(path)
#     #     cut = cut_path(path, depth_to_cut)
#     #     cut_depth = org_depth - depth_to_cut

#     #     self[cut_depth].add(cut)


#     def add(self, path):
#         depth = get_depth(path)
#         self[depth].add(path)


#     def clear(self):
#         for i in self._data:
#             i.clear()


#     def flatten(self):
#         """오름차순으로 탐색. dlist의 첫번째 항목부터 차례로 순회한다."""
#         for paths in self:
#             for cut in paths:
#                 yield cut


#     def intersection(self, depth_list):
#         """
#         self와 depth_list에 대하여 depth마다 교집합 진행. (self & another)
#         """
#         new = DepthList()
#         check_length(new, self, depth_list)
        
#         for i in range(MAX_DEPTH):
#             new[i].clear()
#             new[i].update(self[i] & depth_list[i])
#         return new 
    
    
#     def difference(self, depth_list):
#         """
#         self와 depth_list에 대하여 depth마다 차집합 진행. (self - another)
#         """
#         new = DepthList()
#         check_length(new, self, depth_list)
        
#         for i in range(MAX_DEPTH):
#             new[i].clear()
#             new[i].update(self[i] - depth_list[i])
#         return new 
    

# def check_length(*depth_lists):
#     """ 
#     depth_list들의 길이가 일치하는지 체크하고,
#     불일치시 raise Exception("MAX_DEPTH 불일치 에러")
#     """
#     for i in depth_lists:
#         if len(i) != MAX_DEPTH:
#             raise Exception("MAX_DEPTH 불일치 에러")


# def is_dlist_equal(dlist_1, dlist_2, dlist_intersect):
#     """
#     두 트리가 같은지 비교하는데, 교집합을 가지고 있는 경우에 쓸 수 있다.
#     단순 비교보다 훨씬 빠른 비교를 제공한다.
#     """
#     check_length(dlist_1, dlist_2, dlist_intersect)

#     # 세 가지 depthlist들의 각 depth마다 집합이 존재한다.
#     # 집합 A, B, A&B의 길이가 모두 일치하면 A와 B는 같은 집합이다.
#     # 자세한 증명은 archive/비교 알고리즘.txt를 참고
#     for i in range(MAX_DEPTH):
#         l1 = len(dlist_1[i])
#         l2 = len(dlist_2[i])
#         ls = len(dlist_intersect[i])

#         if l1 == l2 == ls:
#             continue
#         else:
#             return False

#     # for문 제대로 탈출
#     return True





"""
사용하지 않는 함수(deprecated)
이 함수는 compare.compare_dirs로 업그레이드 되었다.

def _deprecated_get_samedir_tree(org_path, tar_path):
    
    두 폴더 사이에서 이름이 같은 폴더를 찾아내
    원래 경로와 폴더 경로를 분리한 다음,
    상대 경로 트리로 반환한다.
    

    sametree = DepthList()  # 리턴값
    sametree[0].add("")  # 현재 폴더 추가
    check_list = [""]  # 검사중인 리스트

    while True:  # 같은 폴더 산출
        same_list = []

        # folder는 상대경로
        for folder in check_list:
            # 비교검사하는 곳
            path1 = os.path.join(org_path, folder)
            path2 = os.path.join(tar_path, folder)

            # {path1} & {path2}
            set1 = get_dirname_set(path1)
            set2 = get_dirname_set(path2)
            set3 = set1 & set2

            # 트리에 추가
            for i in set3:
                # 상대경로
                cut = os.path.join(folder, i)

                same_list.append(cut)
                sametree.attach(cut, 0)  # 이미 cut 되었기 때문에 0

                main_prog.num += 1

        # 반복
        if len(same_list) != 0:
            check_list = same_list
        # while문 종료, 리턴
        else:
            return sametree


"""