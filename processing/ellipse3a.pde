PGraphics pg;
color yellow = color(255,255, 0);
color red = color(255,0,0);
color green = color(0,192,0);
color white = color(255,255,255);
boolean draw_points = false;

// ************************************************************************************************************
void setup() {
  size(1280, 1024);
  pg = createGraphics(320, 256);
  noSmooth();
}

// ************************************************************************************************************
int sgn(int f) {
  if (f > 0) return 1;
  if (f < 0) return -1;
  return 0;
}

int sign_bit(int f) {
  if (f < 0) return -1;
  return 1;
}

// ************************************************************************************************************
void my_line(PGraphics pg, int x1, int y1, int x2, int y2) {
  // Calculate deltas
  int dX=x1-x2;
  int dY=y1-y2;
  boolean samesign = sign_bit(dX) == sign_bit(dY);

  // Find dominant axis
  boolean dominant_axis_is_Y = abs(dX) < abs(dY);
  
  // Set the first point (cx and cy) and last point (tx and ty):
  boolean reverse;
  if (dominant_axis_is_Y) {
    reverse = dY > 0;
  }
  else {
    reverse = dX > 0;
  }

  int cx, cy;
  if (reverse) {
    cx = x2;
    cy = y2;
  }
  else {
    cx = x1;
    cy = y1;
  }

  // Initialise variables including the the step counter, and the error term
  int dDomAxis, dNonDomAxis; 
  if (dominant_axis_is_Y) {
    dDomAxis = dY;
    dNonDomAxis = dX;
  }
  else {
    dDomAxis = dX;
    dNonDomAxis = dY;
  }

  dDomAxis    = abs(dDomAxis);
  dNonDomAxis = abs(dNonDomAxis);
  int steps   = -dDomAxis-1;
  int error   = dDomAxis / 2;

  boolean done = false;
  
  while (!done) {
    pg.point(cx,cy);
    
    //pointList.add( new Pair<int, int>(cx, cy) );
    error -= dNonDomAxis;
    if (error < 0) {
      error = error + dDomAxis;

      // update non-dominant axis
      if (dominant_axis_is_Y) {
        if (samesign) {
          cx += 1;
        }
        else {
          cx -= 1;
        }
      }
      else {
        if (samesign) {
          cy += 1;
        }
        else {
          cy -= 1;
        }
      }
    }

    // update dominant axis
    if (dominant_axis_is_Y) {
      cy += 1;
    }
    else {
      cx += 1;
    }

    steps += 1;
    done = steps == 0;
  }
}

// ************************************************************************************************************
void draw() {

  pg.beginDraw();
  pg.background(100);
  pg.stroke(255);
/*
  for (int y = 0; y < 13; y++) {
    for (int x = 0; x < 13; x++) {
      int cx=16 + (14*x);
      int cy=16 + (14*y);
      pg.stroke(64);
      pg.fill(64);
      pg.rect(cx-6, cy-6, 12, 12);
      pg.stroke(255);
      my_line(pg, cx,cy, cx+x-6,cy+y-6);
    }
  }
*/
  draw_points = true;
  my_ellipse(160,128,58,100,-20);
  draw_points = false;
  my_ellipse(160,128,58,100,-20);
  pg.endDraw();

  pushMatrix();
  translate(0, 1024); 
  scale(1, -1);   
  image(pg, 0, 0, 1280, 1024);
  popMatrix();

  int x = mouseX / 4;
  int y = (1023 - (mouseY - 1)) / 4;
  textSize(14);
  text("(" + x + "," + y + ")", 10, 25);
  text("line count: " + line_count, 10, 45);
  //text("quad count: " + quad_count, 10, 65);
  //text(quad_details, 10, 85);
}

// ************************************************************************************************************
int cx, cy;
int line_count = 0;
int quad_count = 0;
String quad_details = "";

