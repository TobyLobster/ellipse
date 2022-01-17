# Python3 code to draw lines in a grid as per a BBC Micro, to construct a tree of straight lines

depth = 6
gridWidth = depth*2 + 1
gridHeight = gridWidth
bytesWrittenOnLine = 0

labelArray = {
    0:"(-1,-1)",
    1:"(0,-1)",
    2:"(1,-1)",
    3:"(-1,0)",
    4:"(0,0)",
    5:"(1,0)",
    6:"(-1,1)",
    7:"(0,1)",
    8:"(1,1)",
    }

nodeCounter = 0

#def arr_assign(arr, key, val):
#    try:
#        arr[key] = val
#        return
#    except IndexError:
#        # Do not extend the array for negative indices
#        # That is ridiculously counterintuitive
#        assert key >= 0
#        arr.extend(((key + 1) - len(arr)) * [False])
#        arr[key] = val
#        return

def sign_bit(x):
    if (x < 0):
        return True
    return False

def DirFromDXDY(dx,dy):
    return (dx+1) + 3*(dy+1)

def startWriteByteData():
    global bytesWrittenOnLine

    bytesWrittenOnLine = 0

def writeByteData(byte, f):
    global bytesWrittenOnLine

    if bytesWrittenOnLine == 16:
        f.write('\n')
        bytesWrittenOnLine = 0
    if bytesWrittenOnLine == 0:
        f.write('    !byte ')
    elif bytesWrittenOnLine != 0:
        f.write(",")
    f.write(str(byte))
    bytesWrittenOnLine += 1

def endWriteByteData(f):
    f.write('\n')

def writeBitData(array, f):
    index = 0
    a = 0
    startWriteByteData()
    for x in array:
        if x:
            a += 1
        if index == 7:
            writeByteData(a, f)
            index = 0
            a = 0
        else:
            index += 1
            a *= 2

    # flush remaining bits
    if index != 0:
        writeByteData(a,f)
    endWriteByteData(f)

class Node:
    directionFromParent = -1
    cellIndex = 0
    children = [None, None, None, None, None, None, None, None, None]
    parent = None
    isValidDestination = False
    cx = 0
    cy = 0

    def __init__(self, cellIndex, directionFromParent, cx, cy):
        global nodeCounter

        self.cellIndex = cellIndex
        self.directionFromParent = directionFromParent
        self.nodeIndex = nodeCounter
        self.arrayIndex = -1    # not set
        nodeCounter += 1
        self.children = [None, None, None, None, None, None, None, None, None]
        self.parent = None
        self.cx = cx
        self.cy = cy

    def AddToTree(self, dx, dy, isValidDestination, cx, cy):
        dir = DirFromDXDY(dx,dy)
        if (self.children[dir] == None):
            offset = (dy + 1) * gridWidth + (dx + 1)
            child = Node(self.cellIndex + offset, dir, cx, cy)
            self.children[dir] = child
            child.parent = self

        # record if this is a valid end point for a line
        self.children[dir].isValidDestination |= isValidDestination
        return self.children[dir]

