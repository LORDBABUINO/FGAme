# -*- coding: utf8 -*-
from __future__ import absolute_import
if __name__ == '__main__':
    __package__ = 'FGAme.objects'; import FGAme.objects

from .base import LinearObject
from ..mathutils import Vector2D
from ..collision import get_collision, get_collision_aabb

class AABB(LinearObject):
    '''Define um objeto físico que responde a colisões como uma caixa de 
    contorno alinhada aos eixos.
    
    Deve ser inicializada ou por uma tupla com os valores (xmin, xmax, ymin, ymax)
    ou por definido shape=(ladox, ladoy), preferencialmente definindo uma posição
    para o centro de massa pos_cm.
    '''
    def __init__(self, bbox=None, pos_cm=Vector2D(0, 0), shape=None, **kwds):
        if bbox:
            self.xmin, self.xmax, self.ymin, self.ymax = bbox
            if 'pos_cm' in kwds:
                raise TypeError('cannot set bbox and pos_cm simultaneously')
            x = (self.xmin + self.xmax) / 2.
            y = (self.ymin + self.ymax) / 2.
            self.pos_cm = Vector2D(x, y)
        elif shape:
            self.pos_cm = pos_cm
            dx, dy = shape
            x, y = pos_cm
            self.xmin, self.xmax = x - dx / 2., x + dx / 2.
            self.ymin, self.ymax = y - dy / 2., y + dy / 2.
        else:
            raise TypeError('either shape or bbox must be defined')

        super(AABB, self).__init__(**kwds)

    def __repr__(self):
        tname = type(self).__name__
        vel_cm = ', '.join('%.2f' % x for x in self.vel_cm)
        data = ', '.join('%.2f' % x for x in self.bounds)
        return '%s(%s, vel_cm=(%s))' % (tname, data, vel_cm)

    def draw(self, screen):
        self.draw_aabb(screen, color=self.color, fill=True)

    @property
    def inertia(self):
        a = self.xmax - self.xmin
        b = self.ymax - self.ymin
        return self.mass / 12. * (a ** 2 + b ** 2)

#===============================================================================
# Implementa colisões
#===============================================================================
get_collision[AABB, AABB] = get_collision_aabb


if __name__ == '__main__':
    from FGAme import World, Runner

    C1 = AABB(shape=(40, 40), vel_cm=(0, 20))
    C2 = AABB(shape=(60, 60), pos_cm=(30, 40))
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
