# Python3 code to draw lines in a grid as per a BBC Micro, to construct a tree of straight lines

import constants
import asm_writer
import grid
import dot_writer
import subgraph
from node import *

def CreateSubgraphs(root):
    # Create eight subgraphs (initially they are trees), one for each child of the root
    subgraphs = []
    for child in root.children:
        if child:
            childIndexes = []
            for i in range(0,9):
                if child.children[i]:
                    direction = i
                    childIndexes.append(direction)

            # Three directions are possible: A,B,C
            subgraphs.append(subgraph.SubGraph(childIndexes[0], childIndexes[1], childIndexes[2], child))

    # Up to this point 'node.children' has been an array of nine possible child nodes in each direction.
    # We change the meaning of 'node.children' to be the three possible children of the node in directions A,B,C within the subgraph
    # For each subgraph, set the children of each node to be in the A,B,C node order
    for graph in subgraphs:
        stack = [graph.root]
        while stack:
            node = stack.pop()
            node.children = [node.children[graph.A], node.children[graph.B], node.children[graph.C]]
            for child in node.children:
                if child:
                    stack.append(child)
    return subgraphs

def ReorderForSymmetry(subgraphs):
    # Re-order children of subgraphs[0] for symmetry
    temp = subgraphs[0].A
    subgraphs[0].A = subgraphs[0].C
    subgraphs[0].C = subgraphs[0].B
    subgraphs[0].B = temp

    # reorder children
    stack = [subgraphs[0].root]
    while stack:
        node = stack.pop()
        node.children = [node.children[2], node.children[0], node.children[1]]
        for child in node.children:
            if child:
                stack.append(child)

    # Re-order children of subgraphs[7] for symmetry
    for i in range(0,2):    # twice
        temp = subgraphs[7].A
        subgraphs[7].A = subgraphs[7].C
        subgraphs[7].C = subgraphs[7].B
        subgraphs[7].B = temp

        stack = [subgraphs[7].root]
        while stack:
            node = stack.pop()
            node.children = [node.children[2], node.children[0], node.children[1]]
            for child in node.children:
                if child:
                    stack.append(child)
    return subgraphs

def CreateNodeArrayFromSubgraphs(subgraphs):
    nodeArray = []
    queue = []
    for graph in subgraphs:
        # add each graph's root to the queue
        queue.append(graph.root)

    while queue:
        node = queue[0]
        queue = queue[1:]
        nodeArray.append(node)
        for child in node.children:
            if child:
                queue.append(child)

    # Number all nodes in array order
    i = 0
    for node in nodeArray:
        node.nodeIndex = i
        i += 1

    return nodeArray

# Create the root of a new tree
root = Node(0, 0, 0, 0)
root.isValidDestination = True

# Render all straight lines, adding nodes to the tree as we go
pixels = grid.Grid(root)
pixels.DrawAllLines(root, True)

# Number all nodes in breadth first search order
Node.SetNodeIndices([root])

# Output tree
with open('build/line_data.dot', 'w') as dotFile:
    dot_writer.DrawTree(dotFile, root)

# Create graphs (initially they are trees) from the children of the root
subgraphs = CreateSubgraphs(root)

# Make sure the directions are in a nice symmetrical order
subgraphs = ReorderForSymmetry(subgraphs)

# Create nodearray from subgraphs
nodeArray = CreateNodeArrayFromSubgraphs(subgraphs)

with open('build/subgraphs.dot', 'w') as dotFile:
    dot_writer.DrawSubgraphs(subgraphs, dotFile)

# Just keep the first three subgraphs (the unique ones)
threesubgraphs = subgraphs[0:3]

# Create a node array from the subgraphs in breadth first order
nodeArray = CreateNodeArrayFromSubgraphs(threesubgraphs)

# TODO: Hack away at the tree
# nodeArray[4].children[2] = nodeArray[13]


# Output subgraph dot file
with open('build/subgraphs3.dot', 'w') as dotFile:
    dot_writer.DrawSubgraphs3(threesubgraphs, dotFile)

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
    graphIndex = 0
    f.write('   !byte ')
    for graph in subgraphs:
        if graphIndex != 0:
            f.write(',')
        f.write(str(graph.A))
        if graphIndex == 3:
            f.write(',4')
        graphIndex += 1
    f.write('\n')

    f.write('direction1\n')
    graphIndex = 0
    f.write('   !byte ')
    for graph in subgraphs:
        if graphIndex != 0:
            f.write(',')
        f.write(str(graph.B))
        if graphIndex == 3:
            f.write(',4')
        graphIndex += 1
    f.write('\n')

    f.write('direction2\n')
    graphIndex = 0
    f.write('   !byte ')
    for graph in subgraphs:
        if graphIndex != 0:
            f.write(',')
        f.write(str(graph.C))
        if graphIndex == 3:
            f.write(',4')
        graphIndex += 1
    f.write('\n\n')

    f.write("; Each node below the root node is stored in the following arrays.\n")
    f.write("; Each node is specified by an index into these arrays, and each node stores a value for\n")
    f.write("; up to three children (each of these values also being an index) and an isBlue flag\n")
    f.write("; stored in the top bit.\n")
    for i in range(0,3):
        f.write('child' + str(i) + '\n')
        asm_writer.start()
        for node in nodeArray:
            if node.children[i]:
                myIndex = nodeArray.index(node.children[i])
            else:
                myIndex = 255
            asm_writer.writeByte(myIndex, f)
        asm_writer.end(f)

    f.write('isBlue\n')
    asm_writer.start()
    for node in nodeArray:
        myIndex = 0
        if node.isValidDestination:
            myIndex = 128
        asm_writer.writeByte(myIndex, f)
    asm_writer.end(f)
