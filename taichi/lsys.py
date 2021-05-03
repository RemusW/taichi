from math import sin, cos, radians

axiom = "F"
angle = 22.5

def build_string(axiom, angle, depth):
    count = depth
    lsys_string = axiom
    while count > 0:
        chars = lsys_string.split()
        temp = "";
        for char in chars:
            if char == 'F':
                temp = temp + "F F + [ + F - F - F ] - [ - F + F + F ] "
            else:
                temp = temp + char + " "
        lsys_string = temp
        count = count - 1
    return lsys_string[:-1]


def construct_points(lsys):
    chars = lsys.split()
    length = .05
    stack = []
    bone = []
    curr = (0,0,90)
    for char in chars:
        if char == 'F':
            # push (curr_loc, changed_loc) to list of lines
            bone.append(curr)
            yrun = sin(radians(curr[2]))
            xrun = cos(radians(curr[2]))

            curr = (curr[0]+xrun*length, curr[1]+yrun*length, curr[2])
        elif char == '+':
            # rotate direction positively
            if curr[2] + angle < 360:
                curr = (curr[0], curr[1], curr[2] + angle)
            else:
                curr = (curr[0], curr[1], curr[2] + angle - 360)
        elif char == '-':
            # rotate direction negatively
            if curr[2] - angle >= 0:
                curr = (curr[0], curr[1], curr[2] - angle)
            else:
                curr = (curr[0], curr[1], curr[2] - angle + 360)
        elif char == '[':
            # push curr_loc to stack
            stack.append(curr)
        elif char == ']':
            # set curr_loc to popped stack
            curr = stack.pop()
    return bone
    
axiom = "F"
lsys = build_string(axiom, angle, 1)
print(construct_points(lsys))