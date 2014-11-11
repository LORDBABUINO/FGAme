# -*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice
from math import pi
print('Starting simulation...')

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

world = World()
runner = Runner(world)

obj1 = Poly.regular(N=3, length=130, pos_cm=(-200, 0), vel_cm=(100, 0), color=random_color(), omega_cm=0.0)
world.add_object(obj1)

obj2 = Poly.regular(N=5, length=100, pos_cm=(200, 0), theta_cm=pi / 4,
                    color=random_color())
world.add_object(obj2)

def pause(col=None):
    obj1.pause()
    obj2.pause()

def unpause():
    obj1.unpause()
    obj2.unpause()

def col_cb(col):
    A, B = col.objects
    A.add_point(col.pos - A.pos_cm)
    B.add_point(col.pos - B.pos_cm)

world.register_collision_callback(col_cb)
runner.register_key_down('<down>', pause)
runner.register_key_down('<up>', unpause)

# Inicia a simulação
runner.run()
