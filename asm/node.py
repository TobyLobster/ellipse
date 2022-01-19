import constants

nodeCounter = 0

def DirFromDXDY(dx,dy):
    return (dx+1) + 3*(dy+1)

class DirChildPair:
    dir = 0
    child = None

    def __init__(self, dir, child):
        self.dir = dir
        self.child = child

class Node:
    cellIndex = 0
    children = [None, None, None, None, None, None, None, None, None]
    isValidDestination = False
    cx = 0
    cy = 0

    def __init__(self, cellIndex, directionFromParent, cx, cy):
        global nodeCounter

        self.cellIndex = cellIndex
        self.directionFromParent = directionFromParent
        self.nodeIndex = nodeCounter
        nodeCounter += 1
        self.children = [None, None, None, None, None, None, None, None, None]
        self.cx = cx
        self.cy = cy

    def AddToTree(self, dx, dy, isValidDestination, cx, cy):
        dir = DirFromDXDY(dx,dy)
        if (self.children[dir] == None):
            offset = (dy + 1) * constants.gridWidth + (dx + 1)
            child = Node(self.cellIndex + offset, dir, cx, cy)
            self.children[dir] = child

        # record if this is a valid end point for a line
        self.children[dir].isValidDestination |= isValidDestination
        return self.children[dir]

    def SetNodeIndices(rootList):
        # Set the node index of each node in this tree in breadth first search order
        queue = rootList
        index = 0
        while queue:
            node = queue[0]
            queue = queue[1:]
            node.nodeIndex = index
            for child in node.children:
                if child:
                    queue.append(child)
            index += 1

    def __str__(self):
        children = []
        for child in self.children:
            if child:
                children.append(child.nodeIndex)
        return f'Node {self.nodeIndex} at ({self.cx},{self.cy}) with children {children}'