class Grid:
    grid = []

    # For line drawing:
    node = None
    ocx = 0
    ocy = 0

    def __init__(self):
        self.Clear();

    def Clear(self):
        self.grid = []
        for i in range(0,gridWidth * gridHeight):
            self.grid.append(False)

    def Show(self):
        result = ""
        index = 0
        for y in range(0,gridHeight):
            for x in range(0,gridWidth):
                if self.grid[index]:
                    result += '#'
                else:
                    result += '.'
                index += 1
            result += '\n'
        result += '\n'
        return result

    # For drawing straight lines as per the BBC Micro
    def DrawLine(self, x1,y1,x2,y2, debug):

        # Calculate deltas
        dX=x1-x2
        dY=y1-y2
        if sign_bit(dX) == sign_bit(dY):
            increment = 1
        else:
            increment = -1

        # Find dominant axis
        dominant_axis_is_Y = abs(dX) < abs(dY)

        # Set the first point (cx and cy) and last point (tx and ty):
        if dominant_axis_is_Y:
            reverse = (dY > 0)
        else:
            reverse = (dX > 0)

        if reverse:
            cx = x2
            cy = y2
        else:
            cx = x1
            cy = y1

        # Initialise variables including the the step counter, and the error term
        if dominant_axis_is_Y:
            dDomAxis = dY
            dNonDomAxis = dX
        else:
            dDomAxis = dX
            dNonDomAxis = dY

        dDomAxis    = abs(dDomAxis)
        dNonDomAxis = abs(dNonDomAxis)
        steps       = -dDomAxis-1
        error       = dDomAxis // 2

        self.node = root
        pointList = []
        done = False
        while not done:
            pointList.append((cx, cy))

            error -= dNonDomAxis
            if error < 0:
                error=error + dDomAxis

                # update non-dominant axis
                if dominant_axis_is_Y:
                    cx += increment
                else:
                    cy += increment

            # update dominant axis
            if dominant_axis_is_Y:
                cy += 1
            else:
                cx += 1

            steps += 1
            done = steps == 0

        # reverse points if necessary, to get the points in the proper order
        if reverse:
            pointList.reverse()

        index = 0
        (fx, fy) = pointList[0]
        for (cx,cy) in pointList:
            isFirstPoint = index == 0
            isFinalPoint = index == len(pointList)-1

            self.RecordPoint(cx-fx, cy-fy, isFirstPoint, isFinalPoint)
            self.grid[cx + gridWidth*cy] = True
            index += 1

    def RecordPoint(self, cx, cy, isFirst, isValidDestination):
        if not isFirst:
            dx = cx - self.ocx
            dy = cy - self.ocy
            self.node = self.node.AddToTree(dx,dy, isValidDestination, cx, cy)
        self.ocx = cx
        self.ocy = cy

    # Output the tree to a ".dot" file
    def DrawTree(self, dotFile):
        centreX = gridWidth//2
        centreY = gridHeight//2
        centre = str(centreX) + "," + str(centreY)
        totalLines = str(gridWidth*gridHeight)

        dotFile.write("digraph tree {")
        dotFile.write("    graph [labelloc=\"b\" labeljust=\"l\" label=\"\lGiven a " + str(gridWidth) + "x" + str(gridHeight) + " grid of pixels, we consider all " + totalLines + " straight lines that can be drawn from the origin (0,0) at the centre of the grid to each pixel in the grid. We construct a tree.\lEach blue node represents a straight line that can be drawn from the origin by following the (dx,dy) moves along each edge. Note that there are " + totalLines + " blue nodes.\lThe yellow nodes are intermediate nodes that need to be traversed in the hope of reaching a blue node further down the tree.\lEach node is labelled 'node N at (X,Y)' where N is a unique index for each node, and (X,Y) are the coordinates of the pixel being visited.\l\"];")

        stack = []

        stack.append(root)
        while stack:
            node = stack.pop()
            nodeLabel = "node " + str(node.arrayIndex) + "\\n at (" + str(node.cx) + "," + str(node.cy) + ")"
            if (node.isValidDestination):
                color = "00BFFF"    # blue
            else:
                color = "F6C85F"    # yellow
            dotFile.write(" node" + str(node.nodeIndex) + " [label=\"" + nodeLabel + "\",fillcolor=\"#" + color + "\",style=filled]")
            line = "    node" + str(node.nodeIndex) + " -> "
            for c in node.children:
                if c != None:
                    label = labelArray.get(c.directionFromParent, "Invalid input")
                    line_end = "node" + str(c.nodeIndex) + " [label=\" " + label + "\" ];"
                    stack.append(c)
                    dotFile.write(line + line_end)
        dotFile.write("}")

class SubTree:
    A = -1
    B = -1
    C = -1
    root = None

    def __init__(self, a,b,c,root):
        self.A = a
        self.B = b
        self.C = c
        self.root = root


centreX = gridWidth // 2
centreY = gridHeight // 2

# Draw all lines, creating a tree of nodes
root = Node(0, 0, 0, 0)

root.isValidDestination = True
pixels = Grid()

pic = ""
for y in range(0,gridHeight):
    line = "\n" * gridHeight
    for x in range(0,gridWidth):
        pixels.Clear()
        pixels.DrawLine(centreX,centreY,x,y,False)
        onePic = pixels.Show()

        newLine = ""
        for myx,myy in zip(line.splitlines(),onePic.splitlines()):
            newLine += myx + " " + myy + '\n'
        line = newLine

    pic += line + "\n"

# Mirror vertically for the correct orientation...
lines = pic.split("\n")
pic = "\n".join(lines[::-1])