// ************************************************************************************************************
void my_ellipse(int centrex, int centrey, int a, int b, int s) {
  int bb=b*b;
  int aa=a*a;
  int yyaa=0;
  int aabb=aa*bb;
  int yyaa_diff=aa;

  cx = centrex;
  cy = centrey;
  pg.point(cx,cy);      // DEBUG: centre point
  quad_count = 0;
  line_count = 0;
  quad_details = "";

  depth = 0;

  for(int i = 0; i < 4; i++) {
    state[i] = 0;
    frame[i] = i / 2;
  }

  int x1=-a, t1=-a*b, tt1=aabb, bt1=b*t1, st1=s*t1;
  int x2= a, t2=-t1 , tt2=aabb, bt2=-bt1, st2=-st1;
  int bb2=bb/2, sb=s*b, ss=s*s;

  int ox2 = x2, ox1 = x1;
  for(int y=0; y < b; y++) {
    add_point(pg, 0, x1, y, 7 + sgn(x1-ox1));
    add_point(pg, 1, x2, y, 7 + sgn(x2-ox2)); 
    ox2=x2; ox1=x1;
    int dd=aabb-yyaa;

    // first half
    while (t2<0) { x2+=1; t2+=b; tt2+=2*bt2+bb; bt2+=bb; st2+=sb; }
    while (t2>0) {
      int d1=tt2-dd;
      int bd=bt2+bb2;
      if ((bd-d1)<0) { x2-=1; t2-=b; tt2-=2*bt2-bb; bt2-=bb; st2-=sb; continue; }
      if ((bd+d1)<0) { x2+=1; t2+=b; tt2+=2*bt2+bb; bt2+=bb; st2+=sb; continue; }
      break;
    }
    int inc = sgn(x2-ox2);
    for(int x=ox2 + inc; x!=x2; x+=inc) {
      add_point(pg, 1, x, y, 4+inc);
    }

    // second half
    while (t1>0) { x1-=1; t1-=b; tt1-=2*bt1-bb; bt1-=bb; st1-= sb; } 
    while (t1<0) {
      int d1=tt1-dd;
      int bd=bb2-bt1;
      if ((bd-d1)<0) { x1+=1; t1+=b; tt1+=2*bt1+bb; bt1+=bb; st1+=sb; continue; }
      if ((bd+d1)<0) { x1-=1; t1-=b; tt1-=2*bt1-bb; bt1-=bb; st1-=sb; continue; }
      break;
    }

    inc = sgn(x1-ox1);
    for(int x=ox1 + inc; x!=x1; x+=inc) {
      add_point(pg, 0, x, y, 4+inc);
    }

    tt2+=-2*st2+ss; tt1+=-2*st1+ss; st2-=ss; st1-=ss;
    yyaa+=yyaa_diff;
    yyaa_diff+=2*aa;
    bt2-=sb; bt1-=sb; t2-=s; t1-=s;
  }

  // finish off final lines for the ellipse in each quadrant
  if (!draw_points) {
    for(int i = 0; i < 4; i++) {
      finish_off(pg, cx, cy, i);
    }
  }

  // horizontal lines top and bottom to cap the ellipse
  pg.stroke(white);
  my_line(pg, cx+x1, cy+b, cx+x2, cy+b);
  line_count++;
  my_line(pg, cx-x1, cy-b, cx-x2, cy-b);
  line_count++;
}

// ************************************************************************************************************
void finish_off(PGraphics pg, int cx, int cy, int quadrant) {
  if (state[quadrant] == 0) {
    // nothing to do
    return;
  }

  if((frame[quadrant] & 1) > 0) {
    pg.stroke(yellow);
  }
  else {
    pg.stroke(red);
  }
  // draw line
  my_line(pg, cx + lastMoveX[quadrant], cy + lastMoveY[quadrant], cx + lastBlueX[quadrant], cy + lastBlueY[quadrant]);
  line_count++;

  // draw any remaining points on the stack
  int end = stackptr[quadrant];
  int x = lastBlueX[quadrant];
  int y = lastBlueY[quadrant];
  for(int i = 8*quadrant; i < end; i++) {
    int tempdir = stack[i];
    x += dx[tempdir];
    y += dy[tempdir];
    
    my_line(pg, cx + x, cy + y, cx + x, cy + y);  // draw point!
  }
}

// ************************************************************************************************************
// Data encoding a tree.
//
// Consider a 13x13 grid of pixels with origin at the centre having coordinates from
// (-6,-6) to (6,6).
// We investigate the rendering of each straight line from (0,0) to some other point on 
// the grid. There are 13x13=169 of these straight lines.
//
// We encode every pixel move along each line into a single tree.
//
// An edge of the tree represents a move from one pixel to the next along a straight line.

// Encoding Directions:
// We represent the directions from a point X to an adjacent pixel by a number 0-8 (The
// number four is unused. This is an implementation detail to optimise the speed of the
// code):
//
//             678
//             3X5
//             012
// Figure A - encoding directions
//
// Moving from the root of the tree to the first level is in one of eight directions.
// With an initial direction chosen, the straight line then has only three directions
// for the remainder of the pixels along it's length, since straight lines don't turn 90
// degrees or more. For instance, if the straight line starts in direction 0, then the
// each following pixel move for that straight line is in one of the three directions
// (3,0,1) - see Figure A.

