#-*- coding: utf8 -*-
from FGAme.backends.pygame_be import PyGameListener, PyGameScreen, Screen
import pygame
import pygame.gfxdraw
from math import trunc

class PyGameGFXScreen(PyGameScreen):
    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    def draw_circle(self, pos, radius, color=(0, 0, 0), solid=True):
        x, y = self._map_point(pos)
        pygame.gfxdraw.aacircle(self._screen, x, y, trunc(radius), color)
        if solid:
            pygame.gfxdraw.filled_circle(self._screen, x, y, trunc(radius), color)

    def draw_poly(self, points, color=(0, 0, 0), solid=True):
        points = [ self._map_point(pt) for pt in points ]
        pygame.gfxdraw.aapolygon(self._screen, points, color)
        if solid:
            pygame.gfxdraw.filled_polygon(self._screen, points, color)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        Screen.draw_rect(self, pos, shape, color, solid)

    def clear(self, color=None):
        color = color or self.background
        self._screen.fill(color)

del PyGameScreen

def init():
    pygame.init()



