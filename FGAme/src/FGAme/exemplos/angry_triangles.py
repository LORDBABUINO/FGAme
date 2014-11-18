#-*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice
from math import sqrt
set_backend('pygamegfx')

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

class Scenario:
    def floor(self):
        floor = AABB(bbox=(-10000, 10000, -300, -150), color=(68, 170, 0))
        floor.make_static()
        floor.pause()
        return floor

    def pole(self):
        pole = AABB(bbox=(-350, -340, -150, -50), color=(158, 86, 38))
        pole.make_static()
        return pole

    def boxes(self):
        height = 80
        width = 200
        pos = Vector(250, -110)
        shape = (width, height)
        p = Poly.rect(pos_cm=pos, shape=shape, color=(158, 86, 38), centered=True)
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
            yield Poly.rect(pos_cm=pos, shape=shape, color=(158, 86, 38), centered=True)

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
tri.inertia *= 10
tri.move((-345, -50 + L))
tri.boost((150, 150))
tri.aboost(-5)
# tri.is_dynamic_angular = False

# Inicializa o mundo
world = World(background=(0, 204, 255), gravity=80, dfriction=0.3, rest_coeff=0.5)
for obj in scene.get_objects():
    world.add(obj)
world.add(tri)

# Inicia a simulação
world.run()
