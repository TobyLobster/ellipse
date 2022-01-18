## Drawing Ellipses With Fewer Straight Lines

See this code running [here](http://bbc.godbolt.org/?autoboot&disc=https://raw.githubusercontent.com/TobyLobster/ellipse/diagonals/ELLIPS2.SSD).

To reduce the number of straight lines being drawn while retaining the pixel perfect ellipse shape we pre-calculate a static tree structure that encodes all possible straight line renderings from a fixed starting point. To limit the size of the tree, we limit the length of the lines.

We are attempting to optimise the runtime for drawing an ellipse. We have an algorithm that traces the pixels of an ellipse. Instead of drawing each pixel, we call a new routine.

Starting at the root of the tree, the routine will move a pointer from one node of the tree to one of it's children (if possible) depending on the direction taken. If we run out of tree (the latest direction does not lead to a new child node), then we draw the longest straight line found in the tree so far and continue the process starting at the root of the tree again.

### Making the Tree
In particular, consider a 13x13 grid of pixels with origin at the centre. Coordinates
range from (-6,-6) to (6,6).

We investigate the rendering of each straight line from (0,0) to some other point on
the grid. There are 13x13=169 of these straight lines:

![Straight lines](lines.png)

We encode each pixel move along each line into a tree.

An edge of the tree represents a move in a particular direction from one pixel to the next along a straight line.

### Directions
We represent the directions from a point X to an adjacent pixel by a number 0-8 (The
number four is unused. This is an implementation detail to optimise the speed of the
code):
```
                    678
                    3X5
                    012
```
Figure A - encoding directions

Moving from the root of the tree is in one of eight directions.

However once an initial direction is chosen the straight line then has only three directions it can continue along (since straight lines don't turn 90 degrees):
 - the same initial direction
 - one step clockwise from the initial direction
 - one step anti-clockwise from the initial direction

 For instance, if the straight line starts in direction 0, then each following pixel move for that particular straight line is in one of the three directions (3,0,1) as seen in Figure A.

### Blue and Yellow nodes
Each node in the tree is coloured blue or yellow. If a node in the tree represents the final pixel of a straight line, then we colour it blue. Yellow nodes are the remainder - intermediate nodes part way towards longer line(s).

The resulting tree looks like this:

![Full tree](line_data.png)

The root has eight children, corresponding to the eight directions that can be taken from the first pixel. Each subtree's nodes from this point onwards has at most three children.

By symmetry, we see that only the first three subtrees are unique. The remainder of the subtrees are identical to one of the first three, with suitable reordering of the directions. So we get three subtrees:

![Reduced tree](subtrees3.png)

Where A,B,C are directions determined by the initial direction:

| Initial direction | Subtree Root | A | B | C |
| :---------------: | :----------: | - | - | - |
| 0                 | node 0  		| 3 | 0 | 1 |
| 1                 | node 1  		| 0 | 1 | 2 |
| 2                 | node 2  		| 1 | 2 | 5 |
| 3                 | node 1  		| 0 | 3 | 6 |
| 4                 | node 0  		| - | - | - |
| 5                 | node 0  		| 2 | 5 | 8 |
| 6                 | node 2  		| 3 | 6 | 7 |
| 7                 | node 0  		| 6 | 7 | 8 |
| 8                 | node 1  		| 7 | 8 | 5 |

### Implementation details
A python script (asm/create_table.py) is used to create the tree and output the appropriate data (asm/linedata.a). The runtime code (asm/ellips2.a) is the main file to assemble.

There are 93 nodes in the symmetry reduced tree, so each node can be identified by a single byte.

Each node of the tree stores three children and blue/yellow flag (four bytes total).
For speed, we store these values in four separate arrays of bytes 'child0', 'child1',
'child2', and 'isBlue'. A value of 255 means no child is present.

The root is a special case as is has eight children, which is reduced to three due to symmetry as noted above. We store a mapping from the eight possible initial directions to the root of one of the three unique subtrees. We also store the three possible continuing directions for the subtree for each initial direction.

In the runtime, at each iteration we move from a node to it's child. If we run out of tree (the latest direction does not lead to a new child node), then we (a) draw the longest straight line so far encountered (from the root node to the last blue node we visited), and (b) replay any remaining yellow node moves to the new routine (recursively).

Because our ellipse is drawn in four quadrants, each quadrant has it's own set of state  for traversing the tree.

### Limitations
Different operating systems can render straight lines in slightly different ways. This will affect the data produced. So the data is to some degree OS specific when relying on an OS specific line drawing routine.

### Future Development ###
This technique is not just useful for ellipses, but can be used with any shape that's drawn using adjacent pixels.

#### Optimisations
Large or squashed ellipses can have long sections of purely vertical or horizontal lines. At the moment these lines are encoded into multiple lines of length 7. It is possible to adjust the tree data so that e.g. the child of node along a vertical line can point to it's parent. This turns our tree into a graph that can encode vertical and horizontal lines of any length. Similarly for diagonal (45 degree) lines and perhaps some other regular lines too.

We can coalesce identical parts of the tree to save memory.

We can move the isBlue flag into the top bit of e.g. child0, to save memory.
