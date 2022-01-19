from node import *

class SubGraph:
    A = -1
    B = -1
    C = -1
    root = None

    def __init__(self, a,b,c,root):
        self.A = a
        self.B = b
        self.C = c
        self.root = root
        assert(type(root) is Node)
