import taichi as ti
import numpy as np
import lsys
from math import sqrt, isclose, sin, cos, radians
from utils import *
from engine.mpm_solver import MPMSolver

write_to_disk = False

ti.init(arch=ti.cuda)  # Try to run on GPU

gui = ti.GUI("Taichi Elements", res=512, background_color=0x112F41)

mpm = MPMSolver(res=(128, 128), unbounded=False)

mpm.add_surface_collider(point=(0, 0.1),
                         normal=(0, 1),
                         surface=mpm.surface_sticky)

# axiom = "F"
# angle = 22.5
# rules = {
#     "F": "FF+[+F-F-F]-[-F+F+F]"
# }

axiom = "Y"
angle = 25.7
rules = {
    "X": "X[-FFF][+FFF]FX",
    "Y": "YFX[+Y][-Y]"
}

axiom = "X"
angle = 20
rules = {
    "F": "FF",
    "X": "F[+X]F[-X]+X"
}

lsysbuilder = lsys.Lsystem()
lsysbuilder.custom(axiom, angle, rules)
lsysPoints = lsysbuilder.construct_points(lsysbuilder.build_string(depth=3))

def decimal_range(start, stop, increment):
    while start < stop and not isclose(start, stop):
        yield start
        start += increment

def build_lsys(points):
    offset = .5
    for i in range(len(points)):
        factor = points[i][3]
        size = [.02*factor,.02*factor]
        x1=points[i][0]
        y1=points[i][1]
        # size = [.02/(y1*4+1), .02/(y1*4+1)]
        degree = points[i][2]
        yrun = sin(radians(degree))
        xrun = cos(radians(degree))
        x2=points[i][0]+xrun*.05
        y2=points[i][1]+yrun*.05
        dist = sqrt((x2-x1)**2 + (y2-y1)**2)
        steps = .01
        for k in decimal_range(0, dist, steps):
            lc = [x1+k*xrun+offset, y1+k*yrun]
            mpm.add_cube(lower_corner=lc, cube_size=size, material=MPMSolver.material_elastic, sample_density=32*factor, color=0xA52A2A)

print("Building lsys")
# mpm.add_cube(lower_corner=[0,0], cube_size=[1,1], material=MPMSolver.material_water, color=0x111111, sample_density=8)
build_lsys(lsysPoints)

for frame in range(20000):
    mouse = gui.get_cursor_pos()
    if gui.get_event(ti.GUI.PRESS):
        if gui.event.key in [ti.GUI.ESCAPE, ti.GUI.EXIT]: break
        elif gui.event.key == 'f':
            mpm.add_ellipsoid(center=[mouse[0], mouse[1]],
                    radius=[0.025, 0.01],
                    material=MPMSolver.material_elastic,
                    sample_density=8,
                    velocity=[5, .2],
                    color=0x068587)
    if gui.event is not None: mpm.set_gravity((0, -9.8)) # if had any event
    if gui.is_pressed(ti.GUI.LEFT,  'a'): mpm.set_gravity((-2, 0))
    if gui.is_pressed(ti.GUI.RIGHT, 'd'): mpm.set_gravity((2, 0))
    if gui.is_pressed(ti.GUI.UP,    'w'): mpm.set_gravity((0, 2))
    if gui.is_pressed(ti.GUI.DOWN,  's'): mpm.set_gravity((0, -2))
    mpm.step(8e-3)
    colors = np.array([0x068587, 0xED553B, 0xEEEEF0, 0xFFFF00],
                      dtype=np.uint32)
    particles = mpm.particle_info()
    gui.circles(particles['position'],
                radius=1.5,
                color=particles['color'])
    gui.show(f'{frame:06d}.png' if write_to_disk else None)