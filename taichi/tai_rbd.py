import taichi as ti
import numpy as np
from taichi.lang.ops import length
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

# axiom = "F"
# angle = 22.5
# rules = {
#     "F": "FF+[+F-F-F]-[-F+F+F]"
# }

# axiom = "Y"
# angle = 25.7
# rules = {
#     "X": "X[-FFF][+FFF]FX",
#     "Y": "YFX[+Y][-Y]"
# }

axiom = "X"
angle = 20
rules = {
    "F": "FF",
    "X": "F[+X]F[-X]+X"
}

lsysbuilder = lsys.Lsystem()
# lsysbuilder.custom(axiom, angle, rules)
lsysPoints = lsysbuilder.construct_points(lsysbuilder.build_string(depth=3))

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
        size = [.02/(y1*4+1), .02/(y1*4+1)]
        degree = points[i][2]
        yrun = sin(radians(degree))
        xrun = cos(radians(degree))
        x2=points[i][0]+xrun*.05
        y2=points[i][1]+yrun*.05
        dist = sqrt((x2-x1)**2 + (y2-y1)**2)
        steps = .01
        for k in decimal_range(0, dist, steps):
            lc = [x1+k*xrun+offset, y1+k*yrun]
            mpm.add_cube(lower_corner=lc, cube_size=size, material=MPMSolver.material_elastic, sample_density=8)

print("Building lsys")
mpm.add_cube(lower_corner=[0,0], cube_size=[1,1], material=MPMSolver.material_water, color=0x111111, sample_density=8)
build_lsys(lsysPoints)

for frame in range(500):
    mpm.step(8e-3)
    colors = np.array([0x068587, 0xED553B, 0xEEEEF0, 0xFFFF00],
                      dtype=np.uint32)
    particles = mpm.particle_info()
    gui.circles(particles['position'],
                radius=3,
                color=colors[particles['material']])
    # gui.rect(topleft=[1,1], bottomright=[.5,.5])
    gui.show(f'{frame:06d}.png' if write_to_disk else None)