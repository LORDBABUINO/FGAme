#-*- coding: utf8 -*-
from mathutils import Vector
from math import trunc

class Screen(object):
    '''Backend para as funções de desenhar na tela do computador'''

    def __init__(self, width, height, pos=(0, 0), zoom=1, background=(255, 255, 255)):
        self.width = width
        self.height = height
        self.pos = Vector(*pos)
        self.zoom = zoom
        self.background = background

    @property
    def shape(self):
        return self.width, self.height

    #===========================================================================
    # Drawing functions
    #===========================================================================
    def draw_circle(self, pos, radius, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def draw_poly(self, L_points, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def draw_aabb(self, xmin, xmax, ymin, ymax, color=(0, 0, 0), solid=True):
        dx, dy = xmax - xmin, ymax - ymin
        self.draw_rect((xmin, ymin), (dx, dy), color=color, solid=solid)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        x, y = pos
        w, h = shape
        self.draw_poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], color, solid)

    def draw_line(self, pt1, pt2, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def clear(self, color=None):
        raise NotImplementedError

    #===========================================================================
    # Other API functions
    #===========================================================================
    def init(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def _map_point(self, point):
        return point