print(pic)

# Renumber nodes in breadth first search order
queue = [root]
index = 0
while queue:
    node = queue[0]
    queue = queue[1:]
    node.nodeIndex = index
    for c in node.children:
        if c:
            queue.append(c)
    index += 1

# Create subtrees
subTrees = []

for subRoot in root.children:
    if subRoot:
        subRoot.parent = None
        childIndexes = []
        for i in range(0,9):
            if subRoot.children[i]:
                direction = subRoot.children.index(subRoot.children[i])
                childIndexes.append(direction)

        # Three directions are possible: A,B,C
        subTrees.append(SubTree(childIndexes[0],childIndexes[1],childIndexes[2],subRoot))

# Set the children of each node to be in the A,B,C node order
for subTree in subTrees:
    stack = [subTree.root]
    while stack:
        node = stack.pop()
        node.children = [node.children[subTree.A], node.children[subTree.B], node.children[subTree.C]]
        for c in node.children:
            if c:
                stack.append(c)

# Re-order children of subTrees[0] for symmetry
temp = subTrees[0].A
subTrees[0].A = subTrees[0].C
subTrees[0].C = subTrees[0].B
subTrees[0].B = temp

# reorder children
stack = [subTrees[0].root]
while stack:
    node = stack.pop()
    node.children = [node.children[2], node.children[0], node.children[1]]
    for c in node.children:
        if c:
            stack.append(c)

# Re-order children of subTrees[7] for symmetry
for i in range(0,2):
    temp = subTrees[7].A
    subTrees[7].A = subTrees[7].C
    subTrees[7].C = subTrees[7].B
    subTrees[7].B = temp

    stack = [subTrees[7].root]
    while stack:
        node = stack.pop()
        node.children = [node.children[2], node.children[0], node.children[1]]
        for c in node.children:
            if c:
                stack.append(c)

# Show directions for each subtree
#for subTree in subTrees:
#    print(vars(subTree))

# Initialise array indexes
nodeArray = []
queue = []
for subTree in subTrees:
    # Set array index of each node (in breadth first search order)
    queue.append(subTree.root)

i = 0
while queue:
    node = queue[0]
    queue = queue[1:]
    nodeArray.append(node)
    node.arrayIndex = i
    i += 1
    for c in node.children:
        if c:
            queue.append(c)



# Output tree
with open('build/line_data.dot', 'w') as dotFile:
    pixels.DrawTree(dotFile)

# Just keep the first three subtrees
threeSubTrees = subTrees[0:3]

# write first ASM file (storing the data in bits)
#with open('asm/oldlinedata.a', 'w') as f:
#    f.write('isBlueArray\n')
#    f.write('   !word treeDataIsBlue0\n')
#    f.write('   !word treeDataIsBlue1\n')
#    f.write('   !word treeDataIsBlue2\n')
#    f.write('   !word treeDataIsBlue1\n')
#    f.write('   !word treeDataIsBlue0\n')
#    f.write('   !word treeDataIsBlue2\n')
#    f.write('   !word treeDataIsBlue0\n')
#    f.write('   !word treeDataIsBlue1\n')
#
#    f.write('isValidArray\n')
#    f.write('   !word treeDataIsValid0\n')
#    f.write('   !word treeDataIsValid1\n')
#    f.write('   !word treeDataIsValid2\n')
#    f.write('   !word treeDataIsValid1\n')
#    f.write('   !word treeDataIsValid0\n')
#    f.write('   !word treeDataIsValid2\n')
#    f.write('   !word treeDataIsValid0\n')
#    f.write('   !word treeDataIsValid1\n\n')
#
#    f.write('directions\n')
#    for subTree in subTrees:
#        f.write('   !byte ' + str(subTree.A) + ',' + str(subTree.B) + ',' + str(subTree.C) + '\n')
#
#    f.write('\n')
#
#    # Count the number of nodes, the sum of 3^n (from n=0 to 5)
#    subTreeIndex = 0
#    count = 0
#    for i in range(1,6):
#        count += 3**i
#
#    for subTree in threeSubTrees:
#        isBlue = [False] * count
#        isValid = [False] * count
#
#        # Set array index of each node (in breadth first search order)
#        queue = [subTree.root]
#        while queue:
#            node = queue[0]
#            queue = queue[1:]
#            if node.arrayIndex < 0:
#                if node.parent:
#                    arrayIndex = node.parent.arrayIndex
#                    if arrayIndex < 0:
#                        arrayIndex = 0
#                    children = [c for c in node.parent.children if c]
#                    node.arrayIndex = arrayIndex*3 + 1 + children.index(node)
#                    arr_assign(isBlue, node.arrayIndex, node.isValidDestination)
#                    arr_assign(isValid, node.arrayIndex, True)
#                else:
#                    node.arrayIndex = 0
#            for c in node.children:
#                if c:
#                    queue.append(c)
#
#        f.write('treeDataIsBlue' + str(subTreeIndex) + '\n')
#        writeBitData(isBlue, f)
#        f.write('treeDataIsValid' + str(subTreeIndex) + '\n')
#        writeBitData(isValid, f)
#
#        subTreeIndex += 1

