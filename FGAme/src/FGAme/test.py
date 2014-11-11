#-*- coding: utf8 -*-
from __future__ import print_function

from engine import *
from random import uniform

def random_color():
    return tuple(int(uniform(0, 255)) for i in range(3))
        
# Inicializa as partículas    
world = World(rest_coeff=1)
world.make_bounds(70, 730, 70, 530, delta=60) 
for i in range(150):
    V = 300
    S = (30, 50)
    xmin, ymin = uniform(100, 700), uniform(100, 500)
    vel = (uniform(-V, V), uniform(-V, V))
    c = Circle(radius=uniform(5, 10), vel_cm=vel, pos_cm=(xmin, ymin), color=random_color(), mass=1)
    world.add_object(c)
    
    xmin, ymin = uniform(100, 700), uniform(100, 500)
    deltax, deltay = uniform(*S), uniform(*S)
    xmax, ymax = xmin + deltax, ymin + deltay
    c = AABB(vel_cm=vel, bbox=(xmin, xmax, ymin, ymax), color=random_color(), mass=1)
    #world.add_object(c)
    
S = (30, 50)
V = 300
vel = (uniform(-V, V), uniform(-V, V))
xmin, ymin = uniform(100, 700), uniform(100, 500)
xmax, ymax = xmin + 70, ymin + 120
#c = Circle(radius=40, vel_cm=vel, pos_cm=(xmin, ymin), mass=20)
#world.add_object(c)
dt = 1./60

if __name__ == '__main__':
    app = Runner(world)
    app.run()
