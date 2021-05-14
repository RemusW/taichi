import taichi as ti
import numpy as np
from lsys_3D import Lsystem
from math import sqrt, isclose, sin, cos, radians
import utils
from engine.mpm_solver import MPMSolver

write_to_disk = False

ti.init(arch=ti.cuda)  # Try to run on GPU

gravity = ti.Vector.field(2, dtype=float, shape=())
attractor_strength = ti.field(dtype=float, shape=())
attractor_pos = ti.Vector.field(2, dtype=float, shape=())

gui = ti.GUI("Taichi Elements", res=512, background_color=0x112F41)

mpm = MPMSolver(res=(64, 64, 64), size=1)

mpm.add_surface_collider(point=(0, 0.1, 0),
                         normal=(0, 1, 0),
                         surface=mpm.surface_sticky)

# axiom = "F"
# angle = 22.5
# rules = {
#     "F": "FF+[+F-F-F]-[-F+F+F]"
#     # "F": "F+[-^F][+&F]F"
# }

axiom = "Y"
angle = 25.7
rules = {
    "X": "X[-FFF][+FFF]FX",
    "Y": "YFX[+Y][-Y]"
}

# axiom = "X"
# angle = 20
# rules = {
#     "F": "FF",
#     "X": "F[+X]F[-X]+X"
# }

# axiom = "FFA"
# angle = 20
# rules = {
#     "A": "+[B]&&&[B]&&&B",
#     "B": "+FA"
# }

length = .05
size = .03

lsysbuilder = Lsystem()
lsysbuilder.custom(axiom, angle, rules, length)
lsysString = lsysbuilder.build_string(depth=3)
lsysPoints = lsysbuilder.construct_points(lsysString)

def decimal_range(start, stop, increment):
    while start < stop and not isclose(start, stop):
        yield start
        start += increment

def build_lsys(points):
    offset = .5 - length/2
    for i in range(len(points)):
        pos = points[i].pos
        dir = points[i].dir
        factor = points[i].factor
        volume = [size*factor,size*factor,size*factor]
        steps = .01
        count = 0
        for k in decimal_range(0, length, steps):
            lc = [pos[0]+k*dir[0]+offset, pos[1]+k*dir[1], pos[2]+k*dir[2]+.45]
            mpm.add_cube(lower_corner=lc,
                cube_size= volume,
                material=MPMSolver.material_elastic,
                sample_density=16*factor, color=0xA52A2A)
            # Add fruits onto branches
            if count%6 == 0:
                horizon = [0,0,0]
                for i in range(3):
                    if dir[i] > 0:
                        horizon[i] = 1
                    else:
                        horizon[i] = -1
                horizon[1] = 0
                dot = horizon[0]*dir[0] + horizon[2]*dir[2]
                if dot > .6:
                    lc[1]-=.04
                    mpm.add_ellipsoid(center=lc,
                        radius=[0.01, .02, .01],
                        material=MPMSolver.material_snow,
                        sample_density=16)
            count+=1
print("Building lsys")
# mpm.add_cube(lower_corner=[0,.1,0], cube_size=[.95,1,.95], material=MPMSolver.material_water, color=0x068587, sample_density=1)
build_lsys(lsysPoints)

for frame in range(20000):
    mouse = gui.get_cursor_pos()
    if gui.get_event(ti.GUI.PRESS):
        if gui.event.key in [ti.GUI.ESCAPE, ti.GUI.EXIT]: break
        elif gui.event.key == 'f':
            mpm.add_ellipsoid(center=[mouse[0]+.5, mouse[1], 0],
                    radius=[0.05, 0.025, .025],
                    material=MPMSolver.material_elastic,
                    sample_density=8,
                    velocity=[0, .2, 10],
                    color=0x068587)
    if gui.event is not None: mpm.set_gravity((0, -9.8, 0)) # if had any event
    if gui.is_pressed(ti.GUI.LEFT,  'a'): mpm.set_gravity((-2, 0, 0))
    if gui.is_pressed(ti.GUI.RIGHT, 'd'): mpm.set_gravity((2, 0, 0))
    if gui.is_pressed(ti.GUI.UP,    'w'): mpm.set_gravity((0, 2, 0))
    if gui.is_pressed(ti.GUI.DOWN,  's'): mpm.set_gravity((0, -2, 0))
    if gui.is_pressed(ti.GUI.DOWN,  'e'): mpm.set_gravity((0, 0, 2))
    if gui.is_pressed(ti.GUI.DOWN,  'q'): mpm.set_gravity((0, 0, -2))

    mpm.step(4e-3)
    particles = mpm.particle_info()
    np_x = particles['position'] / 1.0

    # simple camera transform
    screen_x = ((np_x[:, 0] + np_x[:, 2]) / 2**0.5) - 0.2
    screen_y = (np_x[:, 1])

    screen_pos = np.stack([screen_x, screen_y], axis=-1)

    colors = np.array([0x068587, 0xED553B, 0xEEEEF0, 0xFFFF00],
                      dtype=np.uint32)
    gui.circles(screen_pos, radius=1.1, color=particles['color'])
    gui.show(f'{frame:06d}.png' if write_to_disk else None)