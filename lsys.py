from math import sin, cos, radians

class Lsystem:

    def __init__(self):
        self.axiom = "F"
        self.angle = 22.5
        self.length = .05
        self.rules = {
            "F": "FF+[+F-F-F]-[-F+F+F]"
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
        return lsys_string[:-1]


    def construct_points(self, lsys):
        # chars = lsys.split()
        chars = [lsys[i:i+1] for i in range(0, len(lsys), 1)]
        angle = self.angle
        length = self.length
        stack = []
        bone = []
        factor = 1
        curr = (0,0,90, 1)
        for char in chars:
            if char == 'F':
                # push (curr_loc, changed_loc) to list of lines
                bone.append(curr)
                yrun = sin(radians(curr[2]))
                xrun = cos(radians(curr[2]))
                curr = (curr[0]+xrun*length, curr[1]+yrun*length, curr[2], 1/factor)
            elif char == '+':
                # rotate direction positively
                if curr[2] + angle < 360:
                    curr = (curr[0], curr[1], curr[2] + angle, curr[3])
                else:
                    curr = (curr[0], curr[1], curr[2] + angle - 360, curr[3])
            elif char == '-':
                # rotate direction negatively
                if curr[2] - angle >= 0:
                    curr = (curr[0], curr[1], curr[2] - angle, curr[3])
                else:
                    curr = (curr[0], curr[1], curr[2] - angle + 360, curr[3])
            elif char == '[':
                # push curr_loc to stack
                if factor+1 > 5:
                    factor = 5
                else:
                    factor += 1
                stack.append(curr)
            elif char == ']':
                # set curr_loc to popped stack
                if factor-1 < 0:
                    factor = 0
                else:
                    factor -= 1
                curr = stack.pop()
        return bone