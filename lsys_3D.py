from math import sin, cos, radians, pi
import numpy as np

class Lsystem:

    def __init__(self):
        self.axiom = "A"
        self.angle = 22.5
        self.length = .05
        self.rules = {
            "A": "[&FL!A]/////’[&FL!A]///////’[&FL!A]",
            "F": "S/////F",
            "S": "FL",
            "L": "[’’’∧∧{-f+f+f-|-f+f+f}]"
        }

    def custom(self, ax, ang, rules, length=.05):
        self.axiom = ax
        self.angle = ang
        self.length = length
        self.rules = rules

    def build_string(self, depth):
        count = depth
        lsys_string = self.axiom
        while count > 0:
            chars = [lsys_string[i:i+1] for i in range(0, len(lsys_string), 1)]
            temp = "";
            for char in chars:
                if char in self.rules:
                    temp = temp + self.rules[char]
                else:
                    temp = temp + char
            lsys_string = temp
            count = count - 1
        return lsys_string

    def rotateX(self, ang):
        return np.array([[cos(ang), sin(ang), 0], \
                         [-1*sin(ang), cos(ang), 0], \
                         [0, 0, 1]])

    def rotateZ(self, ang):
        return np.array([[cos(ang), 0, -1*sin(ang)], \
                         [0, 1, 0], \
                         [sin(ang), 0, cos(ang)]])
    
    def rotateY(self, ang):
        return np.array([[1, 0, 0], \
                         [0, cos(ang), -1*sin(ang)], \
                         [0, sin(ang), cos(ang)]])

    # def rotateX(self, ang):
    #     return np.array([[1, 0, 0], \
    #                      [0, cos(ang), -sin(ang)], \
    #                      [0, 0, 1]])

    # def rotateY(self, ang):
    #     return np.array([[cos(ang), 0, sin(ang)], \
    #                      [0, 1, 0], \
    #                      [-sin(ang), 0, cos(ang)]])
    
    # def rotateZ(self, ang):
    #     return np.array([[cos(ang), -sin(ang), 0], \
    #                      [sin(ang), cos(ang), 0], \
    #                      [0, 0, 1]])

    def construct_points(self, lsys):
        # chars = lsys.split()
        chars = [lsys[i:i+1] for i in range(0, len(lsys), 1)]
        angle = radians(self.angle)
        length = self.length
        stack = []
        bone = []
        factor = 1
        currB = Bone()
        for char in chars:
            if char == 'F':
                # push (curr_loc, changed_loc) to list of lines
                bone.append(currB)
                magDir = [d*length for d in currB.dir]
                newPos = [0,0,0]
                for i in range(3):
                    newPos[i] = currB.pos[i] + magDir[i]
                currB = Bone(newPos, currB.dir, 2/(factor+1))
            elif char == 'f':
                # move forward but do not draw line
                magDir = [d*length for d in currB.dir]
                newPos = [0,0,0]
                for i in range(3):
                    newPos[i] = currB.pos[i] + magDir[i]
                currB = Bone(newPos, currB.dir, 2/(factor+1))
            elif char == '+':
                # rotate direction positively
                currB.dir = np.matmul(self.rotateY(angle), currB.dir)
            elif char == '-':
                # rotate direction negatively
                currB.dir = np.matmul(self.rotateY(-angle), currB.dir)
            elif char == '&':
                # pitch down
                currB.dir = np.matmul(self.rotateZ(angle), currB.dir)
            elif char == '^':
                # pitch up
                currB.dir = np.matmul(self.rotateZ(-angle), currB.dir)
            elif char == '\\':
                # roll left
                currB.dir = np.matmul(self.rotateX(-angle), currB.dir)
            elif char == '/':
                # roll right
                currB.dir = np.matmul(self.rotateX(angle), currB.dir)
            elif char == '|':
                # turn around 180
                currB.dir = np.matmul(self.rotateY(180), currB.dir)
            elif char == '[':
                # push curr_loc to stack
                if factor+1 > 5:
                    factor = 5
                else:
                    factor += 1
                stack.append(currB)
            elif char == ']':
                # set curr_loc to popped stack
                if factor-1 < 0:
                    factor = 0
                else:
                    factor -= 1
                currB = stack.pop()
        return bone

class Bone:
    def __init__(self, pos=[0,0,0], dir=[0,1,0], factor=1):
        self.pos = pos
        self.dir = np.array(dir)
        self.factor = factor

if __name__ == "__main__":
    axiom = "F"
    angle = 22.5
    rules = {
        "F": "FF/[/F\F\F]\[^F/F/F]"
        # "F": "F+[-^F][+&F]F"
    }
    length = .1

    lsysbuilder = Lsystem()
    lsysbuilder.custom(axiom, angle, rules, length)
    lsysString = lsysbuilder.build_string(depth=1)
    lsysPoints = lsysbuilder.construct_points(lsysString)
    print(lsysString)
    for b in lsysPoints:
        print(b.pos, end="          ")
        print(b.factor)

    a = np.array([[1,2,3], [4,5,6], [7,8,9]])
    mat = lsysbuilder.rotateY(radians(angle))
    b = np.array([0,1,0])
    print(np.matmul(mat,b))