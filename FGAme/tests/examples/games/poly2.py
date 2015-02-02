#-*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice
from math_tests import pi
print('Starting simulation...')

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

world = World()

obj1 = Poly.regular(N=3, length=130, pos_cm=(-200, 0), vel_cm=(300, 0), color=random_color(), omega_cm=2.2)
world.add(obj1)

obj2 = Poly.regular(N=5, length=100, pos_cm=(-200, 150), theta_cm=pi / 4,
                    color=random_color())
world.add(obj2)

obj3 = Poly.regular(N=3, length=100, pos_cm=(200, 0), theta_cm=pi / 4,
                    color=random_color())
world.add(obj3)
obj3.is_dynamic_linear = obj3.is_dynamic_angular = False

world.make_bounds(-390, 390, -290, 290, use_poly=True)

def pause():
    obj1.pause()
    obj2.pause()

def unpause():
    obj1.unpause()
    obj2.unpause()

# Inicia a simulação
world.run()
