# -*- coding: utf8 -*-
from __future__ import absolute_import
if __name__ == '__main__':
    __package__ = 'FGAme.objects'; import FGAme.objects

import pygame
from math import trunc
from .base import LinearObject
from ..mathutils import Vector2D
from ..collision import get_collision, Collision

class Circle(LinearObject):
    '''Define um círculo e implementa a detecção de colisão comparando a 
    distância entre os centros com a soma dos raios.'''

    def __init__(self, radius, pos_cm=Vector2D(0, 0), **kwds):
        x, y = self.pos_cm = pos_cm
        self.radius = float(radius)
        super(Circle, self).__init__(**kwds)

    def __repr__(self):
        tname = type(self).__name__
        vel_cm = ', '.join('%.1f' % x for x in self.vel_cm)
        pos_cm = ', '.join('%.1f' % x for x in self.pos_cm)
        return '%s(pos_cm=(%s), vel_cm=(%s), radius=%.1f)' % (tname, pos_cm, vel_cm, self.radius)

    def draw(self, screen):
        '''Desenha objeto na tela'''

        screen.draw_circle(self.pos_cm, self.radius, color=self.color)

    @property
    def area(self):
        return pi * self.radius ** 2

    @property
    def inertia(self):
        try:
            return self._inertia
        except AttributeError:
            self._inertia = self.mass * self.radius ** 2 / 2
            return self._inertia

    @inertia.setter
    def inertia(self, value):
        self._inertia = value

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

        # Atualiza a caixa de contorno
        x, y = self.pos_cm
        self.xmin = x - value
        self.xmax = x + value
        self.ymin = y - value
        self.ymax = y + value

    def scale(self, scale, update_physics=False):
        self.radius *= scale
        if update_physics:
            self.mass /= scale ** 2
            self.intertia /= scale ** 2

    def adjust_superposition(self, other, dt):
        if not isinstance(other, Circle):
            return NotImplemented

        delta = other.pos_cm - self.pos_cm
        u = delta.normalized()
        D = self.radius + other.radius - delta.norm()
        self.move(-D / 2 * u)
        other.move(D / 2 * u)

#===============================================================================
# Implementa colisões
#===============================================================================
@get_collision.dispatch(Circle, Circle)
def circle_collision(A, B):
    '''Testa a colisão pela distância dos centros'''

    delta = B.pos_cm - A.pos_cm
    if delta.norm() < A.radius + B.radius:
        n = delta.normalized()
        D = A.radius + B.radius - delta.norm()
        pos = A.pos_cm + (A.radius - D / 2) * n
        return Collision(A, B, pos=pos, n=n)
    else:
        return None


if __name__ == '__main__':
    from FGAme import World, Runner

    C1 = Circle(radius=20, vel_cm=(0, 100))
    C2 = Circle(radius=35, pos_cm=(30, 40))
    col = get_collision(C1, C2)
    print(col)
    print(col.get_impulse())
    print(col.normal)
    print(col.objects)
    print(col.pos)

    world = World()
    world.add_object(C1)
    world.add_object(C2)
    runner = Runner(world)
    runner.run()
