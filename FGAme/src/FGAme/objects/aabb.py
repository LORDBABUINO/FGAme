#-*- coding: utf8 -*-
from __future__ import absolute_import
if __name__ == '__main__':
    __package__ = 'FGAme.objects'; import FGAme.objects

from .base import LinearObject
from ..mathutils import Vector
from ..collision import get_collision, get_collision_aabb
from ..utils import lazy

class AABB(LinearObject):
    '''Define um objeto físico que responde a colisões como uma caixa de 
    contorno alinhada aos eixos.
    
    Deve ser inicializada ou por uma tupla com os valores (xmin, xmax, ymin, ymax)
    ou por definido shape=(ladox, ladoy), preferencialmente definindo uma posição
    para o centro de massa pos_cm.
    '''
    def __init__(self, bbox=None, pos_cm=None, shape=None, **kwds):
        if bbox:
            self._xmin, self._xmax, self._ymin, self._ymax = map(float, bbox)
            if pos_cm is not None:
                raise TypeError('cannot set bbox and pos_cm simultaneously')
            x = (self._xmin + self._xmax) / 2.
            y = (self._ymin + self._ymax) / 2.
            pos_cm = Vector(x, y)
        elif shape:
            pos_cm = pos_cm or (0, 0)
            dx, dy = map(float, shape)
            x, y = pos_cm
            self._xmin, self._xmax = x - dx / 2., x + dx / 2.
            self._ymin, self._ymax = y - dy / 2., y + dy / 2.
        else:
            raise TypeError('either shape or bbox must be defined')

        super(AABB, self).__init__(pos_cm=pos_cm, **kwds)

    def __repr__(self):
        tname = type(self).__name__
        vel_cm = ', '.join('%.2f' % x for x in self.vel_cm)
        data = ', '.join('%.2f' % x for x in self.bbox)
        return '%s(bbox=[%s], vel_cm=(%s))' % (tname, data, vel_cm)

    def draw(self, screen):
        self.draw_aabb(screen, color=self.color, fill=True)

    #===========================================================================
    # Torna as os limites da AABB modificáveis
    #===========================================================================
    @property
    def xmin(self): return self._xmin

    @xmin.setter
    def xmin(self, value):
        self._xmin = float(value)
        self._pos_cm.x = (self._xmax - self._xmin) / 2

    @property
    def xmax(self): return self._xmax

    @xmax.setter
    def xmax(self, value):
        self._xmax = float(value)
        self._pos_cm.x = (self._xmax - self._xmin) / 2

    @property
    def ymin(self): return self._ymin

    @ymin.setter
    def ymin(self, value):
        self._ymin = float(value)
        self._pos_cm.y = (self._ymax - self._ymin) / 2

    @property
    def ymax(self): return self._ymax

    @ymax.setter
    def ymax(self, value):
        self._ymax = float(value)
        self._pos_cm.y = (self._ymax - self._ymin) / 2


#===============================================================================
# Implementa colisões
#===============================================================================
get_collision[AABB, AABB] = get_collision_aabb
