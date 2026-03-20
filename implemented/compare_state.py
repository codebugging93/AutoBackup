from implemented.DepthList import is_trees_equal, DepthList
from implemented.main_datas import backup_data, original, target
from utils.constants import CMP_STATS



def get_state(tree_same: DepthList):
    """
    original, target의 트리를 
    data.tree_same에 의존하여 비교 상태를 얻는다.
    1. original이나 target의 트리가 비어있는 경우
    2. data.tree_same이 비어있는 경우
    이 두가지 경우에선 반드시 불일치하는 결과가 나온다.
    """
    state = _get_state_between_trees(
        original.tree, 
        target.tree, 
        tree_same
        )
    return state
    

def get_state_str(state):
    if state == CMP_STATS.SAME:
        msg = "완전 일치"
    elif state == CMP_STATS.NOTSAME:
        msg = "불일치"
    elif state == CMP_STATS.PARTIAL:
        msg = "부분 일치"
    elif state == CMP_STATS.ROOT:
        msg = "단일 폴더"
    else:
        msg = "(ERROR; CMP_STATS에 없는 값이 state에 할당되어있음)"
        
    return "폴더 구조 : " + msg


def _get_state_between_trees(tree1, tree2, sametree):
    # 트리 비교
    folders = sametree.num
    result = is_trees_equal(tree1, tree2, sametree)

    # 비교 알고리즘 참고
    if result:
        return CMP_STATS.SAME
    elif folders == 1:
        return CMP_STATS.NOTSAME
    else:
        return CMP_STATS.PARTIAL

