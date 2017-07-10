

def learn_instance(instance, node, threshold):

    if isSplit(node):
        if check_pruning(node):

    else:
        if node.changeDetector:
            #add alternative subtree
            return 0

    return 0


def is_more_accurate(node1, node2):

    return 0


# decides if the alternative subtree is useless given the alternative subtree's root node and it's corresponding main subtree's root node
def is_probably_useless(mainNode, altNode):
    if isLeaf(altNode):
        return 0
    if splitTest(altNode) == splitTest(mainNode):
        return 1
    return is_more_accurate(mainNode, altNode)


def break_by_complexity():

    return 0


def check_pruning(node):
    if is_more_accurate(getLeaf(node), node):
        return 1
    return 0


def get_prediction_vector():
    return 0


def splitTest(node):

    return 0


def getLeaf(node):
    return 0


def isLeaf(node):
    return 0


def isSplit():
    return 0