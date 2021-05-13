import taichi as ti
import numpy as np
from taichi.lang.ops import length
from lsys_3D import Lsystem
from math import sqrt, isclose, sin, cos, radians
import utils
from engine.mpm_solver import MPMSolver

write_to_disk = False

ti.init(arch=ti.cuda)  # Try to run on GPU

gui = ti.GUI("Taichi Elements", res=512, background_color=0x112F41)

mpm = MPMSolver(res=(64, 64, 64), size=1)
mpm.set_gravity((0, -1, 0))

# mpm.add_ellipsoid(center=[0.4, 0.4],
#                   radius=[0.3, 0.3],
#                   material=MPMSolver.material_elastic,
#                   sample_density=2*4)

mpm.add_surface_collider(point=(0, 0.1, 0),
                         normal=(0, 1, 0),
                         surface=mpm.surface_sticky)

axiom = "F"
angle = 22.5
rules = {
    "F": "FF+[+F-F-F]-[-F+F+F]"
    # "F": "F+[-^F][+&F]F"
}

# axiom = "Y"
# angle = 25.7
# rules = {
#     "X": "X[-FFF][+FFF]FX",
#     "Y": "YFX[+Y][-Y]"
# }

# axiom = "X"
# angle = 20
# rules = {
#     "F": "FF",
#     "X": "F[+X]F[-X]+X"
# }

length = .1
lsysbuilder = Lsystem()
lsysbuilder.custom(axiom, angle, rules, length)
lsysString = lsysbuilder.build_string(depth=2)
lsysPoints = lsysbuilder.construct_points(lsysString)

def decimal_range(start, stop, increment):
    while start < stop and not isclose(start, stop):
        yield start
        start += increment

def build_lsys(points):
    offset = .5 - length/2
    size = [.02,.02,.02]
    for i in range(len(points)):
        pos = points[i].pos
        dir = points[i].dir
        steps = .01
        for k in decimal_range(0, length, steps):
            lc = [pos[0]+k*dir[0]+offset, pos[1]+k*dir[1], pos[2]+k*dir[2]+.45]
            mpm.add_cube(lower_corner=lc, cube_size=size, material=MPMSolver.material_elastic, sample_density=8)

print("Building lsys")
# mpm.add_cube(lower_corner=[0,0], cube_size=[1,1], material=MPMSolver.material_water, color=0x111111, sample_density=8)
build_lsys(lsysPoints)

# mpm.add_cube((0, 1, 0.35), (0.5, 0.1, 0.5),
#                 mpm.material_water,
#                 color=0x8888FF, sample_density=2)
for frame in range(500):
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