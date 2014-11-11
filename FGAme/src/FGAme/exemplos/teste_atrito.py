# -*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
print('Starting simulation...')

# Inicializa o mundo
world = World(dfriction=0.1)
world.make_bounds(-390, 390, -290, 290, delta=400)
runner = Runner(world)

SPEED = 200
A = AABB(pos_cm=(0, -200), shape=(50, 50), color='black')
B = AABB(pos_cm=(-150, 200), shape=(50, 50), vel_cm=(SPEED, -2 * SPEED), color='red')
world.add_object(A)
world.add_object(B)

# Inicia a simulação
runner.run()
