axiom = "F"
angle = 22.5

def build_lsys(axiom, depth):
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
    return lsys_string
