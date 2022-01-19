from node import *

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

def WriteLine(file, line):
    file.write(line + "\n")

# Output the tree to a ".dot" file
def DrawTree(dotFile, root):
    totalLines = str(constants.gridWidth * constants.gridHeight)

    WriteLine(dotFile, "digraph tree {")
    WriteLine(dotFile, "    graph [labelloc=\"b\" labeljust=\"l\" label=\"\lGiven a " + str(constants.gridWidth) + "x" + str(constants.gridHeight) + " grid of pixels, we consider all " + totalLines + " straight lines that can be drawn from the origin (0,0) at the centre of the grid to each pixel in the grid. We construct a tree.\lEach blue node represents a straight line that can be drawn from the origin by following the (dx,dy) moves along each edge. Note that there are " + totalLines + " blue nodes.\lThe yellow nodes are intermediate nodes that need to be traversed in the hope of reaching a blue node further down the tree.\lEach node is labelled 'node N at (X,Y)' where N is a unique index for each node, and (X,Y) are the coordinates of the pixel being visited.\l\"];")

    stack = []

    stack.append(root)
    while stack:
        node = stack.pop()
        nodeLabel = "node " + str(node.nodeIndex) + "\\n at (" + str(node.cx) + "," + str(node.cy) + ")"
        if (node.isValidDestination):
            color = "00BFFF"    # blue
        else:
            color = "F6C85F"    # yellow
        WriteLine(dotFile, " node" + str(node.nodeIndex) + " [label=\"" + nodeLabel + "\",fillcolor=\"#" + color + "\",style=filled]")
        line = "    node" + str(node.nodeIndex) + " -> "

        # At this point, node.children has nine entries for each possible direction
        for child in node.children:
            if child:
                dir = node.children.index(child)
                label = labelArray.get(dir, "Invalid input")
                line_end = "node" + str(child.nodeIndex) + " [label=\" " + label + "\" ];"
                stack.append(child)
                WriteLine(dotFile, line + line_end)
    WriteLine(dotFile, "}")

def DrawSubgraphs(subTrees, dotFile):
    WriteLine(dotFile, "digraph tree {")

    stack = []

    for subTree in subTrees:
        stack.append(subTree.root)
        while stack:
            node = stack.pop()
            nodeLabel = "node " + str(node.nodeIndex) + "\\n at (" + str(node.cx) + "," + str(node.cy) + ")"
            if (node.isValidDestination):
                color = "00BFFF"    # blue
            else:
                color = "F6C85F"    # yellow
            WriteLine(dotFile, " node" + str(node.nodeIndex) + " [label=\"" + nodeLabel + "\",fillcolor=\"#" + color + "\",style=filled]")
            line = "    node" + str(node.nodeIndex) + " -> "

            # At this point, node.children has just three children in directions A,B,C
            indexABC = 0
            for child in node.children:
                if child:
                    if indexABC == 0:
                        dir = subTree.A
                    elif indexABC == 1:
                        dir = subTree.B
                    elif indexABC == 2:
                        dir = subTree.C
                    else:
                        print("oops#2")
                        exit(1)
                    label = labelArray.get(dir, "Invalid input")
                    line_end = "node" + str(child.nodeIndex) + " [label=\" " + label + "\" ];"
                    stack.append(child)
                    WriteLine(dotFile, line + line_end)
                indexABC += 1
    WriteLine(dotFile, "}")

def DrawSubgraphs3(subTrees, dotFile):
    WriteLine(dotFile, "digraph tree {")

    stack = []

    for subTree in subTrees:
        stack.append(subTree.root)
        while stack:
            node = stack.pop()
            nodeLabel = "node " + str(node.nodeIndex)
            if (node.isValidDestination):
                color = "00BFFF"    # blue
            else:
                color = "F6C85F"    # yellow
            WriteLine(dotFile, " node" + str(node.nodeIndex) + " [label=\"" + nodeLabel + "\",fillcolor=\"#" + color + "\",style=filled]")
            line = "    node" + str(node.nodeIndex) + " -> "
            foundChildIndex = 0
#            print("Children {")

            # At this point, node.children has just three children in directions A,B,C
            indexABC = 0
            for child in node.children:
                if child:
#                    print("dir: " + str(dir))
#                    print("subTree.A: " + str(subTree.A))
#                    print("subTree.B: " + str(subTree.B))
#                    print("subTree.C: " + str(subTree.C))
#                    print("usedDir: " + str(usedDir))
                    label = "ABC"[indexABC]
                    line_end = "node" + str(child.nodeIndex) + " [label=\" " + label + "\" ];"
                    stack.append(child)
                    WriteLine(dotFile, line + line_end)
                    foundChildIndex += 1
                indexABC += 1
#            print("} //Children")
    WriteLine(dotFile, "}")
