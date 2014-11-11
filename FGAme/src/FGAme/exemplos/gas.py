# -*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice

print('Starting simulation...')

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

# Inicializa o mundo
world = World(gravity=50, dfriction=0.0)
world.make_bounds(-390, 390, -290, 800, delta=400)
runner = Runner(world)

# Bola
SPEED = 200
RADIUS = 10
SIZE = 70
for _ in range(SIZE):
    pos = Vector2D(uniform(-380, 380), uniform(-290, 100))
    vel = Vector2D(uniform(-SPEED, SPEED), uniform(-SPEED, SPEED))
    bola = Circle(radius=RADIUS, vel_cm=vel, pos_cm=pos, color=random_color(), mass=1)
    world.add_object(bola)

# Êmbolo
class Embolo(AABB):
    def external_force(self, t):
        return -100 * self.vel_cm

embolo = Embolo(bbox=(-379.9, 379.9, 120, 170), color=random_color(), mass=50)
world.add_object(embolo)

def mass_up():
    embolo.mass *= 1.1

def mass_down():
    embolo.mass /= 1.1

runner.register_key_down('<up>', mass_up)
runner.register_key_down('<down>', mass_down)

# Inicia a simulação
runner.run()