// Nodes:
// There are 93 nodes in the tree, so each node can be specified by a single byte (0-92).
//
// Each node of the tree stores up to three children and a parent (four bytes total).
// For speed, we store these values in four separate arrays of bytes 'child0', 'child1',
// 'child2', and 'parent' in the data below. A value of 255 represents no edge present.
//
// Additionally the top bit of the 'parent' byte specifies whether the node is 'blue' or
// 'yellow' which we now define:
//
// A 'blue' node represents the end of a straight line rendering from the origin.
// There are 13x13=169 blue nodes.
// 'Yellow' nodes are the remainder - intermediate nodes part way towards longer line(s).

// Child nodes of the root:
// The root of the tree has nine children, one for each direction, but direction four is
// unused so really only eight directions. This number is reduced further to three due to
// symmetry. Hence only the values 0,1,2 are found in the 'rootChildren' table.
// The numbers are indices into the arrays 'child0', 'child1', 'child2', and 'parent' below.
int[] rootChildren = { 0,1,2,1,0,0,2,0,1 };

// These arrays store the possible future directions of a straight line given an initial
// direction as index, e.g. initial direction 0 (i.e. index 0) has possible
// future directions (3,0,1) stored in the three arrays below.
int[] direction0 = { 3,0,1,0,4,2,3,6,7 };
int[] direction1 = { 0,1,2,3,4,5,6,7,8 };
int[] direction2 = { 1,2,5,6,4,8,7,8,5 };

// Each node below the root node is stored in the following arrays.
// Each node is specified by an index into these arrays, and each node stores a value for
// up to three children and a parent (each of these values also being an index), 
// with the blue/yellow value stored in the top bit of parent.
int[] child0 = { 
                 3,6,9,255,13,255,255,18,255,255,23,255,27,255,30,255,
                 255,36,255,255,255,255,43,255,46,255,255,255,52,255,255,255,
                 255,255,255,255,255,61,255,255,255,255,255,255,68,255,255,255,
                 255,255,255,75,255,255,255,255,255,255,255,255,255,255,255,255,
                 255,255,255,87,255,255,255,255,255,255,255,255,255,255,255,255,
                 255,255,255,255,255,255,255,255,255,255,255,255,255 
               };
int[] child1 = { 
                 4,7,10,12,14,16,17,19,21,22,24,26,28,29,31,33,
                 34,37,38,39,40,41,44,45,47,48,49,51,255,53,54,55,
                 56,57,255,59,60,255,62,63,64,255,66,67,255,69,70,71,
                 72,255,74,255,76,255,77,78,79,255,80,255,255,82,83,84,
                 85,86,255,255,88,255,89,90,91,92,255,255,255,255,255,255,
                 255,255,255,255,255,255,255,255,255,255,255,255,255 
               };
int[] child2 = { 
                 5,8,11,255,15,255,255,20,255,255,25,255,255,255,32,255,
                 35,255,255,255,255,42,255,255,255,255,50,255,255,255,255,255,
                 255,255,58,255,255,255,255,255,255,65,255,255,255,255,255,255,
                 255,73,255,255,255,255,255,255,255,255,255,81,255,255,255,255,
                 255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
                 255,255,255,255,255,255,255,255,255,255,255,255,255 
               };
int[] parent = { 
                 255,255,255,128,128,128,1,129,1,130,130,2,131,4,132,4, 
                 133,134,7,135,7,136,137,10,138,10,139,140,12,141,14,142,
                 14,143,16,144,17,145,18,147,20,149,21,150,22,151,24,152,
                 25,154,26,155,28,157,30,159,32,161,34,163,164,37,166,167,
                 168,41,170,171,44,173,46,175,176,49,178,179,180,182,183,184,
                 186,187,189,190,191,192,193,195,196,198,199,200,201 
               };

                                     // Size of each entry
int[] state = new int[4];            // 1 byte
int[] treepos = new int[4];          // 1 byte
int[] lastMoveX = new int[4];        // 2 bytes
int[] lastMoveY = new int[4];        // 2 bytes
//int[] lastBlue = new int[4];         // 1 byte
int[] lastBlueX = new int[4];        // 2 bytes
int[] lastBlueY = new int[4];        // 2 bytes
int[] d0 = new int[4];               // 1 byte
int[] d1 = new int[4];               // 1 byte
int[] d2 = new int[4];               // 1 byte
int[] stack = new int[4*8];          // 8 bytes per quadrant
int[] stackptr = new int[4];         // 1 byte

