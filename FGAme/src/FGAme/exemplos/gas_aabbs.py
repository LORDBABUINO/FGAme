# -*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice

print('Starting simulation...')

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

# Inicializa o mundo
world = World(gravity=50, dfriction=0)
world.make_bounds(-390, 390, -290, 290, delta=400)
runner = Runner(world)

# aabbs
SPEED = 600
SHAPE = (50, 50)
SIZE = 20
for _ in range(SIZE):
    pos = Vector2D(uniform(-370, 370), uniform(-270, 270))
    vel = Vector2D(uniform(-SPEED, SPEED), uniform(-SPEED, SPEED))
    bola = AABB(shape=SHAPE, vel_cm=vel, pos_cm=pos, color=random_color(), mass=1)
    world.add_object(bola)

# Inicia a simulação
runner.run()
