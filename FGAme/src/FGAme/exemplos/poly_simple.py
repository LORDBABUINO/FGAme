#-*- coding: utf8 -*-
from __future__ import print_function

from FGAme import *

world = World()

A = Poly.regular(N=3, length=130, color='red',
                 pos_cm=(-200, 0), vel_cm=(200, 0),
                 name='A', omega_cm=0.6)
B = Poly.regular(N=5, length=100, theta_cm=pi / 4,
                 pos_cm=(200, 0), vel_cm=(-100, -40),
                 name='B')

world.add([A, B])

@world.listen('key-down', 'space')
def pause_toggle(key):
    pass


world.run()