# Set array index of each node (in breadth first search order)
nodeArray = []
queue = [threeSubTrees[0].root, threeSubTrees[1].root, threeSubTrees[2].root]
i = 0
while queue:
    node = queue[0]
    queue = queue[1:]
    nodeArray.append(node)
    node.arrayIndex = i
    i += 1
    for c in node.children:
        if c:
            queue.append(c)

# write second ASM file (storing the data in bytes)
with open('asm/linedata.a', 'w') as f:
    f.write("; Data encoding a tree.\n")
    f.write(";\n")
    f.write("; Consider a 13x13 grid of pixels with origin at the centre having coordinates from\n")
    f.write("; (-6,-6) to (6,6).\n")
    f.write("; We investigate the rendering of each straight line from (0,0) to some other point on \n")
    f.write("; the grid. There are 13x13=169 of these straight lines.\n")
    f.write(";\n")
    f.write("; We encode every pixel move along each line into a single tree.\n")
    f.write(";\n")
    f.write("; An edge of the tree represents a move from one pixel to the next along a straight line.\n")
    f.write("\n")
    f.write("; Encoding Directions:\n")
    f.write("; We represent the directions from a point X to an adjacent pixel by a number 0-8 (The\n")
    f.write("; number four is unused. This is an implementation detail to optimise the speed of the\n")
    f.write("; code):\n")
    f.write(";\n")
    f.write(";             678\n")
    f.write(";             3X5\n")
    f.write(";             012\n")
    f.write("; Figure A - encoding directions\n")
    f.write(";\n")
    f.write("; Moving from the root of the tree to the first level is in one of eight directions.\n")
    f.write("; With an initial direction chosen, the straight line then has only three directions\n")
    f.write("; for the remainder of the pixels along it's length, since straight lines don't turn 90\n")
    f.write("; degrees or more. For instance, if the straight line starts in direction 0, then the\n")
    f.write("; each following pixel move for that straight line is in one of the three directions\n")
    f.write("; (3,0,1) - see Figure A.\n")
    f.write("\n")
    f.write("; Nodes:\n")
    f.write("; There are 93 nodes in the tree, so each node can be specified by a single byte (0-92).\n")
    f.write(";\n")
    f.write("; Each node of the tree stores up to three children and blue/yellow flag (four bytes total).\n")
    f.write("; For speed, we store these values in four separate arrays of bytes 'child0', 'child1',\n")
    f.write("; 'child2', and 'isBlue' in the data below. A value of 255 represents no edge present.\n")
    f.write(";\n")
    f.write("; Each node is 'blue' or 'yellow':\n")
    f.write(";\n")
    f.write("; A 'blue' node represents the end of a straight line rendering from the origin.\n")
    f.write("; There are 13x13=169 blue nodes.\n")
    f.write("; 'Yellow' nodes are the remainder - intermediate nodes part way towards longer line(s).\n")
    f.write("\n")

    f.write("; Child nodes of the root:\n")
    f.write("; The root of the tree has nine children, one for each direction, but direction four is\n")
    f.write("; unused so really only eight directions. This number is reduced further to three due to\n")
    f.write("; symmetry. Hence only the values 0,1,2 are found in the 'rootChildren' table.\n")
    f.write("; The numbers are indices into the arrays 'child0', 'child1', 'child2', and 'isBlue' below.\n")
    f.write("rootChildren\n")
    f.write("   !byte 0,1,2,1,0,0,2,0,1\n")
    f.write("\n")
    f.write("; These arrays store the possible future directions of a straight line given an initial\n")
    f.write("; direction as index, e.g. initial direction 0 (i.e. index 0) has possible\n")
    f.write("; future directions (3,0,1) stored in the three arrays below.\n")
    f.write('direction0\n')
    subTreeIndex = 0
    f.write('   !byte ')
    for subTree in subTrees:
        if subTreeIndex != 0:
            f.write(',')
        f.write(str(subTree.A))
        if subTreeIndex == 3:
            f.write(',4')
        subTreeIndex += 1
    f.write('\n')

    f.write('direction1\n')
    subTreeIndex = 0
    f.write('   !byte ')
    for subTree in subTrees:
        if subTreeIndex != 0:
            f.write(',')
        f.write(str(subTree.B))
        if subTreeIndex == 3:
            f.write(',4')
        subTreeIndex += 1
    f.write('\n')

    f.write('direction2\n')
    subTreeIndex = 0
    f.write('   !byte ')
    for subTree in subTrees:
        if subTreeIndex != 0:
            f.write(',')
        f.write(str(subTree.C))
        if subTreeIndex == 3:
            f.write(',4')
        subTreeIndex += 1
    f.write('\n\n')

    f.write("; Each node below the root node is stored in the following arrays.\n")
    f.write("; Each node is specified by an index into these arrays, and each node stores a value for\n")
    f.write("; up to three children (each of these values also being an index) and an isBlue flag\n")
    f.write("; stored in the top bit.\n")
    for i in range(0,3):
        f.write('child' + str(i) + '\n')
        startWriteByteData()
        for node in nodeArray:
            if node.children[i]:
                myIndex = nodeArray.index(node.children[i])
            else:
                myIndex = 255
            writeByteData(myIndex, f)
        endWriteByteData(f)

    f.write('isBlue\n')
    startWriteByteData()
    for node in nodeArray:
        myIndex = 0
        if node.isValidDestination:
            myIndex = 128
        writeByteData(myIndex, f)
    endWriteByteData(f)

