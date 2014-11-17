#-*- coding: utf8 -*-
from __future__ import absolute_import
if __name__ == '__main__':
    __package__ = 'FGAme.objects'; import FGAme.objects

from math import trunc, pi
from .base import Object
from ..mathutils import Vector
from ..collision import get_collision, Collision
from ..utils import lazy

class Circle(Object):
    '''Define um círculo e implementa a detecção de colisão comparando a 
    distância entre os centros com a soma dos raios.'''

    def __init__(self, radius, *args, **kwds):
        self._radius = float(radius)
        super(Circle, self).__init__(*args, **kwds)
        self.radius = self._radius  # recalcula a AABB de acordo com o raio

    def __repr__(self):
        tname = type(self).__name__
        vel_cm = ', '.join('%.1f' % x for x in self.vel_cm)
        pos_cm = ', '.join('%.1f' % x for x in self.pos_cm)
        return '%s(pos_cm=(%s), vel_cm=(%s), radius=%.1f)' % (tname, pos_cm, vel_cm, self.radius)

    def draw(self, screen):
        '''Desenha objeto na tela'''

        screen.draw_circle(self.pos_cm, self.radius, color=self.color)

    @lazy
    def area(self):
        return pi * self._radius ** 2

    @lazy
    def ROG_sqr(self):
        return self._radius ** 2 / 2

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

        # Atualiza a caixa de contorno
        x, y = self._pos_cm
        self._xmin = x - value
        self._xmax = x + value
        self._ymin = y - value
        self._ymax = y + value

    def scale(self, scale, update_physics=False):
        self.radius *= scale
        if update_physics:
            self.mass *= scale ** 2
            self.inertia *= scale ** 2

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
    from doctest import testmod
    testmod()
