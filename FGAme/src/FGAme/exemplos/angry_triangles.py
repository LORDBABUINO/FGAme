# -*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice
from math import sqrt

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

class Scenario:
    def floor(self):
        floor = Poly.rect(bbox=(-10000, 10000, -300, -150), color=(68, 170, 0))
        floor.is_dynamic_linear = False
        floor.is_dynamic_angular = False
        return floor

    def pole(self):
        pole = AABB(bbox=(-350, -340, -150, -50), color=(158, 86, 38))
        pole.is_dynamic_linear = False
        return pole

    def boxes(self):
        height = 80
        width = 200
        pos = Vector2D(250, -110)
        shape = (width, height)
        p = Poly.rect(pos_cm=pos, shape=shape, color=(158, 86, 38))
        p.is_dynamic = False
        yield p

        for _ in range(4):
            shapeX, shapeY = shape
            height *= 0.75
            width *= 2. / 3
            deltay = shapeY / 2. + height / 2.
            deltax = uniform(-shapeX / 6., shapeX / 6.)
            pos = pos + (deltax, deltay)
            shape = (width, height)
            yield Poly.rect(pos_cm=pos, shape=shape, color=(158, 86, 38))

    def get_objects(self):
        yield self.floor()
        yield self.pole()
        for box in self.boxes():
            yield box


# Inicializa o cenário
scene = Scenario()

# Cria triângulo
L = 40
h = 10 * sqrt(12)
tri = Poly.regular(3, L, color=(200, 0, 0))
print(tri.inertia)
# tri.inertia *= 100
tri.move((-345, -50 + L))
tri.linear_boost((150, 150))
tri.angular_boost(-5)
# tri.is_dynamic_angular = False

# Inicializa o mundo
world = World(background=(0, 204, 255), gravity=80, dfriction=0.01)
runner = Runner(world)
for obj in scene.get_objects():
    world.add_object(obj)
world.add_object(tri)

# Inicia a simulação
runner.run()