# OLD CODE:

# Go to child: Multiply by three and add A=1,2,3:
#    clc
#    adc offset
#    adc offset
#    adc offset
#    sta offset

# go to parent = Divide A by three
#    sta temp
#    lsr
#    adc #21
#    lsr
#    adc temp
#    ror
#    lsr
#    adc temp
#    ror
#    lsr
#    adc temp
#    ror
#    lsr

# get bit from bit array offset in A
#    sta temp
#    lsr
#    lsr
#    lsr
#    tax
#    lda temp
#    and #7
#    tay
#    lda table,X
#    and bitset,Y

#                                            0
#                                           /|\
#                                          / | \
#                                         /  |  \
#                                        /   |   \
#                                       /    |    \
#                                      /     |     \
#                                     /      |      \
#                                    /       |       \
#                                   /        |        \
#                                  /         |         \
#                                 /          |          \
#                                /           |           \
#                               /            |            \
#                              /             |             \
#                             /              |              \
#                            /               |               \
#                           /                |                \
#                          /                 |                 \
#                         /                  |                  \
#                        /                   |                   \
#                       /                    |                    \
#                      /                     |                     \
#                     /                      |                      \
#                    /                       |                       \
#                   /                        |                        \
#                  /                         |                         \
#                 /                          |                          \
#                1                           2                           3
#               /|\                         /|\                         /|\
#              / | \                       / | \                       / | \
#             /  |  \                     /  |  \                     /  |  \
#            /   |   \                   /   |   \                   /   |   \
#           /    |    \                 /    |    \                 /    |    \
#          /     |     \               /     |     \               /     |     \
#         /      |      \             /      |      \             /      |      \
#        /       |       \           /       |       \           /       |       \
#       4        5        6         7        8        9        10       11       12
#      /|\      /|\      /|\       /|\      /|\      /|\       /|\      /|\      /|\
#     / | \    / | \    / | \     / | \    / | \    / | \     / | \    / | \    / | \
#   13 14 15 16 17 18 19 20 21  22 23 24 25 26 27 28 29 30  31 32 33 34 35 36 37 38 39
#
# 3^0=1
# 3^1=3
# 3^2=9
# 3^3=27
# 3^3=81
# 3^4=243
#
# Layers start at offsets 0,1,4,13,40,121
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################


