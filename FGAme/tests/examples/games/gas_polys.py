#-*- coding: utf8 -*-
'''
Semelhante ao gas_aabbs.py, mas desta vez utiliza objetos da classe Poly.
'''
from FGAme import *
from random import uniform, choice

# Constantes da simulação
SPEED = 300
SHAPE = (30, 30)
NUM_POLYS = 100

# Inicializa o mundo
world = World(gravity=50, dfriction=0)
world.make_bounds(10, 790, 10, 590, delta=400)

# Preenche o mundo
for _ in range(NUM_POLYS):
    pos = Vector(uniform(30, 770), uniform(30, 570))
    vel = Vector(uniform(-SPEED, SPEED), uniform(-SPEED, SPEED))
    obj = Poly.rect(shape=SHAPE, vel_cm=vel, pos_cm=pos, color=(200, 0, 0))
    obj.inertia *= 10
    world.add(obj)

# Inicia a simulação
world.run(timeout=3)
