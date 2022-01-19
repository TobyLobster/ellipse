import constants
from node import *

def sign_bit(x):
    if (x < 0):
        return True
    return False

class Grid:
    # A grid of pixels to render to
    grid = []

    # For line drawing:
    root = None
    node = None
    ocx = 0
    ocy = 0

    def __init__(self, root):
        self.root = root
        self.node = root
        self.Clear()

    def Clear(self):
        self.grid = []
        for i in range(0,constants.gridWidth * constants.gridHeight):
            self.grid.append(False)

    def Show(self):
        result = ""
        index = 0
        for y in range(0,constants.gridHeight):
            for x in range(0,constants.gridWidth):
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

        self.node = self.root
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
            self.grid[cx + constants.gridWidth*cy] = True
            index += 1

    def RecordPoint(self, cx, cy, isFirst, isValidDestination):
        if not isFirst:
            dx = cx - self.ocx
            dy = cy - self.ocy
            self.node = self.node.AddToTree(dx,dy, isValidDestination, cx, cy)
        self.ocx = cx
        self.ocy = cy

    def DrawAllLines(self, root, show):
        pixels = Grid(root)

        pic = ""
        for y in range(0,constants.gridHeight):
            line = "\n" * constants.gridHeight
            for x in range(0,constants.gridWidth):
                pixels.Clear()
                pixels.DrawLine(constants.centreX,constants.centreY,x,y,False)
                onePic = pixels.Show()

                newLine = ""
                for myx,myy in zip(line.splitlines(),onePic.splitlines()):
                    newLine += myx + " " + myy + '\n'
                line = newLine

            pic += line + "\n"

        # Mirror vertically for the correct orientation...
        lines = pic.split("\n")
        pic = "\n".join(lines[::-1])

        if show:
            print(pic)
