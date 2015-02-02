#-*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *
from random import uniform, choice

print('Starting simulation...')

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))

world = World()
world.adamping = 0.1

obj1 = Poly.regular(N=4, length=130, pos_cm=(-300, -200), vel_cm=(100, 100),
                    omega_cm=3.1, color=random_color())
obj1.mass = 100
world.add(obj1)


obj2 = Poly.regular(N=4, length=50, pos_cm=(200, 200), vel_cm=(-100, -100),
                    omega_cm=-uniform(0, 4), color=random_color())
obj2.mass = 100
world.add(obj2)

# AABB
aabb = AABB(bbox=(-100, 400, -300, -200), mass=100, color='black')
aabb.make_static()
world.add(aabb)

aabb2 = AABB(bbox=(300, 380, -150, 280), mass=100, color='black')
aabb2.make_static()
world.add(aabb2)


obj3 = Poly.regular(N=5, length=150, pos_cm=(-300, 200), color=random_color())
world.add(obj3)
obj3.make_static()

@world.listen('key-down', 'down')
def pause():
    print('pre-vel', obj1.vel_cm)
    obj1.make_static()
    obj2.make_static()


@world.listen('key-down', 'up')
def unpause():
    obj1.make_dynamic()
    obj2.make_dynamic()

# Inicia a simulação
world.run()
