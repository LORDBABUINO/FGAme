#-*- coding: utf8 -*-
'''
Este exemplo ilustra a simulação de um gás de caixas alinhadas aos eixos
'''
from FGAme import *
from random import uniform, choice

# Constantes da simulação
SPEED = 300
SHAPE = (30, 30)
NUM_ABBS = 50

# Inicializa o mundo
world = World(gravity=50, dfriction=0)
world.make_bounds(-390, 390, -290, 290, delta=400)

# Preenche o mundo
for _ in range(NUM_ABBS):
    pos = Vector(uniform(-370, 370), uniform(-270, 270))
    vel = Vector(uniform(-SPEED, SPEED), uniform(-SPEED, SPEED))
    aabb = AABB(shape=SHAPE, vel_cm=vel, pos_cm=pos, color=(200, 0, 0))
    world.add(aabb)

# Inicia a simulação
world.run()
