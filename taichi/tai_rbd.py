 
import taichi as ti
import numpy as np
import utils
from engine.mpm_solver import MPMSolver

write_to_disk = False

ti.init(arch=ti.cuda)  # Try to run on GPU

gui = ti.GUI("Taichi Elements", res=1024, background_color=0x112F41)

mpm = MPMSolver(res=(128, 128))

mpm.add_ellipsoid(center=[0.4, 0.4],
                  radius=[0.3, 0.3],
                  material=MPMSolver.material_elastic,
                  sample_density=2*4)

mpm.add_cube(lower_corner=[0,0], cube_size=[.1,.1], material=MPMSolver.material_elastic, sample_density=2*4)
# mpm.add_cube(lower_corner=[.05,.05], cube_size=[.1,.1], material=MPMSolver.material_sand, sample_density=1)

for frame in range(500):
    mpm.step(8e-3)
    colors = np.array([0x068587, 0xED553B, 0xEEEEF0, 0xFFFF00],
                      dtype=np.uint32)
    particles = mpm.particle_info()
    gui.circles(particles['position'],
                radius=1.5,
                color=colors[particles['material']])
    gui.rect(topleft=[1,1], bottomright=[.5,.5])
    gui.show(f'{frame:06d}.png' if write_to_disk else None)