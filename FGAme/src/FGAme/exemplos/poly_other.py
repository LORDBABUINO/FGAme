# -*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice

print('Starting simulation...')

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

world = World()
runner = Runner(world)

# Triangulo 1
obj1 = Poly.regular(N=4, length=130, pos_cm=(-300, -200), vel_cm=(100, 100),
                    omega_cm=2.1, color=random_color())
obj1.mass = 100
world.add_object(obj1)

# Triangulo 2
obj2 = Poly.regular(N=4, length=50, pos_cm=(200, 200), vel_cm=(-100, -100),
                    omega_cm=-uniform(0, 4), color=random_color())
obj2.mass = 100
world.add_object(obj2)

# AABB
aabb = AABB(bbox=(-100, 400, -300, -200), mass=100, color='black')
# aabb = Poly.rect(bbox=(-100, 400, -300, -200), mass=100, color='black')
aabb.is_dynamic_linear = False
# aabb.is_dynamic_angular = False
world.add_object(aabb)

aabb2 = AABB(bbox=(300, 380, -150, 280), mass=100, color='black')
aabb2.is_dynamic_linear = False
# aabb2.is_dynamic_angular = False
world.add_object(aabb2)


# Triangulo 2
obj3 = Poly.regular(N=5, length=150, pos_cm=(-300, 200), vel_cm=(-100, -100),
                   omega_cm=-uniform(0, 4), color=random_color())
obj3.mass = 100
obj3.is_dynamic_angular = obj3.is_dynamic_linear = False
world.add_object(obj3)

def pause():
    obj1.pause()
    obj2.pause()

def unpause():
    obj1.unpause()
    obj2.unpause()

runner.register_key_down('<down>', pause)
runner.register_key_down('<up>', unpause)

# Inicia a simulação
runner.run()
