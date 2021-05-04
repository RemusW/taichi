 
import taichi as ti
import numpy as np
import lsys
from math import sqrt, isclose, sin, cos, radians
import utils
from engine.mpm_solver import MPMSolver

write_to_disk = False

ti.init(arch=ti.cuda)  # Try to run on GPU

gui = ti.GUI("Taichi Elements", res=1440, background_color=0x112F41)

mpm = MPMSolver(res=(128, 128), unbounded=False)

# mpm.add_ellipsoid(center=[0.4, 0.4],
#                   radius=[0.3, 0.3],
#                   material=MPMSolver.material_elastic,
#                   sample_density=2*4)

mpm.add_surface_collider(point=(0, 0.1),
                         normal=(0, 1),
                         surface=mpm.surface_sticky)

# lsys = [(0,0, 0,.1), (0,.1, .1,.2), (0,.1, -.1,.2)]

axiom = "F"
angle = 22.5
lsysPoints = lsys.construct_points(lsys.build_string(axiom, angle, 3))

def decimal_range(start, stop, increment):
    while start < stop and not isclose(start, stop):
        yield start
        start += increment

def build_lsys(points):
    offset = .5
    for i in range(len(points)):
        size = [.01,.01]
        x1=points[i][0]
        y1=points[i][1]
        degree = points[i][2]
        yrun = sin(radians(degree))
        xrun = cos(radians(degree))
        x2=points[i][0]+xrun*.05
        y2=points[i][1]+yrun*.05
        dist = sqrt((x2-x1)**2 + (y2-y1)**2)
        if(xrun != 0):
            slope = yrun/xrun
        else:
            slope = 0
        steps = .01
        for k in decimal_range(0, dist, steps):
            lc = [x1+k*xrun+offset, y1+k*yrun]
            # print(f'{i} {k:.2f} {dist:.2f} {yrun} {lc}')
            mpm.add_cube(lower_corner=lc, cube_size=size, material=MPMSolver.material_elastic, sample_density=16)

build_lsys(lsysPoints)

# mpm.add_cube(lower_corner=[.5,0], cube_size=[.1,.1], material=MPMSolver.material_elastic, color=0x111111, sample_density=16)

# lc = [.45,0]
# size = [.01,.01]
# for i in range (50):
#     mpm.add_cube(lower_corner=lc, cube_size=size, material=MPMSolver.material_elastic, sample_density=16)
#     lc[0] += .001
#     lc[1] += .01
    # size[0] -= .01
    # size[1] -= .01
# mpm.add_cube(lower_corner=[0,0], cube_size=[.1,.1], material=MPMSolver.material_elastic, sample_density=2*4)
# mpm.add_cube(lower_corner=[.05,.05], cube_size=[.1,.1], material=MPMSolver.material_sand, sample_density=1)

for frame in range(500):
    mpm.step(8e-3)
    colors = np.array([0x068587, 0xED553B, 0xEEEEF0, 0xFFFF00],
                      dtype=np.uint32)
    particles = mpm.particle_info()
    gui.circles(particles['position'],
                radius=1.5,
                color=colors[particles['material']])
    # gui.rect(topleft=[1,1], bottomright=[.5,.5])
    gui.show(f'{frame:06d}.png' if write_to_disk else None)