int[] frame = new int[4];

int[] dx = new int[] { -1,  0,  1, -1, 0, 1, -1, 0, 1 };
int[] dy = new int[] { -1, -1, -1,  0, 0, 0,  1, 1, 1 };

// recursion variables
int MAX_DEPTH = 2;

int depth = 0;
int[] end = new int[MAX_DEPTH];
int[] i = new int[MAX_DEPTH];

// ************************************************************************************************************
void add_point(PGraphics pg, int quadrant, int newx, int newy, int dir) {
  add_point_quadrant(pg, quadrant, newx, newy, dir);
  if (newy != 0) {
    add_point_quadrant(pg, 3 - quadrant, -newx, -newy, 8-dir);
  }
}

// ************************************************************************************************************
void add_point_quadrant(PGraphics pg, int quadrant, int newx, int newy, int dir) {
  if(draw_points) {
    pg.stroke(0,0,0);
    pg.point(cx + newx, cy + newy);
    return;
  }
  quad_details += "quad_count: " + quad_count + " quadrant: " + quadrant + " state[q]: " + state[quadrant] + "\n";
  if (quad_count == 31) {
    print();
  }
  quad_count++;

  if (state[quadrant] == 0) {
    state_zero(quadrant, newx, newy);
    return;
  }

  if (state[quadrant] == 1) {
    treepos[quadrant] = rootChildren[dir];
    //lastBlue[quadrant] = treepos[quadrant];
    lastBlueX[quadrant] = newx;
    lastBlueY[quadrant] = newy;
    d0[quadrant] = direction0[dir];
    d1[quadrant] = direction1[dir];
    d2[quadrant] = direction2[dir];
    state[quadrant] = 2;
    return;
  }

  int newpos;
  if (d0[quadrant] == dir) {
    newpos = child0[treepos[quadrant]];
  }
  else if (d1[quadrant] == dir) {
    newpos = child1[treepos[quadrant]];
  }
  else if (d2[quadrant] == dir) {
    newpos = child2[treepos[quadrant]];
  }
  else {
    newpos = 255;
  }
  if (newpos != 255) {
    treepos[quadrant] = newpos;
    if ((parent[newpos] & 128) == 0) {
      // yellow node
      stack[stackptr[quadrant]] = dir;
      stackptr[quadrant]++;
    }
    else {
      // blue node
      stackptr[quadrant] = 8*quadrant;
      lastBlueX[quadrant] = newx;
      lastBlueY[quadrant] = newy;
    }
    return;
  }

  if((frame[quadrant] & 1) > 0) {
    pg.stroke(yellow);
  }
  else {
    pg.stroke(red);
  }
  frame[quadrant]++;
  my_line(pg, cx + lastMoveX[quadrant], cy + lastMoveY[quadrant], cx + lastBlueX[quadrant], cy + lastBlueY[quadrant]);
  line_count++;

  // if node is a yellow node
  if ((parent[treepos[quadrant]] & 128) == 0) {
    // if we run out of tree from a yellow node, repeat the last set of moves

    // Add the current move to stack
    stack[stackptr[quadrant]] = dir;
    stackptr[quadrant]++;
    
    state[quadrant] = 0;
    int rememberx = newx;    // DEBUG
    int remembery = newy;    // DEBUG
    assert(depth < MAX_DEPTH);
    end[depth] = stackptr[quadrant];
    newx = lastBlueX[quadrant];
    newy = lastBlueY[quadrant];
    for(i[depth] = 8*quadrant; i[depth] < end[depth]; i[depth]++) {
      dir = stack[i[depth]];
      newx += dx[dir];
      newy += dy[dir];
      depth++;
      add_point_quadrant(pg, quadrant, newx, newy, dir);
      depth--;
    }
    assert(rememberx == newx);
    assert(remembery == newy);
    return;
  }
  state_zero(quadrant, newx, newy);
}

void state_zero(int quadrant, int newx, int newy) { 
  lastMoveX[quadrant] = newx;
  lastMoveY[quadrant] = newy;
  lastBlueX[quadrant] = newx;
  lastBlueY[quadrant] = newy;
  stackptr[quadrant] = 8*quadrant;
  state[quadrant] = 1;
}
